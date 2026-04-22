/**
 * fixtures/hivecompute.js
 *
 * HiveCompute fixture source for the x-agent-trust composite header test harness.
 * Third data source alongside APS and MolTrust.
 *
 * Leaderboard endpoint: https://hivecompute-g2g7.onrender.com/v1/compute/smsh/leaderboard
 * Verify endpoint:      https://hivecompute-g2g7.onrender.com/v1/compute/smsh/verify/:did
 *
 * Schema mapping (HiveCompute → 5-field composite):
 *   did               → did                      (W3C DID, did:hive: method)
 *   smsh_tier         → trust_level              (smsh=1, smsh_enterprise=2, smsh_scale=3)
 *   total_jobs        → attestation_count        (inference jobs as behavioral attestations)
 *   last_seen         → last_verified            (ISO 8601 timestamp)
 *   compression_ratio → evidence_bundle          (uri: pointer to live benchmark evidence)
 *
 * delegation_chain_root: HiveCompute uses a mint → smsh-register two-step chain.
 * Root is the HiveGate onboard event (DID issuance). Expressed as uri: pointer
 * to the verify endpoint, which resolves the full chain.
 *
 * Fixture coverage (per agreed division):
 *   - smsh tier trajectory: unregistered (0) → smsh (1) → smsh_enterprise (2) → smsh_scale (3)
 *   - attestation accumulation: agents at 0, low, and high job counts
 *   - compression evidence: live benchmark at /v1/compute/benchmark
 *   - Carbon Witness variant: EU AI Act Art.12 compliance flag in evidence_bundle
 */

const LEADERBOARD_URL = 'https://hivecompute-g2g7.onrender.com/v1/compute/smsh/leaderboard';
const VERIFY_URL      = 'https://hivecompute-g2g7.onrender.com/v1/compute/smsh/verify';
const BENCHMARK_URL   = 'https://hivecompute-g2g7.onrender.com/v1/compute/benchmark';
const CARBON_URL      = 'https://hivecompute-g2g7.onrender.com/v1/witness/carbon';

/**
 * smsh_tier → trust_level mapping (0-4 scale).
 * Hoisted to module scope — created once, not on every call.
 * Mirrors the trust level progression used by APS and MolTrust.
 */
const TIER_TRUST_MAP = {
  'unregistered':    0,
  'smsh':            1,
  'smsh_enterprise': 2,
  'smsh_scale':      3,
};

/**
 * Map HiveCompute smsh_tier string to trust_level integer (0-4 scale).
 * Mirrors the trust level progression used by APS and MolTrust.
 */
function tierToTrustLevel(smshTier) {
  return TIER_TRUST_MAP[smshTier] ?? 0;
}

/**
 * Build a self-describing delegation_chain_root value.
 * HiveCompute chain: HiveGate onboard (DID issuance) → HiveCompute smsh/register.
 * Root is expressed as a uri: pointer to the verify endpoint (resolves the full chain).
 * Format matches the agreed `"alg:hash"` / `"uri:https://..."` convention.
 */
function buildDelegationChainRoot(did) {
  return `uri:${VERIFY_URL}/${encodeURIComponent(did)}`;
}

/**
 * Build evidence_bundle pointer for a given agent.
 * Points to the live benchmark, which carries HMAC-stamped compression evidence
 * verifiable per-call — the same evidence source the Carbon Witness reads.
 * Format: uri: pointer (self-describing, no schema lookup needed).
 */
function buildEvidenceBundle(did, compressionRatio) {
  // For agents with jobs: point to their verify record (has live compression stats)
  // For agents with no jobs yet: point to the network benchmark
  if (compressionRatio > 0) {
    return `uri:${VERIFY_URL}/${encodeURIComponent(did)}`;
  }
  return `uri:${BENCHMARK_URL}`;
}

/**
 * Fetch the live leaderboard and return all agents as composite header fixtures.
 *
 * @returns {Promise<Array>} Array of composite header objects, one per registered agent.
 */
async function fetchFixtures() {
  const res = await fetch(LEADERBOARD_URL);
  if (!res.ok) {
    throw new Error(`HiveCompute leaderboard returned ${res.status}`);
  }
  const data = await res.json();
  const agents = data.agents ?? [];

  return agents.map(agent => ({
    // ── 5-field composite header ───────────────────────────────────────────────
    did: agent.did,

    trust_level: tierToTrustLevel(agent.smsh_tier),

    attestation_count: agent.total_jobs ?? 0,

    last_verified: agent.last_seen ?? agent.smsh_at,

    evidence_bundle: buildEvidenceBundle(agent.did, agent.compression_ratio ?? 0),

    delegation_chain_root: buildDelegationChainRoot(agent.did),

    // ── HiveCompute-specific fields (fixture metadata, not part of header) ────
    _hivecompute: {
      smsh_name:        agent.smsh_name,
      smsh_tier:        agent.smsh_tier,
      compression_ratio:agent.compression_ratio ?? 0,
      total_saved_usdc: agent.total_saved_usdc ?? 0,
      spread_pct:       agent.spread_pct ?? 25,
      rank:             agent.rank,
      verify_url:       `${VERIFY_URL}/${encodeURIComponent(agent.did)}`,
    },
  }));
}

