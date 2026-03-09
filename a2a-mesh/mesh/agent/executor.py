"""A2A AgentExecutor implementation backed by an OpenAI-compatible LLM."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    Artifact,
    Message,
    Part,
    Role,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TaskArtifactUpdateEvent,
    TextPart,
)

from mesh.agent.base import LLMClient
from mesh.agent.tools import ToolRegistry

logger = logging.getLogger(__name__)


class MeshAgentExecutor(AgentExecutor):
    """A2A executor backed by any OpenAI-compatible LLM.

    Bridges the A2A protocol with OpenAI chat completions.
    Maintains conversation history per context for multi-turn support.
    """

    def __init__(
        self,
        llm: LLMClient,
        system_prompt: str,
        tools: ToolRegistry | None = None,
    ):
        self.llm = llm
        self.system_prompt = system_prompt
        self.tools = tools
        self._conversations: dict[str, list[dict]] = {}

    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Handle an incoming A2A message."""
        user_text = self._extract_text(context)
        context_id = self._get_context_id(context)

        logger.info(f"Executing task in context {context_id}: {user_text[:100]}")

        # Build conversation history
        if context_id not in self._conversations:
            self._conversations[context_id] = [
                {"role": "system", "content": self.system_prompt}
            ]
        self._conversations[context_id].append(
            {"role": "user", "content": user_text}
        )

        try:
            # If tools available and LLM supports them, use tool calling
            if self.tools and self.llm.supports_tools and len(self.tools) > 0:
                response_text = await self.llm.chat_with_tools(
                    messages=list(self._conversations[context_id]),
                    tools=self.tools.get_schemas(),
                    tool_executor=self.tools.execute,
                )
            else:
                # Stream the response
                response_text = ""
                async for chunk in self.llm.chat_stream(
                    self._conversations[context_id]
                ):
                    response_text += chunk

            # Store assistant response in history
            self._conversations[context_id].append(
                {"role": "assistant", "content": response_text}
            )

            # Send artifact with full response
            artifact = Artifact(
                artifactId=str(uuid.uuid4()),
                parts=[Part(root=TextPart(text=response_text))],
                name="response",
            )
            event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    taskId=self._get_task_id(context),
                    contextId=context_id,
                    artifact=artifact,
                    lastChunk=True,
                )
            )

            # Send completed status
            event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    taskId=self._get_task_id(context),
                    contextId=context_id,
                    status=TaskStatus(state=TaskState.completed),
                    final=True,
                )
            )

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            event_queue.enqueue_event(
                TaskStatusUpdateEvent(
                    taskId=self._get_task_id(context),
                    contextId=context_id,
                    status=TaskStatus(
                        state=TaskState.failed,
                        message=Message(
                            role=Role.agent,
                            messageId=str(uuid.uuid4()),
                            parts=[Part(root=TextPart(text=f"Error: {e}"))],
                        ),
                    ),
                    final=True,
                )
            )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Handle task cancellation."""
        context_id = self._get_context_id(context)
        event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                taskId=self._get_task_id(context),
                contextId=context_id,
                status=TaskStatus(state=TaskState.canceled),
                final=True,
            )
        )

    def _extract_text(self, context: RequestContext) -> str:
        """Extract text content from A2A request message."""
        message = context.message
        if message and message.parts:
            texts = []
            for part in message.parts:
                if hasattr(part, "root") and hasattr(part.root, "text"):
                    texts.append(part.root.text)
                elif hasattr(part, "text"):
                    texts.append(part.text)
            return "\n".join(texts) if texts else ""
        return ""

    def _get_context_id(self, context: RequestContext) -> str:
        """Get or generate context ID."""
        if hasattr(context, "context_id") and context.context_id:
            return context.context_id
        if hasattr(context, "task") and context.task:
            return context.task.contextId or str(uuid.uuid4())
        return str(uuid.uuid4())

    def _get_task_id(self, context: RequestContext) -> str:
        """Get or generate task ID."""
        if hasattr(context, "task") and context.task:
            return context.task.id
        return str(uuid.uuid4())
