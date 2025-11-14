# Life of a Task

In the Agent2Agent (A2A) Protocol, interactions can range from simple, stateless
exchanges to complex, long-running processes. When an agent receives a message
from a client, it can respond in one of two fundamental ways:

- **Respond with a Stateless `Message`**: This type of response is
    typically used for immediate, self-contained interactions that conclude
    without requiring further state management.
- **Initiate a Stateful `Task`**: If the response is a `Task`, the agent will
    process it through a defined lifecycle, communicating progress and requiring
    input as needed, until it reaches an interrupted state (e.g.,
    `input-required`, `auth-required`) or a terminal state (e.g., `completed`,
    `canceled`, `rejected`, `failed`).

## Group Related Interactions

A `contextId` is a crucial identifier that logically groups multiple `Task`
objects and independent `Message` objects, providing continuity across a series of
interactions.

- When a client sends a message for the first time, the agent responds
    with a new `contextId`. If a task is initiated, it will also have a `taskId`.
- Clients can send subsequent messages and include the same `contextId` to
    indicate that they are continuing their previous interaction within the same
    context.
- Clients optionally attach the `taskId` to a subsequent message to
    indicate that it continues that specific task.

The `contextId` enables collaboration towards a common goal or a shared
contextual session across multiple, potentially concurrent tasks. Internally, an
A2A agent (especially one using an LLM) uses the `contextId` to manage its internal
conversational state or its LLM context.

## Agent Response: Message or Task

The choice between responding with a `Message` or a `Task` depends on the
nature of the interaction and the agent's capabilities:

- **Messages for Trivial Interactions**: `Message` objects are suitable for
    transactional interactions that don't require long-running
    processing or complex state management. An agent might use messages to
    negotiate the acceptance or scope of a task before committing to a `Task`
    object.
- **Tasks for Stateful Interactions**: Once an agent maps the intent of an
    incoming message to a supported capability that requires substantial,
    trackable work over an extended period, the agent responds with a `Task`
    object.

Conceptually, agents operate at different levels of complexity:

- **Message-only Agents**: Always respond with `Message` objects. They
    typically don't manage complex state or long-running executions, and use
    `contextId` to tie messages together. These agents might directly wrap LLM
    invocations and simple tools.
- **Task-generating Agents**: Always respond with `Task` objects, even for
    responses, which are then modeled as completed tasks. Once a task is
    created, the agent will only return `Task` objects in response to messages
    sent, and once a task is complete, no more messages can be sent. This
    approach avoids deciding between `Task` versus `Message`, but creates completed task objects
    for even simple interactions.
