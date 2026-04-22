# x-agent-trust Fixture Sources

Test fixtures for the `x-agent-trust` composite header harness (ref: [#1742](https://github.com/a2aproject/A2A/issues/1742)).

Each fixture source exposes the same 5-field composite schema:

| Field | Type | Description |
|---|---|---|
| `did` | string | W3C Decentralized Identifier |
| `trust_level` | 0-4 | Issuer-specific trust tier |
| `attestation_count` | number | Number of behavioral attestations |
| `last_verified` | ISO 8601 | Most recent verification timestamp |
| `evidence_bundle` | string | Self-describing pointer (`uri:https://...`) to attestation evidence |
| `delegation_chain_root` | string | Self-describing root of authority chain (`uri:...` or `alg:hash`) |

## Sources

| File | Source | Coverage |
|---|---|---|
| `hivecompute.js` | [HiveCompute](https://hivecompute-g2g7.onrender.com) | smsh tier trajectory, attestation accumulation, compression evidence, Carbon Witness (EU AI Act Art.12) |

APS and MolTrust fixture files to follow per agreed fixture division (see [#1742](https://github.com/a2aproject/A2A/issues/1742)).

## Usage

```js
import { fetchFixtures, fetchFixtureByDID, fetchCarbonWitnessFixture } from './fixtures/hivecompute.js';

// All registered agents (22+ in 48h window)
const fixtures = await fetchFixtures();

// Single agent by DID
const fixture = await fetchFixtureByDID('did:hive:your-agent-hexhex');

// Carbon Witness variant (EU AI Act Art.12 compliance fixture)
const carbonFixture = await fetchCarbonWitnessFixture();
```
