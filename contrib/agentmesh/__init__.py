# Copyright (c) Agent-Mesh Contributors. All rights reserved.
# Licensed under the Apache License 2.0.
"""Agent-Mesh Trust Layer for A2A Protocol.

Provides cryptographic identity verification and trust scoring
for A2A agent-to-agent communications.
"""

from .trust import (
    CMVKIdentity,
    CMVKSignature,
    TrustedAgentCard,
    TrustHandshake,
    TrustVerificationResult,
    TrustGatedA2AClient,
    DelegationChain,
    TrustVerificationError,
)

__all__ = [
    "CMVKIdentity",
    "CMVKSignature",
    "TrustedAgentCard",
    "TrustHandshake",
    "TrustVerificationResult",
    "TrustGatedA2AClient",
    "DelegationChain",
    "TrustVerificationError",
]

__version__ = "0.1.0"