/**
 * Fetch a single agent's composite header fixture by DID.
 * Resolves through /v1/compute/smsh/verify/:did for a live verified record.
 *
 * @param {string} did  - A did:hive: identifier
 * @returns {Promise<Object>} Single composite header object
 */
async function fetchFixtureByDID(did) {
  const res = await fetch(`${VERIFY_URL}/${encodeURIComponent(did)}`);
  if (!res.ok) {
    throw new Error(`HiveCompute verify returned ${res.status} for ${did}`);
  }
  const agent = await res.json();

  return {
    did: agent.did,
    trust_level:          tierToTrustLevel(agent.smsh_tier),
    attestation_count:    agent.stats?.total_jobs ?? 0,
    last_verified:        agent.last_seen ?? agent.smsh_at,
    evidence_bundle:      buildEvidenceBundle(agent.did, agent.stats?.compression_ratio ?? 0),
    delegation_chain_root:buildDelegationChainRoot(agent.did),
    _hivecompute: {
      smsh_name:        agent.smsh_name,
      smsh_tier:        agent.smsh_tier,
      verified:         agent.verified,
      compression_ratio:agent.stats?.compression_ratio ?? 0,
      total_saved_usdc: agent.stats?.total_saved_usdc ?? 0,
      verify_url:       `${VERIFY_URL}/${encodeURIComponent(agent.did)}`,
    },
  };
}

/**
 * Return the Carbon Witness fixture variant.
 * Agents with EU AI Act Art.12 compliance documentation carry a carbon_witness
 * flag in their evidence_bundle — relevant for enterprise verifiers with
 * environmental impact requirements.
 *
 * @returns {Promise<Object>} Carbon Witness network stats + fixture shape
 */
async function fetchCarbonWitnessFixture() {
  const res = await fetch(CARBON_URL);
  if (!res.ok) {
    throw new Error(`Carbon Witness endpoint returned ${res.status}`);
  }
  const carbon = await res.json();

  return {
    // This is a network-level fixture, not per-agent — represents the
    // HiveCompute network's aggregate carbon evidence for the 48h window
    did:              'did:hive:network-carbon-witness',
    trust_level:      1,
    attestation_count:carbon.network?.jobs_measured ?? 0,
    last_verified:    carbon.timestamp,
    evidence_bundle:  `uri:${CARBON_URL}`,
    delegation_chain_root: buildDelegationChainRoot('did:hive:network-carbon-witness'),
    _hivecompute: {
      smsh_name:             'HiveCompute-CarbonWitness.smsh',
      smsh_tier:             'smsh',
      tokens_saved_cumulative: carbon.network?.tokens_saved_cumulative ?? 0,
      co2_kg_avoided:        carbon.network?.co2_kg_avoided_cumulative ?? 0,
      eu_ai_act_article_12:  carbon.compliance?.eu_ai_act_article_12 ?? 'UNKNOWN',
      carbon_url:            CARBON_URL,
    },
  };
}

/**
 * consumer-verify.ts integration.
 *
 * The W3C VC chain resolves through the verify endpoint.
 * A verifier that can handle APS and MolTrust JWKS-based verification
 * can verify HiveCompute DIDs with the same fetch-JWKS + ES256-verify pipeline:
 *
 *   const fixture   = await fetchFixtureByDID(did);
 *   const verifyRes = await fetch(fixture._hivecompute.verify_url);
 *   const record    = await verifyRes.json();
 *   assert(record.verified === true);
 *   assert(record.smsh === true);
 *
 * HiveCompute does not use JWKS-signed JWTs in the current implementation —
 * verification is endpoint-based (the verify endpoint IS the trust anchor).
 * For schema-compatible JWKS integration, track:
 *   https://github.com/srotzin/hivecompute/issues (JWKS endpoint roadmap)
 */

module.exports = {
  fetchFixtures,
  fetchFixtureByDID,
  fetchCarbonWitnessFixture,
  tierToTrustLevel,
  buildDelegationChainRoot,
  buildEvidenceBundle,
};
