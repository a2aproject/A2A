# Tutorials

## Python

Tutorial | Description | Difficulty
:--------|:------------|:-----------
[A2A and Python Quickstart](./python/1-introduction.md) | Learn to build a simple Python-based "echo" A2A server and client. | Easy
[ADK facts](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/adk_facts) | Build and test a simple Personal Assistant agent using the Agent Development Kit (ADK) that can provide interesting facts. | Easy
[ADK agent on Cloud Run](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/adk_cloud_run) | Deploy, manage, and observe an ADK-based agent as a scalable, serverless service on Google Cloud Run.| Easy
[Multi-agent collaboration using A2A](https://github.com/a2aproject/a2a-samples/tree/main/demo) | Learn how to set up an orchestrator (host agent) that routes and manages requests among several specialized A2A-compatible agents. | Easy
[Airbnb and weather multi-agent](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/agents/airbnb_planner_multiagent) | Build a complex multi-agent system where agents collaborate using A2A to plan a trip, finding both Airbnb accommodations and weather information. | Medium
[A2A Client-Server example using remote ADK agent](https://goo.gle/adk-a2a) | Learn how a local A2A client agent discovers and consumes the capabilities of a separate, remote ADK-based agent (for example, a prime number checker). | Easy
[Colab Notebook](https://github.com/a2aproject/a2a-samples/blob/main/notebooks/multi_agents_eval_with_cloud_run_deployment.ipynb) | Use Colab Notebook to deploy A2A agents to Cloud Run from your browser, and then evaluate their performance with Vertex AI. | Easy

## Java

Tutorial | Description | Difficulty
:--------|:------------|:-----------
[Weather Agent](https://github.com/a2aproject/a2a-samples/tree/main/samples/java/agents/weather_mcp) | Build a weather information agent using an MCP server.<br><br>**To make use of this agent in a multi-language, multi-agent system, check out the [weather_and_airbnb_planner sample](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/weather_and_airbnb_planner).** | Easy
[Content Writer Agent](https://github.com/a2aproject/a2a-samples/tree/main/samples/java/agents/content_writer) | Build a content writer agent that generates engaging pieces of content from outlines.<br><br>**To make use of this agent in a content creation multi-language, multi-agent system, check out the [content_creation sample](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/content_creation).** | Easy
[Content Editor Agent](https://github.com/a2aproject/a2a-samples/tree/main/samples/java/agents/content_editor) | Build a content editor agent that proof-reads and polishes content.<br><br>**To make use of this agent in a content creation multi-language, multi-agent system, check out the [content_creation sample](https://github.com/a2aproject/a2a-samples/tree/main/samples/python/hosts/content_creation).** | Easy
[Dice Agent (Multi-Transport)](https://github.com/a2aproject/a2a-samples/tree/main/samples/java/agents/dice_agent_multi_transport) | Build a multi-transport agent that rolls dice and checks for prime numbers. | Medium
[Magic 8 Ball Agent (Security)](https://github.com/a2aproject/a2a-samples/tree/main/samples/java/agents/magic_8_ball_security) | Build a Magic 8 Ball agent to learn how to secure A2A servers with Keycloak using bearer token authentication and configure an A2A client to obtain and pass the required token. | Medium

## JavaScript

Tutorial | Description
:--------|:------------
[Movie research agent using JavaScript](https://github.com/a2aproject/a2a-samples/tree/main/samples/js) | Build an A2A agent with Node.js that uses the TMDB (The Movie Database) API to handle movie searches and queries.

## C#/.NET

Tutorial | Description
:--------|:------------
[All .NET samples](https://github.com/a2aproject/a2a-dotnet/tree/main/samples) | Repository of foundational samples showing how to build A2A clients and servers, including an Echo Agent, using the C#/.NET SDK.
