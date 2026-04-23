# 6. Interacting with the Server

With the Helloworld A2A server running, let's send some requests to it.

## The Helloworld Test Client

The `test_client.py` script demonstrates how to:

1. Fetch the Agent Card from the server.
2. Create a client using `create_client`.
3. Send both `Send Message` and `Send Streaming Message` requests.

Open a **new terminal window**, activate your virtual environment, and navigate to the `a2a-samples` directory.

Activate the virtual environment (be sure to do this in the same directory where you created it):

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

    The `A2ACardResolver` class is a convenience. When `get_agent_card()` is called, it fetches the `AgentCard` from the server's `/.well-known/agent-card.json` endpoint (based on the provided base URL), which is then used to initialize the client.

2. **Initializing the Client & Sending a Non-Streaming Message**:

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/test_client.py:message_send"
    ```

    - The `create_client` function creates a `Client` based on the information provided by the `AgentCard` and a `ClientConfig`.
    - We construct a `Message` using the `new_text_message` helper (passing `role=Role.ROLE_USER`), then wrap it in a `SendMessageRequest`.
    - The client's `send_message` method returns an async iterator that yields a single final `Task` or `Message` response from the agent. In this example, it is a `Task`.

3. **Initializing the Client & Sending a Streaming Message**:

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/test_client.py:message_stream"
    ```

    - A separate streaming client is created via `create_client` with `streaming=True` in its `ClientConfig`.
    - We again call `send_message`, which now streams events: each iteration of the loop prints a discrete chunk as it arrives over the network.
    - Call `await streaming_client.close()` after the loop to release the underlying HTTP connection.

## Expected Output

When you run `test_client.py`, you'll see output for:

- The public agent card, displayed in a formatted summary.
- The non-streaming response: a single `task` in protobuf text format containing the completed status, the generated artifact with "Hello, World!", and the agent's intermediate status message in history.
- The streaming response: four chunks — the initial `task`, a `status_update` for WORKING, an `artifact_update` with the result, and a final `status_update` for COMPLETED.
- The extended agent card, displayed in a formatted summary (with an additional `super_hello_world` skill).

The `id` fields in the output will vary with each run.

```console { .no-copy }
                     AgentCard
--- General ---
Name        : Hello World Agent
Description : Just a hello world agent
Version     : 0.0.1

--- Interfaces ---
  [0] http://localhost:9999  (JSONRPC)

--- Capabilities ---
Streaming           : True
Push notifications  : False
Extended agent card : True

--- I/O Modes ---
Input  : text/plain
Output : text/plain

--- Skills ---
----------------------------------------------------
  ID          : hello_world
  Name        : Returns hello world
  Description : just returns hello world
  Tags        : hello world
  Example     : hi
  Example     : hello world

--- Non-Streaming Call ---

Non-streaming Client initialized.
Response:
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
                     AgentCard
--- General ---
Name        : Hello World Agent - Extended Edition
Description : The full-featured hello world agent for authenticated users.
Version     : 0.0.2

--- Interfaces ---
  [0] http://localhost:9999  (JSONRPC)

--- Capabilities ---
Streaming           : True
Push notifications  : False
Extended agent card : True

--- I/O Modes ---
Input  : text/plain
Output : text/plain

--- Skills ---
----------------------------------------------------
  ID          : hello_world
  Name        : Returns hello world
  Description : just returns hello world
  Tags        : hello world
  Example     : hi
  Example     : hello world
----------------------------------------------------
  ID          : super_hello_world
  Name        : Returns a SUPER Hello World
  Description : A more enthusiastic greeting, only for authenticated users.
  Tags        : hello world, super, extended
  Example     : super hi
  Example     : give me a super hello
```

_(Actual IDs like `xxxxxxxx`, `yyyyyyyy`, `zzzzzzzz`, `wwwwwwww`, and `vvvvvvvv` will be different UUIDs in each run.)_

This confirms your server is correctly handling basic A2A interactions with the updated SDK structure.

You can now shut down the server by pressing Ctrl+C in the terminal window where `__main__.py` is running.
