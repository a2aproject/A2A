"""Master orchestrator — central brain of the mesh network."""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field

import httpx

from mesh.agent.base import LLMClient
from mesh.network.registry import AgentRegistry
from mesh.network.models import NodeInfo
from mesh.orchestrator.intent import (
    ApprovalDecision,
    ApprovalPolicy,
    ApprovalStatus,
    Intent,
    IntentQueue,
    RiskLevel,
)
from mesh.orchestrator.router import TaskRouter

logger = logging.getLogger(__name__)

DECOMPOSITION_PROMPT = """You are a task orchestrator. Given a user request and a list of available agents with their skills, decompose the task into subtasks and assign each to the best agent.

Return a JSON object with this structure:
{
  "plan": [
    {
      "step": 1,
      "description": "What needs to be done",
      "agent_skill": "skill_tag to match",
      "depends_on": []
    }
  ]
}

Only use skills that are available. If a task requires multiple steps, order them with dependencies."""

INTENT_REVIEW_PROMPT = """You are a safety reviewer. Review the following agent intent and decide if it should be approved.

Consider:
- Does the action make sense for the task?
- Are the files/commands reasonable?
- Is the risk level appropriate?
- Could this cause harm or data loss?

Respond with exactly one word: APPROVE or REJECT
If rejecting, add a brief reason on the next line."""


@dataclass
class TaskStep:
    """A single step in a decomposed task plan."""

    step: int
    description: str
    agent_skill: str
    depends_on: list[int] = field(default_factory=list)
    agent: NodeInfo | None = None
    result: str | None = None
    status: str = "pending"  # pending, running, completed, failed


@dataclass
class TaskPlan:
    """A decomposed task plan."""

    plan_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    original_request: str = ""
    steps: list[TaskStep] = field(default_factory=list)
    status: str = "planning"  # planning, executing, completed, failed


class MasterOrchestrator:
    """Central brain of the mesh network.

    Decomposes user requests into subtasks, routes them to agents,
    reviews intents, and monitors progress.
    """

    def __init__(
        self,
        llm: LLMClient,
        registry: AgentRegistry,
        policy: ApprovalPolicy | None = None,
    ):
        self.llm = llm
        self.registry = registry
        self.router = TaskRouter(registry)
        self.policy = policy or ApprovalPolicy()
        self.intent_queue = IntentQueue()
        self.active_plans: dict[str, TaskPlan] = {}

    async def handle_user_request(self, message: str) -> TaskPlan:
        """Process a user request: decompose, assign, and start execution.

        Args:
            message: The user's natural language request.

        Returns:
            A TaskPlan with assigned steps.
        """
        logger.info(f"Orchestrator: Processing request: {message[:100]}")

        # Decompose task using LLM
        plan = await self._decompose_task(message)
        plan.original_request = message
        self.active_plans[plan.plan_id] = plan

        # Assign agents to each step
        for step in plan.steps:
            assignment = self.router.route(
                task_description=step.description,
                required_skills=[step.agent_skill],
            )
            if assignment:
                step.agent = assignment.agent
            else:
                logger.warning(f"No agent for step {step.step}: {step.description}")

        plan.status = "executing"
        return plan

    async def _decompose_task(self, message: str) -> TaskPlan:
        """Use LLM to break a task into subtasks."""
        agents = self.registry.get_all_agents()
        agent_summary = "\n".join(
            f"- {a.name}: skills={a.skill_tags}" for a in agents
        )

        prompt = f"""Available agents:
{agent_summary}

User request: {message}"""

        response = await self.llm.chat([
            {"role": "system", "content": DECOMPOSITION_PROMPT},
            {"role": "user", "content": prompt},
        ])

        text = response.choices[0].message.content or "{}"

        try:
            # Extract JSON from response
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(text[start:end])
            else:
                data = {"plan": [{"step": 1, "description": message, "agent_skill": "general", "depends_on": []}]}

            steps = [
                TaskStep(
                    step=s.get("step", i + 1),
                    description=s.get("description", ""),
                    agent_skill=s.get("agent_skill", ""),
                    depends_on=s.get("depends_on", []),
                )
                for i, s in enumerate(data.get("plan", []))
            ]
        except json.JSONDecodeError:
            # Fallback: single step
            steps = [TaskStep(step=1, description=message, agent_skill="general")]

        return TaskPlan(steps=steps)

    async def review_intent(self, intent: Intent) -> ApprovalDecision:
        """Review an agent's declared intent based on approval policy.

        Returns:
            ApprovalDecision (may block if human approval needed).
        """
        path = self.policy.evaluate(intent)

        if path == "auto":
            decision = ApprovalDecision(
                intent_id=intent.intent_id,
                status=ApprovalStatus.APPROVED,
                approved_by="policy",
                reason="Auto-approved by policy",
            )
            logger.info(f"Intent {intent.intent_id} auto-approved")
            return decision

        if path == "master_llm":
            return await self._llm_review(intent)

        # Human approval needed — submit to queue (blocks until decided)
        return await self.intent_queue.submit(intent)

    async def _llm_review(self, intent: Intent) -> ApprovalDecision:
        """Have master LLM review an intent."""
        response = await self.llm.chat([
            {"role": "system", "content": INTENT_REVIEW_PROMPT},
            {"role": "user", "content": json.dumps(intent.to_dict(), indent=2)},
        ])

        text = (response.choices[0].message.content or "").strip()
        approved = text.upper().startswith("APPROVE")
        reason = text.split("\n", 1)[1].strip() if "\n" in text else ""

        decision = ApprovalDecision(
            intent_id=intent.intent_id,
            status=ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED,
            approved_by="master_llm",
            reason=reason,
        )

        logger.info(
            f"Intent {intent.intent_id} {'approved' if approved else 'rejected'} "
            f"by master LLM: {reason}"
        )
        return decision

    async def dispatch_to_agent(self, step: TaskStep) -> str | None:
        """Send a task to a specific agent via A2A protocol."""
        if not step.agent:
            return None

        agent_url = step.agent.url or f"http://{step.agent.host}:{step.agent.port}"

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                # Send via A2A JSON-RPC
                payload = {
                    "jsonrpc": "2.0",
                    "method": "message/send",
                    "id": str(uuid.uuid4()),
                    "params": {
                        "message": {
                            "role": "user",
                            "messageId": str(uuid.uuid4()),
                            "parts": [{"text": step.description}],
                        }
                    },
                }

                resp = await client.post(
                    agent_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                data = resp.json()
                step.status = "completed"
                step.result = json.dumps(data.get("result", {}))
                return step.result

        except Exception as e:
            logger.error(f"Failed to dispatch to {step.agent.name}: {e}")
            step.status = "failed"
            step.result = str(e)
            return None

    async def execute_plan(self, plan: TaskPlan) -> TaskPlan:
        """Execute all steps in a plan, respecting dependencies."""
        import asyncio

        completed_steps: set[int] = set()

        while True:
            # Find steps ready to run
            ready = [
                step
                for step in plan.steps
                if step.status == "pending"
                and all(d in completed_steps for d in step.depends_on)
            ]

            if not ready:
                break

            # Execute ready steps in parallel
            tasks = [self.dispatch_to_agent(step) for step in ready]
            for step in ready:
                step.status = "running"

            await asyncio.gather(*tasks, return_exceptions=True)

            for step in ready:
                if step.status == "completed":
                    completed_steps.add(step.step)

        # Check if all completed
        all_done = all(s.status == "completed" for s in plan.steps)
        plan.status = "completed" if all_done else "failed"

        return plan
