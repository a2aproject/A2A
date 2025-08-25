# Tutorial: Multi-Agent Collaboration with A2A

This tutorial demonstrates multi-agent collaboration using A2A (Agent2Agent)
communication. A2A enables different agents to interact and solve complex
problems together. You explore a prebuilt example featuring a reimbursement
agent, developed with the Agent Development Kit (ADK), an open-source toolkit
from Google. This example illustrates how to expose a remote agent's endpoint to
a client, facilitating seamless collaboration.

## Objectives

-  Understand core A2A agent components.
-  Set up the development environment.
-  Run a multi-agent collaboration example.
-  Observe agent interaction in a reimbursement scenario.

## Costs

This tutorial uses open-source tools and local execution. It does not incur any charges for Google Cloud services.

## Before You Begin

1.  In the Google Cloud console, on the project selector page, select or create a Google Cloud project.
    **Note**: If you don't plan to keep the resources that you create in this procedure, create a project instead of selecting an existing project. After you finish these steps, you can delete the project, removing all resources associated with the project.
    [Go to project selector](https://console.cloud.google.com/projectselector2/home/dashboard)
1.  Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
1.  Install [Python 3.9 or later](https://www.python.org/downloads/).
1.  Install [pip](https://pip.pypa.io/en/stable/installation/), the Python package installer.

## Understand A2A Agent Components

A2A facilitates collaboration between agents. To convert an agent into an A2A
agent, define three key components: an `AgentSkill`, an `AgentCard`, and an
`AgentExecutor`.

An `AgentSkill` defines a specific capability or tool the agent offers. The
`AgentCard` provides metadata about the agent, including its name, description,
and available skills. The `AgentExecutor` handles the agent's execution logic,
processing requests and generating responses.

The following code defines the `AgentSkill` and `AgentCard` for a reimbursement
agent:

```python
skill = AgentSkill(
           id='process_reimbursement',
           name='Process Reimbursement Tool',
           description='Helps with the reimbursement process for users given the amount and purpose of the reimbursement.',
           tags=['reimbursement'],
           examples=[
               'Can you reimburse me $20 for my lunch with the clients?'
           ],
       )
agent_card = AgentCard(
           name='Reimbursement Agent',
           description='This agent handles the reimbursement process for the employees given the amount and purpose of the reimbursement.',
           url=f'http://{host}:{port}/',
           version='1.0.0',
           default_input_modes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
           default_output_modes=ReimbursementAgent.SUPPORTED_CONTENT_TYPES,
           capabilities=capabilities,
           skills=[skill],
       )
```

The `ReimbursementAgentExecutor` class implements the `AgentExecutor` interface.
This class defines how the reimbursement agent processes incoming requests and
interacts with the A2A framework. It manages task states, updates, and artifact
processing requests and generating responses.

```python
import json
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
   DataPart,
   Part,
   Task,
   TaskState,
   TextPart,
   UnsupportedOperationError,
)
from a2a.utils import (
   new_agent_parts_message,
   new_agent_text_message,
   new_task,
)
from a2a.utils.errors import ServerError
from agent import ReimbursementAgent


class ReimbursementAgentExecutor(AgentExecutor):
   """Reimbursement AgentExecutor Example."""


   def __init__(self):
       self.agent = ReimbursementAgent()


   async def execute(
       self,
       context: RequestContext,
       event_queue: EventQueue,
   ) -> None:
       query = context.get_user_input()
       task = context.current_task


       # This agent always produces Task objects. If this request does
       # not have current task, create a new one and use it.
       if not task:
           task = new_task(context.message)
           await event_queue.enqueue_event(task)
       updater = TaskUpdater(event_queue, task.id, task.context_id)
       # invoke the underlying agent, using streaming results. The streams
       # now are update events.
       async for item in self.agent.stream(query, task.context_id):
           is_task_complete = item['is_task_complete']
           artifacts = None
           if not is_task_complete:
               await updater.update_status(
                   TaskState.working,
                   new_agent_text_message(
                       item['updates'], task.context_id, task.id
                   ),
               )
               continue
           # If the response is a dictionary, assume its a form
           if isinstance(item['content'], dict):
               # Verify it is a valid form
               if (
                   'response' in item['content']
                   and 'result' in item['content']['response']
               ):
                   data = json.loads(item['content']['response']['result'])
                   await updater.update_status(
                       TaskState.input_required,
                       new_agent_parts_message(
                           [Part(root=DataPart(data=data))],
                           task.context_id,
                           task.id,
                       ),
                       final=True,
                   )
                   continue
               await updater.update_status(
                   TaskState.failed,
                   new_agent_text_message(
                       'Reaching an unexpected state',
                       task.context_id,
                       task.id,
                   ),
                   final=True,
               )
               break
           # Emit the appropriate events
           await updater.add_artifact(
               [Part(root=TextPart(text=item['content']))], name='form'
           )
           await updater.complete()
           break


   async def cancel(
       self, request: RequestContext, event_queue: EventQueue
   ) -> Task | None:
       raise ServerError(error=UnsupportedOperationError())
```

## Set Up the Environment

Clone the [`a2a-samples`](https://github.com/a2aproject/a2a-samples/)
GitHub repository to access the prebuilt reimbursement
agent and host client.

1.  Open your terminal or command prompt.
2.  Clone the repository:
    ```bash
    git clone https://github.com/a2aproject/a2a-samples.git
    ```
3.  Navigate to the `demo` directory:
    ```bash
    cd a2a-samples/demo
    ```

## Run the Reimbursement Agent

Start the remote reimbursement agent. This agent exposes its endpoint for client
interaction.

1.  From the `demo` directory, navigate to the `reimbursement_agent` directory:
    ```bash
      cd reimbursement_agent
    ```

2.  Install the required Python dependencies:
    ```bash
      pip install -r requirements.txt
    ```

3.  Run the agent:
    ```bash
      python main.py
    ```
    The agent starts and listens for incoming requests. Keep this terminal window open.

## Run the host client

Start the host client. This client interacts with the reimbursement agent.

1.  Open a new terminal or command prompt window.
2.  Navigate to the `demo` directory within your cloned repository:
    ```bash
      cd a2a-samples/demo
    ```
3.  Navigate to the `host_agent` directory:
    ```bash
      cd host_agent
    ```
4.  Install the required Python dependencies:
    ```bash
      pip install -r requirements.txt
    ```
5.  Run the host client:
    ```bash
      python main.py
    ```
    The host client starts and presents a user interface for interaction.

## Observe Multi-agent Collaboration

Interact with the host client's user interface to initiate a reimbursement
request. Observe how the host client communicates with the remote reimbursement
agent to process the request. The agents collaborate to gather necessary
information and complete the reimbursement task. This interaction demonstrates
the multi-agent collaboration pattern.
