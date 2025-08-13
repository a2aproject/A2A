
## Advanced A2A Agent Card Configuration

This guide explores advanced concepts related to A2A agent development and
deployment to Google Cloud. It includes detailed agent card configurations, advanced
authentication mechanisms, and server creation techniques using A2A SDKs. 

An A2A
agent exposes an agent card, which serves as a manifest detailing its
capabilities, skills, and critical authentication information.

### Example of an Advanced Agent Card Definition

The following code sample shows an advanced agent card definition:


```typescript
const movieAgentCard: AgentCard = {
 name: "Calendar Agent",
 description: "An agent that can manage a user's calendar",
 // This is where the A2A API calls will be made. Adjust the base URL and port as needed.
 url: "http://localhost:41241/",
 provider: {
   organization: "A2A Samples",
   url: "https://example.com/a2a-samples" // Added provider URL
 },
 version: "0.0.2", // Incremented version
 capabilities: {
   streaming: true, // The new framework supports streaming
   pushNotifications: false, // Assuming not implemented for this agent yet
   stateTransitionHistory: true, // Agent uses history
 },
 defaultInputModes: ["text"],
 defaultOutputModes: ["text"],
 skills: [
   {
     id: "Check Availability",
     name: "Check Availability",
     description: "Checks a user's availability for a time using their Google Calendar",
     tags: ["meetings", "free-slot", "schedule"],
     examples: [
       "Am I free from 10am to 11am tomorrow?"
     ],
     inputModes: ["text"], // Explicitly defining for skill
     outputModes: ["text"] // Explicitly defining for skill
   },
 ],
 supportsAuthenticatedExtendedCard: false,
};
```

## Auth Information Within the Agent Card

The A2A agent card includes authentication information using:


*   **`securitySchemes` and `security` parameters**: This adheres to the standard
   OpenAPI specification for describing API security.
*   **Client parsing**: Clients parse this authentication information from the agent
   card to authorize themselves with the A2A server when invoking A2A APIs.
   This process establishes the initial layer of authentication.

Additional considerations:

*   **Tool-specific auth**: An A2A agent might use tools to serve a user query.
   These tools might require further authentication. The agent then marks the
   task with an `auth-required` status.
*   **IAM-based auth**: If the A2A server is exposed only within the
   Google Cloud platform, IAM-based authentication can be used. In such a case,
   omit this authentication information from the agent card.

### Sample JWT-Based Authentication Information in Agent Card

The following code sample shows how to include JWT-based authentication
information in the agent card:


```typescript
const movieAgentCard: AgentCard = {
   name: "Calendar Agent",
   ...
   securitySchemes: {
       bearerJwtAuth: {
           type: "http",
           scheme: "bearer",
           bearerFormat: "JWT",
       }
   },
   security: [
       {
           bearerAuth: []
       }
   ]
};
```

## Build the A2A Server: SDKs and Agent Executors

Developing an A2A server involves leveraging specialized Software Development
Kits (SDKs) to streamline the process. Implement the `AgentExecutor` to
efficiently handle diverse user requests and interactions.

## Use A2A SDKs for Agent Development

A2A provides SDKs in both Python and JavaScript. These SDKs simplify the
development of A2A-compliant agents for developers.


*   **Python A2A SDK installation:**


   ```bash
   pip install a2a-sdk
   ```

*   **JavaScript A2A SDK installation:**


   ```bash
   npm install @a2a-js/sdk
   ```

The SDKs abstract away A2A protocol constructs, including TaskStore management,
task lifecycles, and underlying transport layer handling (for example, JSON-RPC,
gRPC). Focus primarily on implementing an `AgentExecutor` that efficiently
processes incoming user requests and emits relevant messages or task events.


