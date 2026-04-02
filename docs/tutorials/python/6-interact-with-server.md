# 6. Interacting with the Server

With the Helloworld A2A server running, let's send some requests to it. The SDK includes a client (`A2AClient`) that simplifies these interactions.

## The Helloworld Test Client

The `test_client.py` script demonstrates how to:

1. Fetch the Agent Card from the server.
2. Create an `A2AClient` instance.
3. Send both non-streaming (`message/send`) and streaming (`message/stream`) requests.

Open a **new terminal window**, activate your virtual environment, and navigate to the `a2a-samples` directory.

Activate virtual environment (Be sure to do this in the same directory where you created the virtual environment):

=== "Mac/Linux"

    ```sh
    source .venv/bin/activate
    ```

=== "Windows"

    ```powershell
    .venv\Scripts\activate
    ```

Run the test client:

```bash
# from the a2a-samples directory
python samples/python/agents/helloworld/test_client.py
```

## Understanding the Client Code

Let's look at key parts of `test_client.py`:

1. **Fetching the Agent Card**:

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/test_client.py:A2ACardResolver"
    ```

    The `A2ACardResolver` class is a convenience. It first fetches the `AgentCard` from the server's `/.well-known/agent-card.json` endpoint (based on the provided base URL) which is then used to initialize the client.

2. **Initializing the Client & Sending a Non-Streaming Message**:

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/test_client.py:message/send"
    ```

    - A `ClientFactory` creates a non-streaming client based on the fetched card.
    - We construct a `Message` object using `Role.ROLE_USER` and `Part` for the content.
    - This is wrapped in a `SendMessageRequest`.
    - The client's `send_message` method returns an async generator that yields a sequence of `Task` events from the agent.

3. **Initializing the Client & Sending a Streaming Message**:

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/test_client.py:message/stream"
    ```

    - A new streaming client is created via `ClientFactory` configured with `streaming=True`.
    - We again call `send_message` (which now handles both streaming and non-streaming under the same method name, based on the `ClientConfig` and agent `capabilities`).
    - The response dynamically yields `Task` events as they are streamed over the network.

## Expected Output

When you run `test_client.py`, you'll see in protobuf text format outputs for:

- The non-streaming response (a single final `task` log detailing the history, status, and the generated artifact containing the "Hello, World!" text).
- The streaming response (multiple discrete events including the initial `task`, a `status_update`, and a final `artifact_update` containing the "Hello, World!" text).

The `id` fields in the output will vary with each run.

```console { .no-copy }
// Non-streaming response
task {
  id: "xxxxxxxx"
  context_id: "yyyyyyyy"
  status {
    state: TASK_STATE_COMPLETED
  }
  artifacts {
    artifact_id: "zzzzzzzz"
    name: "result"
    parts {
      text: "Hello, World!"
    }
  }
  history {
    message_id: "vvvvvvvv"
    context_id: "yyyyyyyy"
    task_id: "xxxxxxxx"
    role: ROLE_USER
    parts {
      text: "Say hello."
    }
  }
  history {
    message_id: "wwwwwwww"
    role: ROLE_AGENT
    parts {
      text: "Processing request..."
    }
  }
}

// Streaming response
task {
  id: "xxxxxxxx-s"
  context_id: "yyyyyyyy-s"
  status {
    state: TASK_STATE_SUBMITTED
  }
  history {
    message_id: "vvvvvvvv"
    context_id: "yyyyyyyy-s"
    task_id: "xxxxxxxx-s"
    role: ROLE_USER
    parts {
      text: "Say hello."
    }
  }
}

Response chunk:
status_update {
  task_id: "xxxxxxxx-s"
  context_id: "yyyyyyyy-s"
  status {
    state: TASK_STATE_WORKING
    message {
      message_id: "zzzzzzzz-s"
      role: ROLE_AGENT
      parts {
        text: "Processing request..."
      }
    }
  }
}

Response chunk:
artifact_update {
  task_id: "xxxxxxxx-s"
  context_id: "yyyyyyyy-s"
  artifact {
    artifact_id: "wwwwwwww-s"
    name: "result"
    parts {
      text: "Hello, World!"
    }
  }
}

Response chunk:
status_update {
  task_id: "xxxxxxxx-s"
  context_id: "yyyyyyyy-s"
  status {
    state: TASK_STATE_COMPLETED
  }
}
```

_(Actual IDs like `xxxxxxxx`, `yyyyyyyy`, `zzzzzzzz`, `vvvvvvvv`, `wwwwwwww` will be different UUIDs/request IDs)_

This confirms your server is correctly handling basic A2A interactions with the updated SDK structure!

Now you can shut down the server by typing Ctrl+C in the terminal window where `__main__.py` is running.
