# 4. The Agent Executor

The core logic of how an A2A agent processes requests and generates responses/events is handled by an **Agent Executor**. The A2A Python SDK provides an abstract base class `a2a.server.agent_execution.AgentExecutor` that you implement.

## `AgentExecutor` Interface

The `AgentExecutor` class defines two primary methods:

- `async def execute(self, context: RequestContext, event_queue: EventQueue)`: Handles incoming requests that expect a response or a stream of events. It processes the user's input (available via `context`) and uses the `event_queue` to send back `Message`, `Task`, `TaskStatusUpdateEvent`, or `TaskArtifactUpdateEvent` objects.
- `async def cancel(self, context: RequestContext, event_queue: EventQueue)`: Handles requests to cancel an ongoing task.

The `RequestContext` provides information about the incoming request, such as the user's message and any existing task details. The `EventQueue` is used by the executor to send events back to the client.

## Helloworld Agent Executor

Let's look at `agent_executor.py`. It defines `HelloWorldAgentExecutor`.

1. **The Agent (`HelloWorldAgent`)**:
    This is a simple helper class that encapsulates the actual "business logic".

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/agent_executor.py:HelloWorldAgent"
    ```

    It has a simple `invoke` method that returns the string "Hello, World!".

2. **The Executor (`HelloWorldAgentExecutor`)**:
    This class implements the `AgentExecutor` interface.

    - **`__init__`**:

        ```python { .no-copy }
        --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/agent_executor.py:HelloWorldAgentExecutor_init"
        ```

        It instantiates the `HelloWorldAgent`.

    - **`execute`**:

        ```python { .no-copy }
        --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/agent_executor.py:HelloWorldAgentExecutor_execute"
        ```

        When a `message/send` or `message/stream` request comes in (both are handled by `execute` in this simplified executor):

        1. It retrieves the current task from the context or creates a new one, enqueueing it as the first event.
        2. It enqueues a `TaskStatusUpdateEvent` with a state of `TASK_STATE_WORKING` to indicate the agent has begun processing.
        3. It calls `self.agent.invoke()` to execute the actual business logic (which simply returns "Hello, World!").
        4. Finally, it enqueues a `TaskArtifactUpdateEvent` containing the result text, marking it as the last chunk of the response.

    - **`cancel`**:
        The Hello World example's `cancel` method simply raises an exception, indicating that cancellation is not supported for this basic agent.

        ```python { .no-copy }
        --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/agent_executor.py:HelloWorldAgentExecutor_cancel"
        ```

The `AgentExecutor` acts as the bridge between the A2A protocol (managed by the request handler and server application) and your agent's specific logic. It receives context about the request and uses an event queue to communicate results or updates back.