- **Hybrid Agents**: Generate both `Message` and `Task` objects. These agents
    use messages to negotiate agent capability and the scope of work for a task,
    then send a `Task` object to track execution and manage states like
    `input-required` or error handling. Once a task is created, the agent will
    only return `Task` objects in response to messages sent, and once a task is
    complete, no more messages can be sent. A hybrid agent uses messages to
    negotiate the scope of a task, and then generate a task to track its
    execution.
    For more information about hybrid agents, see [A2A protocol: Demystifying Tasks vs Messages](https://discuss.google.dev/t/a2a-protocol-demystifying-tasks-vs-messages/255879).

## Task Refinements

Clients often need to send new requests based on task results or refine the
outputs of previous tasks. This is modeled by starting another interaction using
the same `contextId` as the original task. Clients further hint the agent by
providing references to the original task using `referenceTaskIds` in the
`Message` object. The agent then responds with either a new `Task` or a
`Message`.

## Task Immutability

Once a task reaches a terminal state (completed, canceled, rejected, or failed),
it cannot restart. Any subsequent interaction related to that task, such as a
refinement, must initiate a new task within the same `contextId`. This principle
offers several benefits:

- **Task Immutability.** Clients reliably reference tasks and their
    associated state, artifacts, and messages, providing a clean mapping of
    inputs to outputs. This is valuable for orchestration and traceability.
- **Clear Unit of Work.** Every new request, refinement, or follow-up becomes
    a distinct task. This simplifies bookkeeping, allows for granular tracking
    of an agent's work, and enables tracing each artifact to a specific unit of
    work.
- **Easier Implementation.** This removes ambiguity for agent developers
    regarding whether to create a new task or restart an existing one.

## Parallel Follow-ups

A2A supports parallel work by enabling agents to create distinct, parallel
tasks for each follow-up message sent within the same `contextId`. This allows
clients to track individual tasks and create new dependent tasks as soon as a
prerequisite task is complete.

For example:

- Task 1: Book a flight to Helsinki.
- Task 2: Based on Task 1, book a hotel.
- Task 3: Based on Task 1, book a snowmobile activity.
- Task 4: Based on Task 2, add a spa reservation to the hotel booking.

## Referencing Previous Artifacts

The serving agent infers the relevant artifact from a referenced task or from the
`contextId`. As the domain expert, the serving agent is best suited to resolve
ambiguity or identify missing information. If there is ambiguity, the agent asks
the client for clarification by returning an `input-required` state. The client
then specifies the artifact in its response, optionally populating artifact
references (`artifactId`, `taskId`) in `Part` metadata.

## Tracking Artifact Mutation

Follow-up or refinement tasks often lead to the creation of new artifacts based on older ones. Tracking these mutations is important to ensure that only the most recent version of an artifact is used in subsequent interactions. This could be conceptualized as a version history, where each new artifact is linked to its predecessor.

However, the client is in the best position to manage this artifact linkage. The client determines what constitutes an acceptable result and has the ability to accept or reject new versions. Therefore, the serving agent shouldn't be responsible for tracking artifact mutations, and this linkage is not part of the A2A protocol specification. Clients should maintain this version history on their end and present the latest acceptable version to the user.

To facilitate client-side tracking, serving agents should use a consistent `artifact-name` when generating a refined version of an existing artifact.

When initiating follow-up or refinement tasks, the client should explicitly reference the specific artifact they intend to refine, ideally the "latest" version from their perspective. If the artifact reference is not provided, the serving agent can:

- Attempt to infer the intended artifact based on the current `contextId`.
- If there is ambiguity or insufficient context, the agent should respond with an `input-required` task state to request clarification from the client.

## Example Follow-up Scenario

The following example illustrates a typical task flow with a follow-up:

1. Client sends a message to the agent:

    ```json
    {
      "jsonrpc": "2.0",
      "id": "req-001",
      "method": "message.send",
      "params": {
        "message": {
          "role": "user",
          "parts": [
            {
              "kind": "text",
              "text": "Generate an image of a sailboat on the ocean."
            }
          ]
          "messageId": "msg-user-001"
        }
      }
    }
    ```

2. Agent responds with a boat image (completed task):

    ```json
    {
      "jsonrpc": "2.0",
      "id": "req-001",
      "result": {
        "id": "task-boat-gen-123",
        "contextId": "ctx-conversation-abc",
        "status": {
          "state": "completed"
        },
        "artifacts": [
          {
            "artifactId": "artifact-boat-v1-xyz",
            "name": "sailboat_image.png",
            "description": "A generated image of a sailboat on the ocean.",
            "parts": [
              {
                "kind": "file",
                "file": {
                  "name": "sailboat_image.png",
                  "mimeType": "image/png",
                  "bytes": "base64_encoded_png_data_of_a_sailboat"
                }
              }
            ]
          }
        ],
        "kind": "task"
      }
    }
    ```

3. Client asks to color the boat red. This refinement request refers to the
    previous `taskId` and uses the same `contextId`.

    ```json
    {
      "jsonrpc": "2.0",
      "id": "req-002",
      "method": "message.send",
      "params": {
        "message": {
          "role": "user",
          "messageId": "msg-user-002",
          "contextId": "ctx-conversation-abc",
          "referenceTaskIds": [
            "task-boat-gen-123"
          ],
          "parts": [
            {
              "kind": "text",
              "text": "Please modify the sailboat to be red."
            }
          ]
        }
      }
    }
    ```

4. Agent responds with a new image artifact (new task, same context, same
    artifact name): The agent creates a new task within the same `contextId`. The
    new boat image artifact retains the same name but has a new `artifactId`.

    ```json
    {
      "jsonrpc": "2.0",
      "id": "req-002",
      "result": {
        "id": "task-boat-color-456",
        "contextId": "ctx-conversation-abc",
        "status": {
          "state": "completed"
        },
        "artifacts": [
          {
            "artifactId": "artifact-boat-v2-red-pqr",
            "name": "sailboat_image.png",
            "description": "A generated image of a red sailboat on the ocean.",
            "parts": [
              {
                "kind": "file",
                "file": {
                  "name": "sailboat_image.png",
                  "mimeType": "image/png",
                  "bytes": "base64_encoded_png_data_of_a_RED_sailboat"
                }
              }
            ]
          }
        ],
        "kind": "task"
      }
    }
    ```
