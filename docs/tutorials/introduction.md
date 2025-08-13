
# Get Started with A2A

This guide provides practical guidance and examples to help you get started
with A2A. It covers how the protocol works, supported languages, and how to use
the Python SDK.

## How the A2A Protocol Works

A2A defines how independent AI agent systems interact. It provides
a standardized way for agents to communicate and collaborate.

*   It utilizes JSON-RPC 2.0 over HTTP(S) for structuring and transmitting messages.
*   It allows agents to advertise their capabilities and be found by others through *Agent Cards*.
*   It outlines workflows for initiating, progressing, and completing tasks.
*   It facilitates the exchange of text, files, and structured data.
*   It offers guidelines for secure communication and managing long-running tasks.


## Supported Languages and Code Samples

The A2A Project currently hosts SDKs in four languages (Python, JS, Java, .NET)
and contributors are adding more, including Go.


The following table lists the supported languages and their stability.

| Language | Support  |
| :------- | :------- |
| Python   | [Stable](https://github.com/a2aproject/a2a-python) |
| JS       | [Stable](https://github.com/a2aproject/a2a-js)   |
| Java     | [Stable](https://github.com/a2aproject/a2a-java)   |
| .NET     | [Stable](https://github.com/a2aproject/a2a-dotnet)   |
| Go       | [In Progress](https://github.com/a2aproject/a2a-go) |

The A2A project provides numerous samples across supported languages.

### Python

*   **ADK expense reimbursement agent:** This sample uses the [Agent Development
    Kit (ADK)](/application-integration/docs/agents/about-adk) to create an
    "Expense Reimbursement" agent. The agent hosts
    as an A2A server. This agent takes text requests from the client. If any
    details are missing, it returns a webform for the client or its user to fill
    out. After the client fills out the form, the agent completes the task.


    -   **Prerequisites**

        *   Python 3.9 or higher
        *   UV
        *   Access to an LLM and API Key


    -   **Run the sample**


        1.  Navigate to the samples directory:
            ```bash
            cd samples/python/agents/adk_expense_reimbursement
            ```


        2.  Create an environment file with your API key:
            ```bash
            echo "GEMINI_API_KEY=your_api_key_here" > .env
            ```


        3.  Run an agent:
            ```bash
            uv run .
            ```
        4.  In a separate terminal, run the A2A client:
            ```bash
            cd samples/python/hosts/cli
            uv run . --agent http://localhost:10002
            ```
               If you changed the port when starting the agent, use that port instead.

            For example:

               ```bash
               # Connect to the agent (specify the agent URL with correct port)
               uv run . --agent http://localhost:YOUR_PORT
               ```

    -   For additional Python samples, see the following:
        *   [A2A Samples](https://github.com/a2aproject/a2a-samples/tree/main/samples/python)
        *   [Hello World](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/helloworld)
        *   [ADK agent on Cloud Run](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/adk_cloud_run)
        *   [Airbnb and weather multiagent](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/airbnb_planner_multiagent)

### Java

  *   For a multi-language translator agent using Java, see [Java samples](https://github.com/a2aproject/a2a-samples/tree/main/samples/java).

### JavaScript

  *    For a movie research agent using JavaScript, see [JavaScript samples](https://github.com/a2aproject/a2a-samples/tree/main/samples/js).

### .NET

  *   For all .NET samples, see [.NET samples](https://github.com/a2aproject/a2a-dotnet/tree/main/samples).

## A2A Python SDK 
The A2A Python SDK provides Pydantic models for resources like `AgentSkill`,
`AgentCapabilities`, and `AgentCard`. This provides an interface for expediting
development and integration with the A2A protocol.
An `AgentSkill` advertises a tool to other agents. For example, a currency agent
has a tool for `get_exchange_rate`:

```python
# A2A Agent Skill definition
skill = AgentSkill(
   id='get_exchange_rate',
   name='Currency Exchange Rates Tool',
   description='Helps with exchange values between various currencies',
   tags=['currency conversion', 'currency exchange'],
   examples=['What is exchange rate between USD and GBP?'],
)
```

The Agent Card lists the agent's skills and capabilities. It also includes
additional details like input and output modes that the agent handles:

```python
# A2A Agent Card definition
agent_card = AgentCard(
   name='Currency Agent',
   description='Helps with exchange rates for currencies',
   url=f'http://{host}:{port}/',
   version='1.0.0',
   defaultInputModes=["text"],
   defaultOutputModes=["text"],
   capabilities=AgentCapabilities(streaming=True),
   skills=[skill],
)
```

The `AgentExecutor` interface handles the core logic of how an A2A agent
processes requests and generates responses or events. The A2A Python SDK
provides an abstract base class `a2a.server.agent_execution.AgentExecutor` that
you implement. For more information, see the [A2A GitHub repository](https://github.com/google/a2a).


## Tutorials

*   [Multi-agent collaboration with A2A](./tutorials/python/multi-agent.md):
    This tutorial demonstrates multi-agent collaboration using A2A. You explore
    a prebuilt example featuring a reimbursement agent, developed with the Agent
    Development Kit (ADK).
*   [Writing an A2A agent from scratch - Hello world](./tutorials/python/1-introduction/): This tutorial demonstrates
    how to write an A2A agent from scratch using Python.
