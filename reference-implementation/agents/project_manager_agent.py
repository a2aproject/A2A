"""
Project Manager Agent - Intelligent task routing and agent coordination
"""
import sys
sys.path.append('..')

from typing import List, Dict, Any, Optional, Tuple
from core.a2a_base import (
    BaseAgent, Message, Task, TaskStatus, Artifact,
    TextPart, DataPart, AgentSkill, MessageRole, AgentRegistry
)
import json
from datetime import datetime


class ProjectManagerAgent(BaseAgent):
    """
    Intelligent project manager that analyzes tasks and routes them to
    the most appropriate specialized agent. Coordinates multi-agent workflows.
    """

    def __init__(self, agent_registry: AgentRegistry):
        super().__init__(
            name="Project Manager Agent",
            description="Intelligent task router and agent coordinator for optimal task-agent matching",
            version="1.0.0"
        )

        self.registry = agent_registry

        # Register skills
        self.add_skill(AgentSkill(
            id="task_routing",
            name="Task Routing",
            description="Analyze tasks and route to the most appropriate specialized agent",
            tags=["routing", "coordination", "task-management"],
            examples=[
                "Route data loading task to dataset agent",
                "Find best agent for research query",
                "Assign task to appropriate specialist"
            ]
        ))

        self.add_skill(AgentSkill(
            id="workflow_coordination",
            name="Workflow Coordination",
            description="Coordinate multi-agent workflows and manage dependencies",
            tags=["workflow", "coordination", "orchestration"],
            examples=[
                "Coordinate research and data loading",
                "Manage complex multi-step tasks",
                "Orchestrate agent collaboration"
            ]
        ))

        self.add_skill(AgentSkill(
            id="agent_selection",
            name="Agent Selection",
            description="Select optimal agent based on capabilities and task requirements",
            tags=["selection", "matching", "optimization"],
            examples=[
                "Find agent for dataset analysis",
                "Choose best researcher for topic"
            ]
        ))

        # Routing history for learning
        self.routing_history: List[Dict[str, Any]] = []

    def _analyze_task_requirements(self, message_text: str) -> Dict[str, Any]:
        """
        Analyze task to determine requirements and suitable agent types.
        Uses keyword matching and pattern recognition.
        """
        text_lower = message_text.lower()

        analysis = {
            "task": message_text,
            "keywords": [],
            "required_skills": [],
            "complexity": "medium",
            "priority": "normal",
            "agent_preferences": []
        }

        # Dataset-related keywords
        dataset_keywords = ["dataset", "load", "data", "glue", "huggingface", "csv", "json", "etl"]
        if any(keyword in text_lower for keyword in dataset_keywords):
            analysis["required_skills"].append("load_dataset")
            analysis["agent_preferences"].append("Dataset Ingestion Agent")
            analysis["keywords"].extend([k for k in dataset_keywords if k in text_lower])

        # Research-related keywords
        research_keywords = ["research", "analyze", "analysis", "review", "study", "investigate",
                             "examine", "synthesize", "hypothesis"]
        if any(keyword in text_lower for keyword in research_keywords):
            analysis["required_skills"].append("deep_analysis")
            analysis["agent_preferences"].append("Deep Researcher Agent")
            analysis["keywords"].extend([k for k in research_keywords if k in text_lower])

        # Grant writing keywords
        grant_keywords = ["grant", "nih", "proposal", "nsf", "funding", "application",
                         "specific aims", "biosketch", "budget", "r01", "pdf format", "page limit"]
        if any(keyword in text_lower for keyword in grant_keywords):
            analysis["required_skills"].append("format_validation")
            analysis["agent_preferences"].append("Grant Writing Genius Agent")
            analysis["keywords"].extend([k for k in grant_keywords if k in text_lower])

        # VPN and networking keywords
        vpn_keywords = ["vpn", "outline", "shadowsocks", "proxy", "circumvent", "bypass",
                       "socks5", "network", "censorship", "tunnel", "sdk integration"]
        if any(keyword in text_lower for keyword in vpn_keywords):
            analysis["required_skills"].append("outline_setup")
            analysis["agent_preferences"].append("VPN Setup Agent")
            analysis["keywords"].extend([k for k in vpn_keywords if k in text_lower])

        # Bloom/LLM evaluation keywords
        bloom_keywords = ["bloom", "evaluation", "behavior", "llm", "sycophancy", "bias",
                         "judgment", "transcript", "seed.yaml", "ideation", "rollout"]
        if any(keyword in text_lower for keyword in bloom_keywords):
            analysis["required_skills"].append("evaluation_design")
            analysis["agent_preferences"].append("Bloom Agent")
            analysis["keywords"].extend([k for k in bloom_keywords if k in text_lower])

        # Determine complexity
        if any(word in text_lower for word in ["complex", "comprehensive", "deep", "detailed"]):
            analysis["complexity"] = "high"
        elif any(word in text_lower for word in ["simple", "quick", "basic"]):
            analysis["complexity"] = "low"

        # Determine priority
        if any(word in text_lower for word in ["urgent", "asap", "immediately", "critical"]):
            analysis["priority"] = "high"
        elif any(word in text_lower for word in ["later", "whenever", "low priority"]):
            analysis["priority"] = "low"

        return analysis

    def _score_agent_fit(self, agent: BaseAgent, task_analysis: Dict[str, Any]) -> float:
        """
        Calculate how well an agent fits the task requirements.
        Returns a score between 0.0 and 1.0.
        """
        score = 0.0

        # Check if agent is in preferences
        if agent.name in task_analysis["agent_preferences"]:
            score += 0.5

        # Check skill overlap
        agent_skill_ids = [skill.id for skill in agent.skills]
        required_skills = task_analysis["required_skills"]

        if required_skills:
            skill_match_ratio = len(set(agent_skill_ids) & set(required_skills)) / len(required_skills)
            score += skill_match_ratio * 0.3

        # Check keyword relevance in agent description
        agent_text = (agent.name + " " + agent.description).lower()
        keyword_matches = sum(1 for keyword in task_analysis["keywords"] if keyword in agent_text)

        if task_analysis["keywords"]:
            keyword_match_ratio = keyword_matches / len(task_analysis["keywords"])
            score += keyword_match_ratio * 0.2

        return min(1.0, score)

    def select_agent(self, task_analysis: Dict[str, Any]) -> Tuple[Optional[BaseAgent], float]:
        """
        Select the best agent for the task based on analysis.
        Returns (agent, confidence_score) tuple.
        """
        # Get all available agents (excluding self)
        available_agents = [
            agent for agent in self.registry.agents.values()
            if agent.name != self.name
        ]

        if not available_agents:
            return None, 0.0

        # Score each agent
        agent_scores = [
            (agent, self._score_agent_fit(agent, task_analysis))
            for agent in available_agents
        ]

        # Sort by score (descending)
        agent_scores.sort(key=lambda x: x[1], reverse=True)

        # Get best agent
        best_agent, best_score = agent_scores[0]

        # Log routing decision
        self.routing_history.append({
            "timestamp": datetime.now().isoformat(),
            "task": task_analysis["task"],
            "selected_agent": best_agent.name,
            "confidence": best_score,
            "alternatives": [
                {"agent": agent.name, "score": score}
                for agent, score in agent_scores[1:3]  # Top 3 alternatives
            ]
        })

        return best_agent, best_score

    async def route_task(self, messages: List[Message]) -> Dict[str, Any]:
        """
        Analyze messages and route to appropriate agent.
        Returns routing decision and delegation info.
        """
        # Get the last user message
        user_messages = [msg for msg in messages if msg.role == MessageRole.USER]
        if not user_messages:
            return {
                "status": "error",
                "error": "No user message found"
            }

        last_message = user_messages[-1]
        text_parts = [part for part in last_message.parts if isinstance(part, TextPart)]

        if not text_parts:
            return {
                "status": "error",
                "error": "No text content in message"
            }

        message_text = text_parts[0].text

        # Analyze task
        task_analysis = self._analyze_task_requirements(message_text)

        # Select agent
        selected_agent, confidence = self.select_agent(task_analysis)

        if not selected_agent:
            return {
                "status": "error",
                "error": "No suitable agent found",
                "task_analysis": task_analysis
            }

        return {
            "status": "success",
            "selected_agent": selected_agent.name,
            "confidence": confidence,
            "task_analysis": task_analysis,
            "agent": selected_agent
        }

    async def process_message(self, messages: List[Message]) -> Task:
        """Process task routing requests"""
        task = self.create_task(messages)
        self.update_task_status(task.id, TaskStatus.WORKING)

        try:
            # Route the task
            routing_result = await self.route_task(messages)

            if routing_result["status"] == "error":
                raise ValueError(routing_result["error"])

            # Delegate to selected agent
            selected_agent = routing_result["agent"]
            delegated_task = await selected_agent.process_message(messages)

            # Create response artifact
            response_text = self._format_routing_response(routing_result, delegated_task)

            artifact = Artifact(
                name="Task Routing and Execution",
                description=f"Task routed to {selected_agent.name}",
                parts=[
                    TextPart(text=response_text),
                    DataPart(data={
                        "routing": routing_result,
                        "execution": {
                            "agent": selected_agent.name,
                            "task_id": delegated_task.id,
                            "status": delegated_task.status.value
                        }
                    })
                ]
            )

            # Add artifacts from delegated task
            for delegated_artifact in delegated_task.artifacts:
                self.add_artifact(task.id, delegated_artifact)

            self.add_artifact(task.id, artifact)
            self.update_task_status(task.id, TaskStatus.COMPLETED)

        except Exception as e:
            self.update_task_status(task.id, TaskStatus.FAILED, error=str(e))

        return self.get_task(task.id)

    def _format_routing_response(self, routing_result: Dict[str, Any],
                                 delegated_task: Task) -> str:
        """Format routing decision and results"""
        response = f"""📋 Project Manager - Task Routing Report

🎯 Task Analysis:
  Complexity: {routing_result['task_analysis']['complexity'].upper()}
  Priority: {routing_result['task_analysis']['priority'].upper()}
  Required Skills: {', '.join(routing_result['task_analysis']['required_skills']) or 'General'}

🤖 Agent Selection:
  Selected Agent: {routing_result['selected_agent']}
  Confidence: {routing_result['confidence']:.1%}

✓ Task Delegated Successfully
  Task ID: {delegated_task.id}
  Status: {delegated_task.status.value}
  Artifacts Generated: {len(delegated_task.artifacts)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Execution Results:
"""
        return response

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get statistics about routing decisions"""
        if not self.routing_history:
            return {"total_routings": 0}

        agent_counts = {}
        total_confidence = 0.0

        for routing in self.routing_history:
            agent_name = routing["selected_agent"]
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
            total_confidence += routing["confidence"]

        return {
            "total_routings": len(self.routing_history),
            "average_confidence": total_confidence / len(self.routing_history),
            "agent_distribution": agent_counts,
            "most_used_agent": max(agent_counts.items(), key=lambda x: x[1])[0] if agent_counts else None
        }
