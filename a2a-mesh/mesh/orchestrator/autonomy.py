"""Autonomous execution engine with guardrails.

Manages the autonomy levels and ensures agents operate
within their approved boundaries.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import IntEnum

from mesh.orchestrator.intent import (
    ApprovalDecision,
    ApprovalPolicy,
    ApprovalStatus,
    Intent,
    IntentQueue,
    RiskLevel,
)

logger = logging.getLogger(__name__)


class AutonomyLevel(IntEnum):
    """Autonomy levels for agent execution."""

    MANUAL = 0       # Every action requires human approval
    SUPERVISED = 1   # Master LLM approves medium, human approves high
    AUTONOMOUS = 2   # Master LLM approves all except critical
    FULL_AUTO = 3    # All actions auto-approved


@dataclass
class AutonomyConfig:
    """Per-agent autonomy configuration."""

    default_level: AutonomyLevel = AutonomyLevel.SUPERVISED
    agent_overrides: dict[str, AutonomyLevel] | None = None
    blocked_actions: list[str] | None = None  # Never auto-approve these

    def get_level(self, agent_id: str) -> AutonomyLevel:
        if self.agent_overrides and agent_id in self.agent_overrides:
            return self.agent_overrides[agent_id]
        return self.default_level


class AutonomyEngine:
    """Manages autonomous execution based on configured autonomy levels.

    This wraps the ApprovalPolicy to add autonomy level awareness.
    """

    def __init__(
        self,
        config: AutonomyConfig | None = None,
        intent_queue: IntentQueue | None = None,
    ):
        self.config = config or AutonomyConfig()
        self.intent_queue = intent_queue or IntentQueue()
        self._blocked_actions = set(self.config.blocked_actions or [])

    def should_auto_approve(self, intent: Intent) -> bool:
        """Check if an intent should be auto-approved based on autonomy level."""
        # Blocked actions are never auto-approved
        if intent.action in self._blocked_actions:
            return False

        level = self.config.get_level(intent.agent_id)

        if level == AutonomyLevel.FULL_AUTO:
            return True

        if level == AutonomyLevel.AUTONOMOUS:
            return intent.risk_level != RiskLevel.CRITICAL

        if level == AutonomyLevel.SUPERVISED:
            return intent.risk_level == RiskLevel.LOW

        # MANUAL — never auto-approve
        return False

    async def process_intent(
        self, intent: Intent, llm_reviewer=None
    ) -> ApprovalDecision:
        """Process an intent through the autonomy engine.

        Args:
            intent: The intent to review.
            llm_reviewer: Optional async callable(Intent) -> bool for LLM review.

        Returns:
            ApprovalDecision.
        """
        level = self.config.get_level(intent.agent_id)

        # Full auto — approve everything (except blocked actions)
        if level == AutonomyLevel.FULL_AUTO and intent.action not in self._blocked_actions:
            return ApprovalDecision(
                intent_id=intent.intent_id,
                status=ApprovalStatus.APPROVED,
                approved_by="autonomy_engine",
                reason=f"Auto-approved (autonomy level: FULL_AUTO)",
            )

        # Check if auto-approvable
        if self.should_auto_approve(intent):
            return ApprovalDecision(
                intent_id=intent.intent_id,
                status=ApprovalStatus.APPROVED,
                approved_by="autonomy_engine",
                reason=f"Auto-approved (autonomy level: {level.name}, risk: {intent.risk_level.value})",
            )

        # For SUPERVISED/AUTONOMOUS with medium risk, try LLM review
        if level >= AutonomyLevel.SUPERVISED and llm_reviewer:
            if intent.risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM):
                try:
                    approved = await llm_reviewer(intent)
                    return ApprovalDecision(
                        intent_id=intent.intent_id,
                        status=ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED,
                        approved_by="master_llm",
                        reason="Reviewed by master LLM",
                    )
                except Exception as e:
                    logger.warning(f"LLM review failed: {e}, falling through to human")

        # Fall through to human approval
        logger.info(
            f"Intent {intent.intent_id} requires human approval "
            f"(level: {level.name}, risk: {intent.risk_level.value})"
        )
        return await self.intent_queue.submit(intent)
