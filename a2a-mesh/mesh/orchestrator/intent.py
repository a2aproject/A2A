"""Intent declaration, review, and approval system.

Before an agent takes any significant action, it declares its intent.
The master reviews the intent based on approval policies.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class Intent:
    """An agent's declared intention before taking action."""

    intent_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    agent_id: str = ""
    agent_name: str = ""
    task_id: str = ""
    action: str = ""  # e.g., "write_code", "execute_command", "research"
    description: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    risk_level: RiskLevel = RiskLevel.LOW
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "intent_id": self.intent_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "task_id": self.task_id,
            "action": self.action,
            "description": self.description,
            "details": self.details,
            "risk_level": self.risk_level.value,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Intent:
        return cls(
            intent_id=data.get("intent_id", str(uuid.uuid4())[:12]),
            agent_id=data.get("agent_id", ""),
            agent_name=data.get("agent_name", ""),
            task_id=data.get("task_id", ""),
            action=data.get("action", ""),
            description=data.get("description", ""),
            details=data.get("details", {}),
            risk_level=RiskLevel(data.get("risk_level", "low")),
        )


@dataclass
class ApprovalDecision:
    """Result of an intent review."""

    intent_id: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: str = ""  # "policy", "master_llm", "human"
    reason: str = ""
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def approved(self) -> bool:
        return self.status == ApprovalStatus.APPROVED

    def to_dict(self) -> dict:
        return {
            "intent_id": self.intent_id,
            "status": self.status.value,
            "approved_by": self.approved_by,
            "reason": self.reason,
            "decided_at": self.decided_at.isoformat(),
        }


class IntentQueue:
    """Queue of intents pending human approval.

    Intents are added when they require human review (via UI).
    The UI polls or subscribes via WebSocket for pending intents.
    """

    def __init__(self):
        self._pending: dict[str, Intent] = {}
        self._decisions: dict[str, asyncio.Future[ApprovalDecision]] = {}
        self._history: list[tuple[Intent, ApprovalDecision]] = []

    async def submit(self, intent: Intent) -> ApprovalDecision:
        """Submit an intent for human review. Blocks until decided."""
        self._pending[intent.intent_id] = intent
        future: asyncio.Future[ApprovalDecision] = asyncio.get_event_loop().create_future()
        self._decisions[intent.intent_id] = future

        logger.info(
            f"Intent queued for review: [{intent.risk_level.value}] "
            f"{intent.agent_name} → {intent.action}: {intent.description}"
        )

        return await future

    def approve(self, intent_id: str, by: str = "human", reason: str = "") -> bool:
        """Approve a pending intent."""
        if intent_id not in self._decisions:
            return False

        decision = ApprovalDecision(
            intent_id=intent_id,
            status=ApprovalStatus.APPROVED,
            approved_by=by,
            reason=reason,
        )

        intent = self._pending.pop(intent_id, None)
        future = self._decisions.pop(intent_id)
        future.set_result(decision)

        if intent:
            self._history.append((intent, decision))
        logger.info(f"Intent {intent_id} approved by {by}")
        return True

    def reject(self, intent_id: str, by: str = "human", reason: str = "") -> bool:
        """Reject a pending intent."""
        if intent_id not in self._decisions:
            return False

        decision = ApprovalDecision(
            intent_id=intent_id,
            status=ApprovalStatus.REJECTED,
            approved_by=by,
            reason=reason,
        )

        intent = self._pending.pop(intent_id, None)
        future = self._decisions.pop(intent_id)
        future.set_result(decision)

        if intent:
            self._history.append((intent, decision))
        logger.info(f"Intent {intent_id} rejected by {by}: {reason}")
        return True

    def get_pending(self) -> list[Intent]:
        """Get all pending intents (for UI)."""
        return list(self._pending.values())

    def get_history(self, limit: int = 50) -> list[dict]:
        """Get recent approval history."""
        recent = self._history[-limit:]
        return [
            {"intent": i.to_dict(), "decision": d.to_dict()}
            for i, d in recent
        ]


class ApprovalPolicy:
    """Determines how intents are approved based on risk level and action type."""

    def __init__(
        self,
        auto_approve_risks: list[str] | None = None,
        auto_approve_actions: list[str] | None = None,
        master_approve_risks: list[str] | None = None,
        require_human_risks: list[str] | None = None,
        require_human_actions: list[str] | None = None,
    ):
        self.auto_approve_risks = set(auto_approve_risks or ["low"])
        self.auto_approve_actions = set(
            auto_approve_actions or ["research", "summarize", "analyze", "read_file"]
        )
        self.master_approve_risks = set(master_approve_risks or ["medium"])
        self.require_human_risks = set(require_human_risks or ["high", "critical"])
        self.require_human_actions = set(
            require_human_actions or ["execute_command", "deploy", "delete_file"]
        )

    def evaluate(self, intent: Intent) -> str:
        """Determine approval path for an intent.

        Returns: "auto", "master_llm", or "human"
        """
        # Hard rules: certain actions always need human approval
        if intent.action in self.require_human_actions:
            return "human"
        if intent.risk_level.value in self.require_human_risks:
            return "human"

        # Auto-approve low-risk and safe actions
        if intent.risk_level.value in self.auto_approve_risks:
            return "auto"
        if intent.action in self.auto_approve_actions:
            return "auto"

        # Master LLM can approve medium risk
        if intent.risk_level.value in self.master_approve_risks:
            return "master_llm"

        return "human"
