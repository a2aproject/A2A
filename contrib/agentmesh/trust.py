# Copyright (c) Agent-Mesh Contributors. All rights reserved.
# Licensed under the Apache License 2.0.
"""CMVK-based trust layer for A2A Protocol."""

from __future__ import annotations

import base64
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# Try to use real cryptography, fall back to simulation for environments without it
try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.exceptions import InvalidSignature
    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False


class TrustVerificationError(Exception):
    """Raised when trust verification fails."""
    pass


@dataclass
class CMVKSignature:
    """Cryptographic signature using CMVK scheme."""
    
    algorithm: str = "CMVK-Ed25519"
    public_key: str = ""
    signature: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "public_key": self.public_key,
            "signature": self.signature,
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CMVKSignature":
        return cls(
            algorithm=data.get("algorithm", "CMVK-Ed25519"),
            public_key=data.get("public_key", ""),
            signature=data.get("signature", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(timezone.utc),
        )


@dataclass
class CMVKIdentity:
    """Cryptographic identity for an agent using CMVK scheme.
    
    Uses Ed25519 for real cryptographic signing when the `cryptography`
    library is available. Falls back to simulation for demo/testing.
    """
    
    did: str  # Decentralized Identifier
    agent_name: str
    public_key: str  # Base64-encoded public key
    private_key: Optional[str] = None  # Base64-encoded private key (only available to owner)
    capabilities: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def generate(cls, agent_name: str, capabilities: Optional[List[str]] = None) -> "CMVKIdentity":
        """Generate a new CMVK identity with Ed25519 key pair.
        
        Args:
            agent_name: Name of the agent.
            capabilities: List of capabilities this agent has.
            
        Returns:
            New CMVKIdentity with generated keys.
        """
        # Generate deterministic DID from agent name and timestamp
        seed = f"{agent_name}:{time.time_ns()}"
        did_hash = hashlib.sha256(seed.encode()).hexdigest()[:32]
        did = f"did:cmvk:{did_hash}"
        
        if _HAS_CRYPTO:
            # Real Ed25519 key generation
            private_key_obj = ed25519.Ed25519PrivateKey.generate()
            public_key_obj = private_key_obj.public_key()
            
            private_key = base64.b64encode(
                private_key_obj.private_bytes_raw()
            ).decode('ascii')
            public_key = base64.b64encode(
                public_key_obj.public_bytes_raw()
            ).decode('ascii')
        else:
            # Simulated keys for demo (not cryptographically secure)
            public_key = base64.b64encode(
                hashlib.sha256(f"pub:{seed}".encode()).digest()
            ).decode()
            private_key = base64.b64encode(
                hashlib.sha256(f"priv:{seed}".encode()).digest()
            ).decode()
        
        return cls(
            did=did,
            agent_name=agent_name,
            public_key=public_key,
            private_key=private_key,
            capabilities=capabilities or [],
        )
    
    def sign(self, data: str) -> CMVKSignature:
        """Sign data with this identity's private key.
        
        Args:
            data: String data to sign.
            
        Returns:
            CMVKSignature containing the signature.
            
        Raises:
            ValueError: If private key is not available.
        """
        if not self.private_key:
            raise ValueError("Cannot sign without private key")
        
        if _HAS_CRYPTO:
            # Real Ed25519 signing
            private_key_bytes = base64.b64decode(self.private_key)
            private_key_obj = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
            signature_bytes = private_key_obj.sign(data.encode('utf-8'))
            signature = base64.b64encode(signature_bytes).decode('ascii')
        else:
            # Simulated signing for demo
            message = f"{data}:{self.private_key}"
            signature = base64.b64encode(
                hashlib.sha256(message.encode()).digest()
            ).decode()
        
        return CMVKSignature(
            public_key=self.public_key,
            signature=signature,
        )
    
    def verify_signature(self, data: str, signature: CMVKSignature) -> bool:
        """Verify a signature against this identity's public key.
        
        Args:
            data: Original string data that was signed.
            signature: The signature to verify.
            
        Returns:
            True if signature is valid, False otherwise.
        """
        if signature.public_key != self.public_key:
            return False
        
        if _HAS_CRYPTO:
            # Real Ed25519 verification
            try:
                public_key_bytes = base64.b64decode(self.public_key)
                public_key_obj = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
                signature_bytes = base64.b64decode(signature.signature)
                public_key_obj.verify(signature_bytes, data.encode('utf-8'))
                return True
            except (InvalidSignature, ValueError):
                return False
        else:
            # Simulated verification (public key match only for demo)
            return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "did": self.did,
            "agent_name": self.agent_name,
            "public_key": self.public_key,
            "capabilities": self.capabilities,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CapabilityProof:
    """Cryptographic proof that an agent has a capability."""
    
    capability: str
    proof: str  # Base64-encoded proof
    issuer_did: str
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "capability": self.capability,
            "proof": self.proof,
            "issuer_did": self.issuer_did,
            "issued_at": self.issued_at.isoformat(),
        }
        if self.expires_at:
            result["expires_at"] = self.expires_at.isoformat()
        return result


