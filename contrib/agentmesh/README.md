# Agent-Mesh Trust Layer for A2A Protocol

Cryptographic identity verification and trust scoring for A2A agent communications using [Agent-Mesh](https://github.com/imran-siddique/agent-mesh).

## Overview

A2A enables agent-to-agent communication, but doesn't specify how agents should verify each other's identity or establish trust. This contribution adds:

- **CMVK-Enhanced Agent Cards**: Cryptographically signed Agent Cards with verifiable identity
- **Trust Verification**: Pre-task trust handshake between agents
- **Capability Attestation**: Cryptographic proof of agent capabilities
- **Delegation Chains**: Verifiable delegation with trust propagation

## Why Trust Matters for A2A

When Agent A delegates a task to Agent B:
1. How does A know B is who it claims to be?
2. How does A know B can actually perform the task?
3. How does A verify B hasn't been compromised?

Agent-Mesh provides cryptographic answers to all three questions.

## Installation

```bash
pip install agentmesh-a2a
# or
pip install agent-mesh[a2a]
```

## Quick Start

### Creating a Trusted Agent Card

```python
from agentmesh.a2a import TrustedAgentCard, CMVKIdentity

# Create cryptographic identity
identity = CMVKIdentity.generate(
    agent_name="research-agent",
    capabilities=["web_search", "summarization", "citation"]
)

# Create A2A Agent Card with CMVK signature
agent_card = TrustedAgentCard(
    name="research-agent",
    description="Expert research assistant",
    url="https://agents.example.com/research",
    identity=identity,
    
    # Standard A2A fields
    capabilities=["web_search", "summarization"],
    input_modes=["text"],
    output_modes=["text", "file"],
)

# Export for A2A discovery
card_json = agent_card.to_a2a_json()
```

### Verifying a Peer Before Task Delegation

```python
from agentmesh.a2a import TrustHandshake, TrustedAgentCard, CMVKIdentity

# Generate your identity (or load existing)
my_identity = CMVKIdentity.generate("my-agent", capabilities=["coordination"])

# Load peer's agent card (from A2A discovery)
peer_card = TrustedAgentCard.from_a2a_json(peer_card_json)

# Verify before delegating task
handshake = TrustHandshake(my_identity)
result = await handshake.verify_peer(peer_card)

if result.trusted:
    print(f"Peer verified! Trust score: {result.trust_score}")
    # Safe to delegate task via your A2A client
else:
    print(f"Verification failed: {result.reason}")
    # Don't delegate to untrusted agent
```

### Trust-Gated Task Creation

```python
from agentmesh.a2a import TrustGatedA2AClient, CMVKIdentity

# Generate your identity
my_identity = CMVKIdentity.generate("coordinator", capabilities=["task-delegation"])

# Create client with trust requirements
client = TrustGatedA2AClient(
    identity=my_identity,
    min_trust_score=0.7,
    require_capability_proof=True,
)

# Task creation requires a TrustedAgentCard (obtained from discovery)
peer_card = TrustedAgentCard.from_a2a_json(discovered_agent_json)

try:
    task = await client.create_task(
        peer_card=peer_card,
        task_spec={
            "description": "Write a report on AI safety",
            "required_capabilities": ["writing", "research"],
        }
    )
except TrustVerificationError as e:
    print(f"Agent not trusted: {e}")
```

## CMVK-Enhanced Agent Card Schema

Standard A2A Agent Card extended with trust fields:

```json
{
    "name": "research-agent",
    "description": "Expert research assistant",
    "url": "https://agents.example.com/research",
    "capabilities": ["web_search", "summarization"],
    "input_modes": ["text"],
    "output_modes": ["text", "file"],
    
    "_agentmesh": {
        "version": "1.0",
        "identity": {
            "did": "did:cmvk:abc123...",
            "public_key": "-----BEGIN PUBLIC KEY-----...",
            "signature": "base64-encoded-signature"
        },
        "trust_score": 0.95,
        "capability_proofs": {
            "web_search": "base64-proof-of-capability",
            "summarization": "base64-proof-of-capability"
        },
        "delegation_chain": [
            {
                "delegator": "did:cmvk:root...",
                "delegatee": "did:cmvk:abc123...",
                "capabilities": ["web_search", "summarization"],
                "signature": "base64-delegation-signature"
            }
        ],
        "issued_at": "2026-02-05T23:00:00Z",
        "expires_at": "2026-02-06T23:00:00Z"
    }
}
```

## Integration with A2A Flows

### 1. Agent Discovery with Trust

```python
from agentmesh.a2a import TrustHandshake, TrustedAgentCard, CMVKIdentity

# Your identity
my_identity = CMVKIdentity.generate("coordinator", capabilities=["discovery"])

# When you receive agent cards from A2A discovery, verify them
handshake = TrustHandshake(my_identity)

# Filter discovered agents by trust
async def filter_trusted_agents(discovered_cards, min_trust=0.8):
    trusted = []
    for card_json in discovered_cards:
        card = TrustedAgentCard.from_a2a_json(card_json)
        result = await handshake.verify_peer(card, min_trust_score=min_trust)
        if result.trusted:
            trusted.append(card)
    return trusted

# Discover agents with trust filtering
trusted_agents = await filter_trusted_agents(
    discovered_cards,
    min_trust=0.8,
)
```

### 2. Task Delegation with Verification

```python
from agentmesh.a2a import TrustGatedA2AClient, CMVKIdentity, TrustedAgentCard

# Your identity
my_identity = CMVKIdentity.generate("delegator", capabilities=["coordination"])

# Create trust-gated client
client = TrustGatedA2AClient(
    identity=my_identity,
    min_trust_score=0.7,
)

# Load peer's card (from discovery)
writer_card = TrustedAgentCard.from_a2a_json(writer_agent_json)

# Delegate with automatic trust verification
result = await client.create_task(
    peer_card=writer_card,
    task_spec={
        "description": "Write summary",
        "input": document,
    },
)
```

### 3. Multi-Hop Delegation

```python
from agentmesh.a2a import DelegationChain, CMVKIdentity, TrustedAgentCard

# Identities for each agent in the chain
my_identity = CMVKIdentity.generate("coordinator")
research_identity = CMVKIdentity.generate("researcher")

# Agent cards (with identities)
research_agent_card = TrustedAgentCard(
    name="Research Agent",
    description="Performs research",
    url="https://example.com/research",
    capabilities=["research"],
)
research_agent_card.sign(research_identity)

writer_agent_card = TrustedAgentCard(
    name="Writer Agent",
    description="Writes content",
    url="https://example.com/writer",
    capabilities=["writing"],
)

# Create delegation chain: Me -> Research Agent -> Writer Agent
chain = DelegationChain(my_identity)

# Root delegates to research agent
chain.add_delegation(
    delegatee=research_agent_card,
    capabilities=["research", "delegate_writing"],
)

# Research agent delegates to writer (requires research agent's identity)
chain.add_delegation(
    delegator=research_agent_card,
    delegatee=writer_agent_card,
    capabilities=["writing"],
    delegator_identity=research_identity,  # Sign with delegator's key
)

# Verify entire chain
is_valid = await chain.verify()
```

## Security Considerations

1. **Key Management**: CMVK keys should be stored securely (HSM, secure enclave)
2. **Expiration**: Agent Cards should have short expiration times
3. **Revocation**: Check revocation status before trusting
4. **Capability Scope**: Only delegate minimum required capabilities

## Links

- [Agent-Mesh GitHub](https://github.com/imran-siddique/agent-mesh)
- [A2A Protocol Specification](https://github.com/a2aproject/A2A)
