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

1. **Fetching the Agent Card & Initializing the Client**:

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/test_client.py:A2ACardResolver"
    ```

    The `A2ACardResolver` class is a convenience. It first fetches the `AgentCard` from the server's `/.well-known/agent-card.json` endpoint (based on the provided base URL) which is then used to initialize the client.

2. **Sending a Non-Streaming Message**:

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/test_client.py:send_message"
    ```

    - A `ClientFactory` creates a non-streaming client based on the fetched card.
    - We construct a `Message` object using `Role.ROLE_USER` and `Part` for the content.
    - This is wrapped in a `SendMessageRequest`.
    - The client's `send_message` method returns an async generator that yields a sequence of `Task` events from the agent.

3. **Sending a Streaming Message**:

    ```python { .no-copy }
    --8<-- "https://raw.githubusercontent.com/a2aproject/a2a-samples/refs/heads/main/samples/python/agents/helloworld/test_client.py:send_message_streaming"
    ```

    - A new streaming client is created via `ClientFactory` configured with `streaming=True`.
    - We again call `send_message` (which now handles both streaming and non-streaming under the same method name, based on the `ClientConfig`).
    - The response dynamically yields `Task` events as they are streamed over the network.

## Expected Output

When you run `test_client.py`, you'll see JSON outputs for:

- The non-streaming response (a single final `task` log detailing the history, status, and artifact generated).
- The streaming response (multiple discrete events including the initial `task`, a `status_update`, and a final `artifact_update`).

The `id` fields in the output will vary with each run.

```console { .no-copy }
// Non-streaming response
task {
  id: "f2d64c50-0850-4abf-96bf-e5702967ed21"
  context_id: "36a81ce7-a041-4698-b029-f0d900ab1562"
  status {
    state: TASK_STATE_WORKING
    message {
      message_id: "9e666f39-cf19-41b3-a23c-c3ad7cf011d5"
      role: ROLE_AGENT
      parts {
        text: "Processing request..."
      }
    }
  }
  artifacts {
    artifact_id: "bb39244e-2c35-436d-8d5f-b62967b15ae0"
    name: "result"
    parts {
      text: "Hello, World!"
    }
  }
  history {
    message_id: "32166163067c40c0a71f74064c2bea33"
    context_id: "36a81ce7-a041-4698-b029-f0d900ab1562"
    task_id: "f2d64c50-0850-4abf-96bf-e5702967ed21"
    role: ROLE_USER
    parts {
      text: "how much is 10 USD in INR?"
    }
  }
}
```

This confirms your server is correctly handling basic A2A interactions with the updated SDK structure!

Now you can shut down the server by typing Ctrl+C in the terminal window where `__main__.py` is running.
