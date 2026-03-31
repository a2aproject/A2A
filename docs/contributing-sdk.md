# Contributing an SDK

This guide covers how to build, test, and verify a community A2A SDK.

!!! note "Verification infrastructure is in active development"
    The [A2A TCK](https://github.com/a2aproject/a2a-tck) is being overhauled on the `1.0-dev` branch to support the v1.0 specification. The [ITK](https://github.com/a2aproject/a2a-samples/tree/main/itk) is a new addition for cross-SDK interop testing. Verification badges on the [Community SDKs](./community-sdks.md) page will be added once these stabilize.

## Building Your SDK

1. Read the [A2A v1.0 Specification](https://a2a-protocol.org/latest/specification/)
2. Study the [Python SDK](https://github.com/a2aproject/a2a-python) as the reference implementation
3. Open a [Discussion](https://github.com/a2aproject/A2A/discussions) to signal intent and get early feedback

### What to Implement

At minimum, a community SDK should cover:

- **Agent Card** — serve a valid `AgentCard` at `/.well-known/agent.json`
- **Task Lifecycle** — `tasks/send`, `tasks/get`, `tasks/cancel` with correct state transitions
- **Streaming** — `tasks/sendSubscribe` with Server-Sent Events (SSE)
- **JSON-RPC 2.0** — proper request/response/error envelope format

Additional features to consider:

- Multiple transports (gRPC, HTTP+JSON/REST)
- Push notifications
- Authentication schemes
- Task storage backends

## Getting Listed

See the [Community SDKs](./community-sdks.md) page for listing requirements. To add your SDK:

1. Ensure it meets the [minimum criteria](./community-sdks.md#requirements-for-listing)
2. Open an issue on [a2aproject/A2A](https://github.com/a2aproject/A2A/issues) with:
    - Link to your repository
    - Link to published package
    - Brief description of feature coverage
3. A maintainer will review and merge the listing

## Verifying with the TCK

The [A2A TCK](https://github.com/a2aproject/a2a-tck) (Technology Compatibility Kit) validates protocol compliance through automated tests.

### How It Works

1. **Build a SUT (System Under Test)** — a minimal A2A server using your SDK
2. **The TCK sends requests** with specific `messageId` prefixes that signal expected behavior (e.g., prefix `tck-complete-task` → complete with a response message)
3. **The TCK validates** responses match the specification

### Running the TCK

```bash
git clone https://github.com/a2aproject/a2a-tck.git
cd a2a-tck
uv venv && source .venv/bin/activate && uv pip install -e .

# Start your SUT agent, then:
./run_tck.py --sut-host http://localhost:9999
```

### TCK Compliance Levels

| Level | Criteria | Meaning |
|-------|----------|---------|
| 🔴 Non-Compliant | Any mandatory failure | Not A2A compliant |
| 🟡 Mandatory | 100% mandatory pass | Core compliance |
| 🟢 Recommended | + capabilities ≥85%, quality ≥75% | Production-ready |
| 🏆 Full | All categories at threshold | Complete implementation |

### Submitting Your SUT

Once your SDK passes, contribute it back:

1. Add your SUT under `sut/<sdk-name>/` in the TCK repo
2. Include build and run scripts (see `sut/a2a-python/` for reference)
3. Submit a PR to [`a2aproject/a2a-tck`](https://github.com/a2aproject/a2a-tck)

The TCK's `1.0-dev` branch also includes a **codegen** system that auto-generates SUT code from Gherkin scenarios. Python and Java emitters exist — contributing an emitter for your language is a great way to help the ecosystem.

## Verifying with the ITK

The [ITK](https://github.com/a2aproject/a2a-samples/tree/main/itk) (Integration Testing Kit) validates cross-SDK interoperability through multi-hop agent chains.

### How It Works

The ITK dispatches a nested instruction through a chain of agents built with different SDKs. Each hop:

1. Resolves the next agent's card
2. Maps the requested transport (JSON-RPC, gRPC, or REST)
3. Forwards the remaining instructions

This proves your SDK can discover, call, and be called by agents built with other SDKs.

### Adding Your SDK to the ITK

1. Implement an ITK agent in `itk/agents/<language>/v10/`
2. The agent must support configurable ports and respond to traversal instructions
3. Update `run_tests.py` to include your agent in the hop chain
4. Submit a PR to [`a2aproject/a2a-samples`](https://github.com/a2aproject/a2a-samples)

See `itk/agents/python/v10/` and `itk/agents/go/v10/` for reference implementations.

## Verification Badges

Community SDKs that pass verification earn badges on the [Community SDKs](./community-sdks.md) page:

| Badge | Meaning | How to Earn |
|-------|---------|-------------|
| ✅ TCK Mandatory | Passes all mandatory TCK tests | SUT merged in `a2a-tck`, passes `--category mandatory` |
| 🟢 TCK Recommended | Production-ready compliance | Higher TCK compliance level |
| 🏆 TCK Full | Complete compliance | All TCK categories at threshold |
| 🔗 ITK Verified | Cross-SDK interop demonstrated | Agent merged in `a2a-samples/itk/` |

!!! info "Badge availability"
    Badges will be awarded once the TCK `1.0-dev` branch is merged to `main` and the ITK agent contribution process is formalized. In the meantime, SDKs are listed with self-reported compliance.

## Advancement Path

| Status | What It Means |
|--------|--------------|
| **Listed** | Meets minimum requirements, self-reported compliance |
| **TCK Verified** | Passes TCK mandatory + capabilities |
| **ITK Verified** | Cross-SDK interop via ITK multi-hop testing |
| **Official** | TSC approval, sustained maintenance, repo under `a2aproject` |

Promotion to official status requires a sustained maintenance track record, verified compliance, and TSC review.
