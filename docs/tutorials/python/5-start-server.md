# 5. Starting the Server

Now that we have an Agent Card and an Agent Executor, we can set up and start the A2A server.

The A2A Python SDK provides route factory helpers (`create_agent_card_routes`, `create_jsonrpc_routes`, `create_rest_routes`) that return Starlette `Route` objects. These work natively with [Starlette](https://www.starlette.io/) and [FastAPI](https://fastapi.tiangolo.com/) (which is Starlette-based), and the resulting application is run with an ASGI server like [Uvicorn](https://www.uvicorn.org/). In this tutorial we use Starlette with `create_agent_card_routes` and `create_jsonrpc_routes`; `create_rest_routes` is available for REST-style endpoints but is not used in this sample.

## Server Setup in Helloworld

Let's look at `__main__.py` again to see how the server is initialized and started.

```python { .no-copy }
--8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/__main__.py"
```

Let's break this down:

1. **`DefaultRequestHandler`**:

    - The SDK provides `DefaultRequestHandler`. This handler takes your `AgentExecutor` implementation (here, `HelloWorldAgentExecutor`), a `TaskStore` (here, `InMemoryTaskStore`), and the public and extended `AgentCard` objects.
    - It routes incoming A2A RPC calls to the appropriate methods on your executor (like `execute` or `cancel`).
    - The `TaskStore` is used by the `DefaultRequestHandler` to manage the lifecycle of tasks, especially for stateful interactions, streaming, and resubscription. Even if your agent executor is simple, the handler needs a task store.
    - `agent_card` is passed to the handler so it can verify the agent's declared capabilities when processing incoming requests (for example, checking whether streaming or push notifications are supported before handling those request types).
    - `extended_agent_card` is passed so the handler can serve it via the `GetExtendedAgentCard` RPC method to authenticated clients.

2. **`create_agent_card_routes` and `create_jsonrpc_routes`**:

    - `create_agent_card_routes(public_agent_card)` returns Starlette routes that expose the Agent Card at the `/.well-known/agent-card.json` endpoint for public discovery.
    - `create_jsonrpc_routes(request_handler, '/')` returns Starlette routes that handle all incoming A2A JSON-RPC method calls by delegating to the `request_handler`.
    - These route lists are combined and passed to a standard `Starlette` application.

3. **`uvicorn.run(app, ...)`**:
    - The constructed `Starlette` app is run using `uvicorn.run()`, making your agent accessible over HTTP.
    - `host='127.0.0.1'` makes the server accessible only from your local machine.
    - `port=9999` specifies the port to listen on. This matches the endpoints defined in the `AgentCard`'s `supported_interfaces`.

## Running the Helloworld Server

Navigate to the `a2a-samples` directory in your terminal (if you're not already there) and ensure your virtual environment is activated.

To run the Helloworld server:

```bash
# from the a2a-samples directory
python samples/python/agents/helloworld/__main__.py
```

You should see output similar to this, indicating the server is running:

```console { .no-copy }
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:9999 (Press CTRL+C to quit)
```

Your A2A Helloworld agent is now live and listening for requests! In the next step, we'll interact with it.
