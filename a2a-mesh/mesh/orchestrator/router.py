"""Skill-based task routing — find the best agent for a task."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from mesh.network.registry import AgentRegistry
from mesh.network.models import NodeInfo

logger = logging.getLogger(__name__)


@dataclass
class Assignment:
    """A task assigned to a specific agent."""

    agent: NodeInfo
    task_description: str
    required_skills: list[str]
    score: float = 0.0


class TaskRouter:
    """Routes tasks to the best available agent based on skill matching."""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry

    def route(
        self,
        task_description: str,
        required_skills: list[str],
        prefer_idle: bool = True,
    ) -> Assignment | None:
        """Find the best agent for a task.

        Args:
            task_description: What needs to be done.
            required_skills: Skill tags needed (e.g., ["code", "python"]).
            prefer_idle: Prefer agents with fewer active tasks.

        Returns:
            Assignment with best agent, or None if no agent found.
        """
        candidates: list[tuple[float, NodeInfo]] = []

        for agent in self.registry.get_all_agents():
            if not agent.healthy:
                continue

            score = self._score_agent(agent, required_skills)
            if score > 0:
                candidates.append((score, agent))

        if not candidates:
            logger.warning(f"No agent found for skills: {required_skills}")
            return None

        candidates.sort(key=lambda x: x[0], reverse=True)
        best_score, best_agent = candidates[0]

        logger.info(
            f"Routed task to '{best_agent.name}' (score: {best_score:.2f})"
        )

        return Assignment(
            agent=best_agent,
            task_description=task_description,
            required_skills=required_skills,
            score=best_score,
        )

    def route_multi(
        self,
        tasks: list[dict],
    ) -> list[Assignment]:
        """Route multiple tasks to agents.

        Args:
            tasks: List of {"description": str, "skills": list[str]}

        Returns:
            List of assignments (one per task).
        """
        assignments = []
        for task in tasks:
            assignment = self.route(
                task_description=task["description"],
                required_skills=task["skills"],
            )
            if assignment:
                assignments.append(assignment)
            else:
                logger.warning(f"Could not route task: {task['description']}")
        return assignments

    def _score_agent(self, agent: NodeInfo, required_skills: list[str]) -> float:
        """Score how well an agent matches required skills (0.0 to 1.0)."""
        if not required_skills:
            return 0.5  # Any agent works

        agent_skills = set(agent.skill_tags)
        required = set(required_skills)

        if not agent_skills:
            return 0.0

        # Skill overlap ratio
        overlap = len(agent_skills & required)
        skill_score = overlap / len(required) if required else 0.0

        return skill_score