For information on how to integrate with SDKs in your preferred language, see
[A2A samples for SDK integration](https://github.com/a2a-samples). For SDK
[Python SDK repository](https://github.com/a2a-python-sdk) and
[JavaScript SDK repository](https://github.com/a2a-js-sdk).

## A2A Agent Executor Implementation with ADK

Effectively use the Agent Development Kit (ADK) for developing and
orchestrating A2A agents. For ADK sample agent implementations, see
[samples](https://github.com/a2a-samples).

### Basic ADK Agent Definition

The following code sample shows a basic ADK agent definition:


```python
from google.adk.agents import LlmAgent


facts_agent = LlmAgent(
   name="facts_agent",
   model="gemini-2.0-flash-001",
   description=("Agent to give interesting facts."),
   instruction=("You are a helpful agent who can provide interesting facts."),
   tools=[google_search],
)
```

To seamlessly integrate with A2A SDKs and expose A2A APIs correctly, you must
implement a specific agent executor interface. For more information, see the
[Official A2A wrapper for ADK](https://github.com/a2a-adk-wrapper).

### Sample Wrapper: Convert ADK Agent to A2A Executor

The following code sample shows how to convert an ADK agent to an A2A executor:


```python
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue, EventConsumer


from google.adk.memory.base_memory_service import BaseMemoryService
from google.adk.artifacts.base_artifact_service import BaseArtifactService
from google.adk.sessions.base_session_service import BaseSessionService


class AdkAgentToA2AExecutor(AgentExecutor):
   _runner: Runner;


   def __init__(
       self,
       name: str,
       agent: BaseAgent,
       session_service: BaseSessionService = InMemorySessionService(),
       artifact_service: BaseArtifactService | None = None,
       memory_service: BaseMemoryService | None = None,
   ):
       self._runner = Runner(
           app_name=name,
           agent=agent,
           session_service=session_service,
           artifact_service=artifact_service,
           memory_service=memory_service,
       )
       self._name = name
       self._user_id = "remote_agent"


   async def execute(
       self,
       context: RequestContext,
       event_queue: EventQueue,
   ) -> None:
       query = context.get_user_input()
       task = context.current_task
   raise ServerError(error=UnsupportedOperationError())


   async def cancel(
       self, context: RequestContext, event_queue: EventQueue
   ) -> None:
       raise ServerError(error=UnsupportedOperationError())
```

### Implement the `execute()` Method

The following sections describe the key steps to implement the `execute()` method:

#### Create a Task
An agent either directly responds with a message or, more
commonly, generates a `Task` object. In the provided example, the agent
consistently produces `Task` objects. If no current task is associated with
the request, a new one is automatically created and enqueued.

```python
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
       if not context.message:
           return


       task = new_task(context.message)
       await event_queue.enqueue_event(task)


   updater = TaskUpdater(event_queue, task.id, task.contextId)
```

#### Manage and Retrieve a Session

Based on the `contextId` from the `RequestContext`, the `execute()` method
initiates or retrieves an existing session. A `contextId` logically groups
multiple `Task` or `Message` objects.

```python
async def execute(
       self,
       context: RequestContext,
       event_queue: EventQueue,
   ) -> None:
       # ...
       session_id = task.contextId
       session = await self._runner.session_service.get_session(
           app_name=self._name,
           user_id=self._user_id,
           session_id=session_id,
       )
       if session is None:
           session = await self._runner.session_service.create_session(
               app_name=self._name,
               user_id=self._user_id,
               state={},
               session_id=session_id,
           )
```

#### Run the ADK Agent

Run the ADK agent to generate a response based on the user's query.


```python
async def execute(
       self,
       context: RequestContext,
       event_queue: EventQueue,
   ) -> None:
       # ...


       content = types.Content(
           role="user", parts=[types.Part.from_text(text=query)]
       )


       # Working status
       await updater.start_work()


       # To record partial text chunks
       full_response_text = ""


       async for event in self._runner.run_async(
           user_id=self._user_id, session_id=session.id, new_message=content
       ):
           if event.partial and event.content and event.content.parts and event.content.parts[0].text:
               full_response_text += event.content.parts[0].text
```

#### Finalize Task

Ensure that the task's lifecycle is properly concluded. Mark the task as complete
once the final response from the agent is received and processed.

```python
async def execute(
   self,
   context: RequestContext,
   event_queue: EventQueue,
 ) -> None:
   # ...


   async for event in self._runner.run_async(
     user_id=self._user_id, session_id=session.id, new_message=content
   ):
     if event.partial and event.content and event.content.parts and event.content.parts[0].text:
       full_response_text += event.content.parts[0].text


     # Check if this event marks the final response.
     if event.is_final_response():


       # 1. Check if it has text parts.
       if event.content and event.content.parts and event.content.parts[0].text:
         final_text = full_response_text + (event.content.parts[0].text if not event.partial else "")
         await updater.add_artifact(
           [Part(root=TextPart(text=final_text))], name='response'
          )
         await updater.complete()


       # 2. If there's function response. Normally LLM summarises it and adds to text parts. If not, we simply include the function response.
       elif event.actions and event.actions.skip_summarization and event.get_function_responses():
         response_data = event.get_function_responses()
         await updater.add_artifact(
           [Part(root=TextPart(text=str(response_data[0].response)))], name='response'
         )
         await updater.complete()


       # 3. In special case of long running tools, we mark the task as working.
       elif hasattr(event, 'long_running_tool_ids') and event.long_running_tool_ids:
         await updater.update_status(
           TaskState.working,
           new_agent_text_message("waiting for tools in background", task.contextId, task.id), 
           final=True,
           )
         break;
```

## Optional Task: Nested Authentication for A2A Agents

A sophisticated A2A agent handles complex scenarios where it requires additional
authentication scopes or separate authentication credentials. This applies when
invoking external APIs, tools, or other A2A agents. In such cases, the agent
intelligently transitions the respective task to an `auth-required` state,
signaling the need for further authentication.

For information on how to capture auth-event for a tool within an ADK agent, see
[Capture auth events within ADK agent](https://github.com/a2a-adk-wrapper/auth-events).

## TaskStore Management for A2A Protocol

The A2A protocol fundamentally operates with Tasks. Therefore, A2A SDKs require
a TaskStore for efficient task management throughout the agent's lifecycle.

## In-Memory TaskStore

The `InMemoryTaskStore` provides an in-memory implementation of a task store.
Use this for local testing. A production A2A server should use persistent
storage.

## Alloy DB for Persistent Storage

{{gcp_name}} Alloy DB can persist A2A tasks. The following is a sample implementation
demonstrating how to integrate an Alloy DB-backed task store into your A2A agent.

To set up your cluster, follow these steps:

1.  Set up the cluster using the [AlloyDB documentation](/alloydb/docs/cluster-create#console).
2.  Postgres is the default database that automatically creates. You have the
   option to create your own database.
3.  Note your username and password for future reference.
4.  Navigate to **Connectivity** in the left panel and note the connection URI.
   For example:
   `projects/{my-project}/locations/us-central1/clusters/{my-cluster}/instances/primary-instance`.

The following code sample demonstrates how to integrate an AlloyDB-backed task
store into your A2A agent:

```python
from a2a.server.tasks import DatabaseTaskStore


import asyncpg
import sqlalchemy
import sqlalchemy.ext.asyncio


from google.cloud.alloydbconnector import AsyncConnector


async def create_sqlalchemy_engine(
   inst_uri: str,
   user: str,
   password: str,
   db: str,
   refresh_strategy: str = "background",
) -> tuple[sqlalchemy.ext.asyncio.engine.AsyncEngine, AsyncConnector]:
   """Creates a connection pool for an AlloyDB instance and returns the pool
   and the connector. Callers are responsible for closing the pool and the
   connector.


   Args:
       instance_uri (str):
           The instance URI specifies the instance relative to the project,
           region, and cluster. For example:
           "projects/my-project/locations/us-central1/clusters/my-cluster/instances/my-instance"
       user (str):
           The database user name, e.g., postgres
       password (str):
           The database user's password, e.g., secret-password
       db (str):
           The name of the database, e.g., mydb
       refresh_strategy (Optional[str]):
           Refresh strategy for the AlloyDB Connector. Can be one of "lazy"
           or "background". For serverless environments use "lazy" to avoid
           errors resulting from CPU being throttled.
   """
   connector = AsyncConnector(refresh_strategy=refresh_strategy)


   # create SQLAlchemy connection pool
   engine = sqlalchemy.ext.asyncio.create_async_engine(
       "postgresql+asyncpg://",
       async_creator=lambda: connector.connect(
           inst_uri,
           "asyncpg",
           user=user,
           password=password,
           db=db,
      # Use PUBLIC, if you have ip_type as public.
           ip_type="PUBLIC",
       ),
       execution_options={"isolation_level": "AUTOCOMMIT"},
   )
   return engine, connector


# Secrets should come from env variables


# DB_INSTANCE will be of format &quot;projects/{my-project}/locations/us-central1/clusters/{my-cluster}/instances/primary-instance&quot;
DB_INSTANCE = os.environ['DB_INSTANCE']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_NAME = os.environ['DB_NAME']


engine, connector = await create_sqlalchemy_engine(
   DB_INSTANCE,
   DB_USER,
   DB_PASS,
   DB_NAME,
)
alloydb_task_store = DatabaseTaskStore(engine)
```

## Advanced Agent Authentication Methods

Beyond foundational service-level authentication, A2A agents implement more
granular and sophisticated authentication mechanisms to secure interactions.

## IAM-Based Authentication for Internal Google Cloud Workloads

For clients and services operating within Google Cloud, such as Agent Space,
IAM-based authentication is a highly secure and efficient method. Configure
these internal clients with appropriate service accounts and grant them the
`roles/run.invoker` IAM role to securely interact with your A2A
Google Cloud service.

## Custom Authentication for Public A2A Agents

If your A2A service is designed for public exposure, implement custom
authentication logic directly within the service itself. In such scenarios,
define and expose the custom authentication's security schemes within the A2A
agent card.

### Sample Custom Authentication Implementation Using JWTAuthBackend

The following code sample shows a custom authentication implementation using a
`JWTAuthBackend`:


```python
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.exceptions import HTTPException
from jose import jwt, JWTError


class JWTAuthBackend(AuthenticationBackend):
 async def authenticate(self, conn):
   if "Authorization" not in conn.headers:
     return


   auth = conn.headers["Authorization"]
   try:
     scheme, credentials = auth.split()
     if scheme.lower() != "bearer":
       return
    
     # Replace 'your-secret-key' with your actual secret key
     # Replace 'your-algorithm' with the algorithm used for signing (e.g., "HS256")
     payload = jwt.decode(credentials, "your-secret-key", algorithms=["your-algorithm"])
     username = payload.get("sub") # "sub" is a common claim for subject (username)
     if username is None:
       raise HTTPException(status_code=401, detail="Invalid authentication credentials")


     # You can fetch user details from a database here if needed
     user = SimpleUser(username) 
     return AuthCredentials(["authenticated"]), user


# DB_INSTANCE will be of format &quot;projects/{my-project}/locations/us-central1/clusters/{my-cluster}/instances/primary-instance&quot;
DB_INSTANCE = os.environ["DB_INSTANCE"]
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_NAME = os.environ["DB_NAME"]


engine, connector = await create_sqlalchemy_engine(
This instance integrates with your defined agent executor and exposes the A2A
APIs using either JSON-RPC or gRPC communication protocols. The application URL
is typically configured through an environment variable, which automatically populates
during the {{cloud_run_name}} deployment process.

The following code sample shows how to construct an A2A server:

```python
facts_agent = LlmAgent(
   name="facts_agent",
   model="gemini-2.5-flash-lite-preview-06-17",
   description=("Agent to give interesting facts."),
   instruction=("You are a helpful agent who can provide interesting facts."),
   tools=[google_search],
)


def make_sync(func):
   @functools.wraps(func)
   def wrapper(*args, **kwargs):
       return asyncio.run(func(*args, **kwargs))
   return wrapper


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
@make_sync
async def main(host, port):
   # Agent card (metadata)
   agent_card = AgentCard(
       name=facts_agent.name,
       description=facts_agent.description,
       url=os.environ["APP_URL"],
       version="1.0.0",
       defaultInputModes=["text", "text/plain"],
       defaultOutputModes=["text", "text/plain"],
       capabilities=AgentCapabilities(streaming=True),
       skills=[
           AgentSkill(
               id="give_facts",
               name="Provide Interesting Facts",
               description="Searches Google for interesting facts",
               tags=["search", "google", "facts"],
               examples=[
                   "Provide an interesting fact about New York City.",
               ],
           )
       ],
   )


   use_alloy_db_str = os.getenv("USE_ALLOY_DB", "False")
   if use_alloy_db_str.lower() == "true":
       DB_INSTANCE = os.environ["DB_INSTANCE"]
       DB_NAME = os.environ["DB_NAME"]
       DB_USER = os.environ["DB_USER"]
       DB_PASS = os.environ["DB_PASS"]


       engine, connector = await create_sqlalchemy_engine(
           DB_INSTANCE,
           DB_USER,
           DB_PASS,
           DB_NAME,
       )
       task_store = DatabaseTaskStore(engine)
   else:
       task_store = InMemoryTaskStore()
       request_handler = DefaultRequestHandler(
       agent_executor=AdkAgentToA2AExecutor(
           agent=facts_agent,
       ),
       task_store=my_task_store,
   )


   a2a_app = A2AStarletteApplication(
       agent_card=agent_card,
       http_handler=request_handler
   )
   routes = a2a_app.routes()

   app = Starlette(
       routes=routes,
       middleware=[
           # Add your auth middleware
           Middleware(AuthenticationMiddleware, backend=JWTAuthBackend())
       ],
   )


   uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
   main()
```

