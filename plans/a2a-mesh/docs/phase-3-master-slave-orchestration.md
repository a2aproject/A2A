# Phase 3: Master-Slave Orchestration & Agent Autonomy

## Goal

The master node acts as the brain of the network — it decomposes tasks, routes them to the right agents, reviews agent intentions before execution, and monitors progress. Agents operate autonomously after the master (or human via UI) approves their plan.

## Deliverables

1. `mesh/orchestrator/master.py` — Master orchestrator agent
2. `mesh/orchestrator/slave.py` — Slave-side intent reporting and execution
3. `mesh/orchestrator/intent.py` — Intent declaration, review, and approval system
4. `mesh/orchestrator/router.py` — Skill-based task routing
5. `mesh/orchestrator/autonomy.py` — Autonomous execution engine with guardrails
6. `mesh/orchestrator/workflow.py` — Multi-agent workflow chains

## Core Concept: Intent Review

Before an agent takes any significant action, it must declare its **intent** to the master:

```
┌─────────┐    1. Task      ┌────────┐    2. Intent    ┌────────┐
│  User   │ ──────────────► │ Master │ ◄────────────── │ Slave  │
│  (UI)   │                 │        │ ───────────────► │        │
└─────────┘                 │        │    3. Approve    │        │
     ▲                      │        │                  │        │
     │     5. Result        │        │ ◄────────────── │        │
     └───────────────────── │        │    4. Execute    │        │
                            └────────┘    & Report      └────────┘
```

### Intent Declaration Format

```json
{
  "intent_id": "intent-abc123",
  "agent_id": "coder-agent",
  "task_id": "task-xyz789",
  "action": "write_code",
  "description": "I will create a Python module `parser.py` with a CSV parsing function that handles quoted fields and custom delimiters.",
  "details": {
    "files_to_create": ["src/parser.py"],
    "files_to_modify": [],
    "files_to_read": ["src/models.py"],
    "estimated_complexity": "medium",
    "tools_needed": ["write_file", "read_file"]
  },
  "risk_level": "low",     // low, medium, high, critical
  "requires_approval": true
}
```

### Approval Policies

```yaml
# In master.yaml
orchestrator:
  approval_policy:
    # Auto-approve low-risk actions
    auto_approve:
      risk_levels: ["low"]
      actions: ["research", "summarize", "analyze", "read_file"]

    # Require human approval for these
    require_human:
      risk_levels: ["high", "critical"]
      actions: ["execute_command", "deploy", "delete_file"]

    # Master LLM can auto-approve these (no human needed)
    master_approve:
      risk_levels: ["medium"]
      actions: ["write_file", "write_code", "refactor"]

  # Timeout: auto-reject if no approval within N seconds
  approval_timeout: 300
```

## Detailed Implementation

### Master Orchestrator (`mesh/orchestrator/master.py`)

```python
class MasterOrchestrator:
    """Central brain of the mesh network."""

    def __init__(self, config, registry, llm_client):
        self.config = config
        self.registry = registry          # Agent registry
        self.llm = llm_client             # Master's own LLM for reasoning
        self.intent_queue = IntentQueue() # Pending intents
        self.workflows = {}               # Active workflows

    async def handle_user_request(self, message: str) -> str:
        """Process a user request from the UI."""
        # 1. Use master LLM to decompose task
        plan = await self.decompose_task(message)
        # 2. Route subtasks to agents
        assignments = await self.assign_tasks(plan)
        # 3. Dispatch and monitor
        return await self.dispatch_workflow(assignments)

    async def decompose_task(self, message: str) -> TaskPlan:
        """Use LLM to break task into subtasks with agent assignments."""
        prompt = f"""Given these available agents and their skills:
        {self.registry.get_agent_summaries()}

        Decompose this task into subtasks and assign each to the best agent:
        Task: {message}

        Return a JSON plan with ordered steps."""
        return await self.llm.chat([
            {"role": "system", "content": DECOMPOSITION_PROMPT},
            {"role": "user", "content": prompt}
        ])

    async def assign_tasks(self, plan: TaskPlan) -> list[Assignment]:
        """Match each subtask to the best available agent."""
        assignments = []
        for step in plan.steps:
            agent = await self.registry.find_best_agent(
                skill_tags=step.required_skills,
                prefer_idle=True
            )
            assignments.append(Assignment(
                step=step,
                agent=agent,
                order=step.order,
                depends_on=step.dependencies
            ))
        return assignments

    async def review_intent(self, intent: Intent) -> ApprovalDecision:
        """Review an agent's declared intent."""
        policy = self.config.approval_policy

        # Check auto-approve rules
        if intent.risk_level in policy.auto_approve.risk_levels:
            return ApprovalDecision(approved=True, by="policy")

        # Check if master LLM can approve
        if intent.risk_level in policy.master_approve.risk_levels:
            decision = await self._llm_review(intent)
            return ApprovalDecision(approved=decision, by="master_llm")

        # Queue for human approval (via UI)
        await self.intent_queue.add(intent)
        return ApprovalDecision(approved=None, by="pending_human")

    async def _llm_review(self, intent: Intent) -> bool:
        """Have master LLM review an intent for safety."""
        response = await self.llm.chat([
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user", "content": f"Review this intent:\n{intent.to_json()}"}
        ])
        return "APPROVE" in response.upper()
```

