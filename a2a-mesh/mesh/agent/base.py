"""LLM client abstraction for any OpenAI-compatible endpoint."""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI

from mesh.agent.config import LLMConfig

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified async client for any OpenAI-compatible LLM endpoint.

    Works with: Ollama, vLLM, LM Studio, llama.cpp, text-generation-webui,
    OpenAI, and any other provider exposing /v1/chat/completions.
    """

    def __init__(self, config: LLMConfig):
        self.client = AsyncOpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
            timeout=float(config.timeout),
        )
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.supports_tools = config.supports_tools

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        stream: bool = False,
    ):
        """Send a chat completion request."""
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": stream,
        }
        if tools and self.supports_tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        return await self.client.chat.completions.create(**kwargs)

    async def chat_stream(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion, yielding text chunks."""
        response = await self.chat(messages, tools, stream=True)
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        tool_executor,
        max_rounds: int = 10,
    ) -> str:
        """Chat with tool calling loop. Calls tools and feeds results back.

        Args:
            messages: Conversation history.
            tools: OpenAI-format tool schemas.
            tool_executor: Callable(name, args) -> str that runs a tool.
            max_rounds: Max tool call rounds to prevent infinite loops.

        Returns:
            Final text response from the model.
        """
        if not self.supports_tools:
            # Fall back to regular chat if model doesn't support tools
            response = await self.chat(messages)
            return response.choices[0].message.content or ""

        for _ in range(max_rounds):
            response = await self.chat(messages, tools=tools)
            choice = response.choices[0]

            # If no tool calls, return the text response
            if not choice.message.tool_calls:
                return choice.message.content or ""

            # Add assistant message with tool calls
            messages.append(choice.message.model_dump())

            # Execute each tool call
            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                logger.info(f"Tool call: {fn_name}({fn_args})")
                try:
                    result = await tool_executor(fn_name, fn_args)
                except Exception as e:
                    result = f"Error executing {fn_name}: {e}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                })

        return "Max tool call rounds reached."

    async def health_check(self) -> bool:
        """Check if the LLM backend is reachable."""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