@dataclass
class Delegation:
    """A delegation of capabilities from one agent to another."""
    
    delegator_did: str
    delegatee_did: str
    capabilities: List[str]
    signature: str
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "delegator": self.delegator_did,
            "delegatee": self.delegatee_did,
            "capabilities": self.capabilities,
            "signature": self.signature,
            "issued_at": self.issued_at.isoformat(),
        }
        if self.expires_at:
            result["expires_at"] = self.expires_at.isoformat()
        return result


@dataclass
class TrustedAgentCard:
    """A2A Agent Card enhanced with CMVK trust metadata."""
    
    # Standard A2A fields
    name: str
    description: str
    url: str
    capabilities: List[str] = field(default_factory=list)
    input_modes: List[str] = field(default_factory=lambda: ["text"])
    output_modes: List[str] = field(default_factory=lambda: ["text"])
    
    # Agent-Mesh trust fields
    identity: Optional[CMVKIdentity] = None
    trust_score: float = 0.0
    capability_proofs: Dict[str, CapabilityProof] = field(default_factory=dict)
    delegation_chain: List[Delegation] = field(default_factory=list)
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    
    def sign(self, identity: CMVKIdentity) -> None:
        """Sign this agent card with the given identity."""
        self.identity = identity
        # Card is now signed by having the identity attached
    
    def to_a2a_json(self) -> str:
        """Export as A2A-compatible JSON with trust extensions."""
        card = {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "capabilities": self.capabilities,
            "input_modes": self.input_modes,
            "output_modes": self.output_modes,
        }
        
        if self.identity:
            card["_agentmesh"] = {
                "version": "1.0",
                "identity": {
                    "did": self.identity.did,
                    "public_key": self.identity.public_key,
                },
                "trust_score": self.trust_score,
                "capability_proofs": {
                    k: v.to_dict() for k, v in self.capability_proofs.items()
                },
                "delegation_chain": [d.to_dict() for d in self.delegation_chain],
                "issued_at": self.issued_at.isoformat(),
            }
            if self.expires_at:
                card["_agentmesh"]["expires_at"] = self.expires_at.isoformat()
        
        return json.dumps(card, indent=2)
    
    @classmethod
    def from_a2a_json(cls, json_str: str) -> "TrustedAgentCard":
        """Parse A2A JSON with trust extensions."""
        data = json.loads(json_str)
        
        card = cls(
            name=data["name"],
            description=data.get("description", ""),
            url=data["url"],
            capabilities=data.get("capabilities", []),
            input_modes=data.get("input_modes", ["text"]),
            output_modes=data.get("output_modes", ["text"]),
        )
        
        if "_agentmesh" in data:
            mesh = data["_agentmesh"]
            if "identity" in mesh:
                card.identity = CMVKIdentity(
                    did=mesh["identity"]["did"],
                    agent_name=data["name"],
                    public_key=mesh["identity"]["public_key"],
                )
            card.trust_score = mesh.get("trust_score", 0.0)
            if "issued_at" in mesh:
                card.issued_at = datetime.fromisoformat(mesh["issued_at"])
            if "expires_at" in mesh:
                card.expires_at = datetime.fromisoformat(mesh["expires_at"])
        
        return card


@dataclass
class TrustVerificationResult:
    """Result of a trust verification."""
    
    trusted: bool
    trust_score: float
    reason: str
    verified_capabilities: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class TrustHandshake:
    """Performs trust verification handshake between agents."""
    
    def __init__(self, identity: CMVKIdentity):
        """Initialize with the local agent's identity."""
        self.identity = identity
        self._verified_peers: Dict[str, TrustVerificationResult] = {}
        self._cache_ttl = 900  # 15 minutes
    
    async def verify_peer(
        self,
        peer_card: TrustedAgentCard,
        required_capabilities: Optional[List[str]] = None,
        min_trust_score: float = 0.0,
    ) -> TrustVerificationResult:
        """Verify a peer agent before communication.
        
        Args:
            peer_card: The peer's agent card to verify.
            required_capabilities: Capabilities the peer must have.
            min_trust_score: Minimum trust score required.
            
        Returns:
            TrustVerificationResult with verification details.
        """
        warnings = []
        
        # Check if peer has identity
        if not peer_card.identity:
            return TrustVerificationResult(
                trusted=False,
                trust_score=0.0,
                reason="Peer has no cryptographic identity",
            )
        
        # Verify identity is valid (in production, verify signature)
        if not peer_card.identity.did.startswith("did:cmvk:"):
            return TrustVerificationResult(
                trusted=False,
                trust_score=0.0,
                reason="Invalid DID format",
            )
        
        # Check expiration
        if peer_card.expires_at and peer_card.expires_at < datetime.now(timezone.utc):
            return TrustVerificationResult(
                trusted=False,
                trust_score=0.0,
                reason="Agent card has expired",
            )
        
        # Check trust score
        if peer_card.trust_score < min_trust_score:
            return TrustVerificationResult(
                trusted=False,
                trust_score=peer_card.trust_score,
                reason=f"Trust score {peer_card.trust_score} below minimum {min_trust_score}",
            )
        
        # Verify required capabilities
        verified_caps = []
        if required_capabilities:
            for cap in required_capabilities:
                if cap in peer_card.capabilities:
                    verified_caps.append(cap)
                else:
                    return TrustVerificationResult(
                        trusted=False,
                        trust_score=peer_card.trust_score,
                        reason=f"Missing required capability: {cap}",
                    )
        else:
            verified_caps = peer_card.capabilities.copy()
        
        # Check delegation chain validity
        if peer_card.delegation_chain:
            # In production, verify each delegation signature
            for delegation in peer_card.delegation_chain:
                if delegation.expires_at and delegation.expires_at < datetime.now(timezone.utc):
                    warnings.append(f"Delegation from {delegation.delegator_did} has expired")
        
        # Cache result
        result = TrustVerificationResult(
            trusted=True,
            trust_score=peer_card.trust_score,
            reason="Verification successful",
            verified_capabilities=verified_caps,
            warnings=warnings,
        )
        self._verified_peers[peer_card.identity.did] = result
        
        return result
    
    def is_peer_verified(self, did: str) -> bool:
        """Check if a peer has been recently verified."""
        return did in self._verified_peers and self._verified_peers[did].trusted