### Slave Intent Reporter (`mesh/orchestrator/slave.py`)

```python
class SlaveAgent:
    """Wraps agent execution with intent reporting."""

    def __init__(self, agent_executor, master_url):
        self.executor = agent_executor
        self.master_url = master_url

    async def execute_with_intent(self, task):
        """Execute task with intent review loop."""
        # 1. Analyze task and declare intent
        intent = await self.plan_intent(task)

        # 2. Submit intent to master
        decision = await self.submit_intent(intent)

        # 3. Wait for approval if pending
        if decision.status == "pending":
            decision = await self.wait_for_approval(intent.intent_id)

        # 4. Execute if approved
        if decision.approved:
            result = await self.executor.execute(task)
            await self.report_result(task.id, result)
            return result
        else:
            await self.report_rejection(task.id, decision.reason)
            return None

    async def plan_intent(self, task) -> Intent:
        """Use local LLM to plan what actions are needed."""
        # Ask LLM to describe its plan before executing
        response = await self.llm.chat([
            {"role": "system", "content": INTENT_PLANNING_PROMPT},
            {"role": "user", "content": f"Task: {task.description}\nDescribe your plan."}
        ])
        return Intent.from_llm_response(response)
```

### Task Router (`mesh/orchestrator/router.py`)

```python
class TaskRouter:
    """Routes tasks to the best agent based on skills and availability."""

    def __init__(self, registry):
        self.registry = registry

    async def route(self, task_description: str, required_skills: list[str]) -> AgentInfo:
        """Find the best agent for a task."""
        candidates = []

        for skill in required_skills:
            agents = await self.registry.find_agents_by_skill(skill)
            candidates.extend(agents)

        if not candidates:
            raise NoAgentAvailable(f"No agent found for skills: {required_skills}")

        # Score candidates
        scored = []
        for agent in candidates:
            score = self._score_agent(agent, required_skills)
            scored.append((score, agent))

        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[0][1]

    def _score_agent(self, agent, required_skills) -> float:
        """Score agent suitability (0-1)."""
        skill_match = len(set(agent.skill_tags) & set(required_skills)) / len(required_skills)
        load_score = 1.0 - (agent.active_tasks / agent.max_tasks)
        return (skill_match * 0.7) + (load_score * 0.3)
```

### Workflow Engine (`mesh/orchestrator/workflow.py`)

Supports sequential and parallel multi-agent workflows:

```python
class Workflow:
    """Multi-agent workflow with dependencies."""

    def __init__(self, name: str, steps: list[WorkflowStep]):
        self.name = name
        self.steps = steps
        self.results = {}

    async def execute(self, orchestrator):
        """Execute workflow steps respecting dependencies."""
        pending = list(self.steps)

        while pending:
            # Find steps whose dependencies are satisfied
            ready = [s for s in pending if self._deps_met(s)]

            if not ready:
                raise WorkflowDeadlock("No steps can proceed")

            # Execute ready steps in parallel
            tasks = [orchestrator.dispatch_to_agent(step) for step in ready]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for step, result in zip(ready, results):
                self.results[step.id] = result
                pending.remove(step)

    def _deps_met(self, step) -> bool:
        return all(dep in self.results for dep in step.depends_on)
```

**Example Workflow Definition:**
```yaml
workflow:
  name: "feature-implementation"
  steps:
    - id: research
      agent_skill: "research"
      prompt: "Research best practices for {topic}"
      depends_on: []
    - id: implement
      agent_skill: "write_code"
      prompt: "Implement based on research: {research.result}"
      depends_on: [research]
    - id: review
      agent_skill: "code_review"
      prompt: "Review this implementation: {implement.result}"
      depends_on: [implement]
    - id: fix
      agent_skill: "write_code"
      prompt: "Fix issues found in review: {review.result}"
      depends_on: [review]
      condition: "review.has_issues"
```

## Autonomy Levels

| Level | Name | Behavior |
|-------|------|----------|
| 0 | Manual | Every action requires human approval |
| 1 | Supervised | Master LLM approves medium risk, human approves high risk |
| 2 | Autonomous | Master LLM approves all except critical, human approves critical |
| 3 | Full Auto | All actions auto-approved (use with caution) |

Configurable per-agent and per-skill:
```yaml
orchestrator:
  default_autonomy: 1
  agent_overrides:
    coder-agent:
      autonomy: 2
      except_actions: ["deploy", "delete"]
```

## Testing Plan

1. **Task decomposition**: User message → multi-step plan
2. **Intent review**: Auto-approve, LLM-approve, and human-approve paths
3. **Task routing**: Correct agent selected based on skills
4. **Workflow execution**: Sequential and parallel steps with dependencies
5. **Rejection handling**: Agent handles rejected intents gracefully
6. **Timeout handling**: Pending approvals timeout correctly

## Success Criteria

- [ ] User sends task via UI → master decomposes into subtasks automatically
- [ ] Subtasks route to correct agents based on skills
- [ ] Agents declare intent before taking action
- [ ] Intent review respects approval policies
- [ ] Agents execute autonomously after approval
- [ ] Multi-step workflows with dependencies work correctly
- [ ] Human can override/redirect any task in progress
