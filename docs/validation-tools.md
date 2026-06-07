# Validation Tools

The A2A project provides validation tools for different stages of agent and SDK
development. Use the Inspector for interactive debugging, the Technology
Compatibility Kit (TCK) for protocol conformance, and the Integration Test Kit
(ITK) for cross-SDK integration testing.

| Tool | Best for | Repository |
| :--- | :------- | :--------- |
| A2A Inspector | Inspecting and debugging an A2A server manually | [a2a-inspector](https://github.com/a2aproject/a2a-inspector) |
| A2A TCK | Validating one A2A implementation against protocol requirements | [a2a-tck](https://github.com/a2aproject/a2a-tck) |
| A2A ITK | Validating interoperability across SDKs, versions, and transports | [a2a-itk](https://github.com/a2aproject/a2a-itk) |

## A2A Inspector

The A2A Inspector is a web application for exploring a running A2A server. It is
useful while building or debugging an agent because it can connect to a local
agent, fetch and display the Agent Card, run basic Agent Card validation, send
messages through a chat interface, and show raw JSON-RPC traffic in a debug
console.

Use the Inspector when you want to:

- Confirm that an agent is reachable from a browser-based tool.
- Review the Agent Card returned by the server.
- Send exploratory messages without writing a custom client.
- Inspect request and response payloads during development.

The Inspector is not a full conformance suite. For protocol-level validation,
use the TCK.

## Technology Compatibility Kit

The A2A Technology Compatibility Kit validates a single A2A implementation,
called the System Under Test (SUT), against A2A protocol requirements. It can run
against the transports declared in the agent's `supportedInterfaces` and
currently supports gRPC, JSON-RPC, and HTTP+JSON.

Use the TCK when you want to:

- Validate that an A2A server implements required protocol behavior.
- Exercise a specific transport such as `grpc`, `jsonrpc`, or `http_json`.
- Generate compatibility reports for local review or CI systems.
- Focus validation on requirement levels such as `must`, `should`, or `may`.

### Running the TCK

Install and run the TCK from its repository:

```bash
git clone https://github.com/a2aproject/a2a-tck.git
cd a2a-tck

uv venv
source .venv/bin/activate
uv pip install -e .

./run_tck.py --sut-host http://localhost:9999
```

Run only one transport:

```bash
./run_tck.py --sut-host http://localhost:9999 --transport grpc
```

Run only a specific requirement level:

```bash
./run_tck.py --sut-host http://localhost:9999 --level must
```

The TCK writes reports to the `reports/` directory, including machine-readable
compatibility output, an HTML compatibility report, a pytest HTML report, and
JUnit XML for CI integration.

## Integration Test Kit

The A2A Integration Test Kit validates interoperability across SDK
implementations, SDK versions, and transport combinations. It uses multi-hop
agent traversal scenarios to verify that messages can move through a cluster of
agents using transports such as JSON-RPC, gRPC, and HTTP+JSON.

Use the ITK when you want to:

- Test an SDK against stable reference SDK implementations.
- Validate cross-version behavior before merging SDK changes.
- Exercise multi-agent routing across different transport protocols.
- Run PR-focused or nightly integration suites.
- Publish recurring integration results to the ITK dashboard.

### Running the ITK

Install the ITK from its repository and run the stable integration suite:

```bash
git clone https://github.com/a2aproject/a2a-itk.git
cd a2a-itk

uv run run_tests.py
```

The ITK repository includes stable reference agents, scenario definitions,
runner scripts, a mock notification server, and a dashboard for compatibility
matrix results.

## Choosing a Tool

Use the tools together as the implementation matures:

1. Use the Inspector during development to verify that the server is reachable
   and that request and response payloads look correct.
2. Run the TCK when the server is ready for protocol validation.
3. Add ITK coverage when an SDK or framework needs cross-implementation
   compatibility checks.

The TCK and ITK are complementary. The TCK asks whether one implementation
conforms to A2A protocol requirements. The ITK asks whether multiple
implementations work together across versions, transports, and agent traversal
patterns.

## CI and SDK Integration

For CI pipelines, start with the smallest validation scope that catches the
failure mode you care about:

- Agent implementation repositories can run the TCK against a local test server
    and publish the generated `reports/` artifacts.
- SDK repositories can run ITK scenarios against a "current" SDK checkout and
    stable reference SDK agents.
- Nightly pipelines can run broader ITK matrices and publish metrics for the
    centralized dashboard.

When integrating ITK into an SDK repository, provide:

- An instruction-handling test agent for the SDK.
- Scenario definitions for PR and nightly validation.
- A runner script that checks out the ITK revision, mounts the SDK workspace,
    starts the required agent cluster, and verifies the result artifacts.

See the ITK repository for production integration examples in the Python and Go
SDK repositories.