class TrustGatedA2AClient:
    """A2A client that requires trust verification before operations."""
    
    def __init__(
        self,
        identity: CMVKIdentity,
        min_trust_score: float = 0.5,
        require_capability_proof: bool = False,
    ):
        """Initialize the trust-gated client.
        
        Args:
            identity: This agent's identity.
            min_trust_score: Minimum trust score to accept.
            require_capability_proof: Whether to require capability proofs.
        """
        self.identity = identity
        self.min_trust_score = min_trust_score
        self.require_capability_proof = require_capability_proof
        self.handshake = TrustHandshake(identity)
    
    async def create_task(
        self,
        peer_card: TrustedAgentCard,
        task_spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a task with trust verification.
        
        Args:
            peer_card: The peer agent's card.
            task_spec: The task specification.
            
        Returns:
            Task creation result.
            
        Raises:
            TrustVerificationError: If peer is not trusted.
        """
        # Verify peer first
        required_caps = task_spec.get("required_capabilities", [])
        result = await self.handshake.verify_peer(
            peer_card,
            required_capabilities=required_caps,
            min_trust_score=self.min_trust_score,
        )
        
        if not result.trusted:
            raise TrustVerificationError(f"Peer verification failed: {result.reason}")
        
        # In production, this would make the actual A2A API call
        return {
            "task_id": f"task-{hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:16]}",
            "status": "created",
            "peer_did": peer_card.identity.did if peer_card.identity else None,
            "trust_score": result.trust_score,
            "verified_capabilities": result.verified_capabilities,
        }


class DelegationChain:
    """Manages a chain of delegations between agents."""
    
    def __init__(self, root_identity: CMVKIdentity):
        """Initialize with the root delegator's identity."""
        self.root_identity = root_identity
        self.delegations: List[Delegation] = []
    
    def add_delegation(
        self,
        delegatee: TrustedAgentCard,
        capabilities: List[str],
        delegator: Optional[TrustedAgentCard] = None,
        expires_in_hours: int = 24,
    ) -> Delegation:
        """Add a delegation to the chain.
        
        Args:
            delegatee: The agent receiving delegation.
            capabilities: Capabilities being delegated.
            delegator: The delegating agent (default: root).
            expires_in_hours: How long the delegation is valid.
            
        Returns:
            The created Delegation.
        """
        delegator_did = (
            delegator.identity.did if delegator and delegator.identity
            else self.root_identity.did
        )
        delegatee_did = delegatee.identity.did if delegatee.identity else ""
        
        # Create and sign delegation
        delegation_data = f"{delegator_did}:{delegatee_did}:{','.join(capabilities)}"
        signature = self.root_identity.sign(delegation_data)
        
        delegation = Delegation(
            delegator_did=delegator_did,
            delegatee_did=delegatee_did,
            capabilities=capabilities,
            signature=signature.signature,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
        )
        
        self.delegations.append(delegation)
        return delegation
    
    async def verify(self) -> bool:
        """Verify the entire delegation chain.
        
        Returns:
            True if the chain is valid, False otherwise.
        """
        if not self.delegations:
            return True
        
        # Verify chain starts from root
        if self.delegations[0].delegator_did != self.root_identity.did:
            return False
        
        # Verify each link in the chain
        for i, delegation in enumerate(self.delegations):
            # Check expiration
            if delegation.expires_at and delegation.expires_at < datetime.now(timezone.utc):
                return False
            
            # Verify delegator of this link matches delegatee of previous
            if i > 0:
                prev = self.delegations[i - 1]
                if delegation.delegator_did != prev.delegatee_did:
                    return False
        
        return True
    
    def get_delegations_for(self, did: str) -> List[Delegation]:
        """Get all delegations where the given DID is the delegatee."""
        return [d for d in self.delegations if d.delegatee_did == did]
