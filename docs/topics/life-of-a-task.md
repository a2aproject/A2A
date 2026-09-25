# Life of a Task

In the Agent2Agent (A2A) Protocol, interactions vary widely. They range from
simple, stateless exchanges to complex, long-running processes. When an agent
receives a message from a client, it can respond in one of two ways:

- **Respond with a Stateless `Message`**: Use this for immediate, self-contained
    interactions. They finish without any further state to manage.
- **Initiate a Stateful `Task`**: The agent runs a `Task` through a defined
    lifecycle. It reports progress and asks for input as needed, until it
    reaches an interrupted state (such as `input-required` or `auth-required`) or
    a terminal state (such as `completed`, `canceled`, `rejected`, or `failed`).

## Group Related Interactions

A `contextId` is a key identifier. It groups multiple `Task` objects and
independent `Message` objects. This gives continuity across a series of
interactions.

- When a client sends a message for the first time, the agent responds
    with a new `contextId`. If a task is initiated, it will also have a `taskId`.
- To continue a previous interaction, clients send later messages with the same
    `contextId`.
- Clients optionally attach the `taskId` to a subsequent message to
    indicate that it continues that specific task.

The `contextId` enables collaboration toward a common goal, or a shared session
across several tasks that may run at once. Internally, an A2A agent (especially
one using an LLM) uses the `contextId` to manage its conversational state or its
LLM context.

## Agent Response: Message or Task

The choice between responding with a `Message` or a `Task` depends on the
nature of the interaction and the agent's capabilities:

- **Messages for Trivial Interactions**: Use `Message` objects for transactional
    interactions. These need no long-running processing or complex state. An agent
    might use messages to agree on the scope of a task before it commits to a
    `Task` object.
- **Tasks for Stateful Interactions**: An agent maps an incoming message to a
    supported capability. When that capability needs substantial, trackable work
    over a longer period, the agent responds with a `Task` object.

Conceptually, agents operate at different levels of complexity:

- **Message-only Agents**: Always respond with `Message` objects. They
    typically don't manage complex state or long-running executions, and use
    `contextId` to tie messages together. These agents might directly wrap LLM
    invocations and simple tools.
- **Task-generating Agents**: Always respond with `Task` objects. Even plain
    responses are modeled as completed tasks. Once a task is created, the agent
    returns only `Task` objects; once a task is complete, no more messages can be
    sent. This avoids the `Task`-versus-`Message` decision, but it creates
    completed task objects even for simple interactions.
- **Hybrid Agents**: Generate both `Message` and `Task` objects. These agents
    use messages to negotiate agent capability and the scope of work, then send a
    `Task` object to track execution and manage states like `input-required` or
    error handling. In other words, `Message` objects carry the lightweight
    back-and-forth that establishes what should be done, and a `Task` is created
    once there is committed work to execute and observe. As with task-generating
    agents, once a task is created the agent returns only `Task` objects in
    response to subsequent messages, and once a task is complete no more messages
    can be sent to it.

    For a deeper discussion of when to use messages versus tasks, see [A2A protocol: Demystifying Tasks vs Messages](https://discuss.google.dev/t/a2a-protocol-demystifying-tasks-vs-messages/255879).

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

- **Task Immutability.** Clients reliably reference a task and its state,
    artifacts, and messages. This gives a clean mapping of inputs to outputs,
    which helps orchestration and traceability.
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
`contextId`. As the domain expert, it is best placed to resolve ambiguity or spot
missing information. When something is ambiguous, the agent returns an
`input-required` state to ask the client for clarification. The client then names
the artifact in its response, and can add artifact references (`artifactId`,
`taskId`) in `Part` metadata.

## Tracking Artifact Mutation

Follow-up or refinement tasks often create new artifacts based on older ones. Track these mutations so that later interactions use only the most recent version. Think of it as a version history, where each new artifact links to the one before it.

The client is best placed to manage this artifact linkage. The client decides what counts as an acceptable result and can accept or reject new versions. So the serving agent shouldn't track artifact mutations, and this linkage is not part of the A2A protocol specification. Clients should keep the version history on their end and show the user the latest acceptable version.

To help client-side tracking, serving agents should reuse a consistent `artifact-name` when they generate a refined version of an existing artifact.

For follow-up or refinement tasks, the client should name the exact artifact it wants to refine — ideally the "latest" version from its perspective. If the client provides no artifact reference, the serving agent can:

- Attempt to infer the intended artifact based on the current `contextId`.
- If there is ambiguity or insufficient context, the agent should respond with an `input-required` task state to request clarification from the client.

## Example Follow-up Scenario

The following example illustrates a typical task flow with a follow-up:

1. Client sends a message to the agent:

    ```json
    {
      "jsonrpc": "2.0",
      "id": "req-001",
      "method": "SendMessage",
      "params": {
        "message": {
          "role": "user",
          "parts": [
            {
              "text": "Generate an image of a sailboat on the ocean."
            }
          ],
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
        "task": {
          "id": "task-boat-gen-123",
          "contextId": "ctx-conversation-abc",
          "status": {
            "state": "TASK_STATE_COMPLETED"
          },
          "artifacts": [
            {
              "artifactId": "artifact-boat-v1-xyz",
              "name": "sailboat_image.png",
              "description": "A generated image of a sailboat on the ocean.",
              "parts": [
                {
                  "filename": "sailboat_image.png",
                  "mediaType": "image/png",
                  "raw": "base64_encoded_png_data_of_a_sailboat"
                }
              ]
            }
          ]
        }
      }
    }
    ```

3. Client asks to color the boat red. This refinement request refers to the
    previous `taskId` and uses the same `contextId`.

    ```json
    {
      "jsonrpc": "2.0",
      "id": "req-002",
      "method": "SendMessage",
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
              "text": "Please modify the sailboat to be red."
            }
          ]
        }
      }
    }
    ```

4. Agent responds with a new image artifact (new task, same context, same
    artifact name): The agent creates a new task within the same `contextId`. The
    new boat image artifact keeps the same name but has a new `artifactId`.

    ```json
    {
      "jsonrpc": "2.0",
      "id": "req-002",
      "result": {
        "task": {
          "id": "task-boat-color-456",
          "contextId": "ctx-conversation-abc",
          "status": {
            "state": "TASK_STATE_COMPLETED"
          },
          "artifacts": [
            {
              "artifactId": "artifact-boat-v2-red-pqr",
              "name": "sailboat_image.png",
              "description": "A generated image of a red sailboat on the ocean.",
              "parts": [
                {
                  "filename": "sailboat_image.png",
                  "mediaType": "image/png",
                  "raw": "base64_encoded_png_data_of_a_RED_sailboat"
                }
              ]
            }
          ]
        }
      }
    }
    ```
