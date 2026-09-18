# Content Integrity Profile: jcs_depth_v1 conformance vectors

## What this corpus pins

`jcs_edge_v1` pins the bytes an RFC 8785 canonicalizer must produce. This corpus pins the input it must refuse.

RFC 8785 specifies escaping, number form and property ordering, and it specifies no limit on how deeply an input may nest. That omission is deliberate and it is not a defect in the RFC, but it leaves a profile built on JCS with a gap the byte-level vectors cannot reach. Two implementations that agree on all ten `jcs_edge_v1` vectors can still disagree about whether a deeply nested artifact canonicalizes at all: one returns bytes, one returns an error, and one walks off the end of its call stack. All three are conformant to RFC 8785, so the profile has to state the bound itself or inherit whichever bound each implementation happened to pick.

The gap has teeth because canonicalization runs before signature verification. A verifier has to canonicalize a received artifact to know what bytes the signature covers, so the recursive walk is reachable by anyone who can hand the verifier an artifact, with no key and no prior trust. A canonicalizer that recurses once per nesting level and carries no depth counter exhausts its stack on such input. In a compiled runtime that is not an exception a caller can catch: Go reports `fatal error: stack overflow` and unwinds the process, and a deferred `recover` does not intercept it. The widely used Go implementation `gowebpki/jcs` is built this way, with a recursive descent through `parseElement`, `parseObject` and `parseArray` and no depth counter on any path; measured on one machine, about 10^5 levels canonicalize normally and about 10^7 levels, roughly 20 MB of brackets, kill the process. A byte cap does not close this, because pure nesting stays small per level and reaches any plausible size limit long after it has passed any plausible stack. The bound has to be checked before the walk begins.

## The bound

Depth counts **open containers**. The outermost brace or bracket is depth 1, and every object or array opened inside it adds one, an empty container included.

The counting rule matters as much as the number. A counter that charges a level when it recurses into a child, rather than when a container opens, never charges an empty container and lands one level off. Two implementations can hold the identical constant and still disagree across the boundary, which is the failure `jcs-depth-004` and `jcs-depth-103` exist to separate.

The bound in this corpus is **128**. It is the same figure and the same counting rule stated in the predicate specification proposed in [in-toto/attestation#570](https://github.com/in-toto/attestation/pull/570), where it was chosen on two grounds: it is the recursion limit `serde_json` already enforces, and it sits far above real content. The deepest artifact in the corpus that prompted it nests seven levels.

## The vectors

| vector | outcome | depth | what it separates |
| --- | --- | --- | --- |
| `jcs-depth-001-object-at-bound` | accept | 128 | the deepest input the bound admits, in objects |
| `jcs-depth-002-array-at-bound` | accept | 128 | the same boundary in the array branch |
| `jcs-depth-003-alternating-at-bound` | accept | 128 | a counter that tracks one container kind and resets on the other |
| `jcs-depth-004-empty-object-leaf-at-bound` | accept | 128 | an empty container counted as its own level |
| `jcs-depth-101-object-one-past-bound` | reject | 129 | one wrapping object past `jcs-depth-001` |
| `jcs-depth-102-array-one-past-bound` | reject | 129 | one wrapping array past `jcs-depth-002` |
| `jcs-depth-103-empty-object-leaf-one-past-bound` | reject | 129 | a per-child counter, which accepts this and rejects `jcs-depth-101` |
| `jcs-depth-104-unbounded-recursion` | reject | 10000000 | a refusal from a crash |

Four `pair_invariants` in the corpus state the relations the individual vectors cannot: each accept and its one-level-deeper reject locate the boundary exactly, since an implementation that accepts both has no bound and one that rejects both has the bound off by one. `jcs-depth-104` is passed only when the implementation returns a rejection to its caller. A process that dies on that input has not rejected it.

## How to run

Preimages are given as nesting rules rather than literal JSON, so this file stays four levels deep and can be read by a parser that enforces the bound it describes. Materialize a rule, then check the corpus against your canonicalizer:

1. For `i` from 0 to `count - 1`, emit the opener for `containers[i % len(containers)]`: `{"a":` for `object`, `[` for `array`.
2. Emit `leaf`, then the matching closers innermost first.
3. Compute SHA-256 over the materialized UTF-8 bytes and compare against `preimage_sha256`. Do this before canonicalizing anything. A vector built wrong cross-checks cleanly against itself and proves nothing.
4. For an `accept` vector, canonicalize the preimage, compare the bytes exactly against the base64-decoded `expected_jcs_bytes_b64`, and compare SHA-256 of those bytes against `expected_sha256`.
5. For a `reject` vector, confirm your canonicalizer returns a rejection to the caller. No canonical bytes are published for these: an implementation that produces bytes here has not applied the bound.

Every `expected_jcs_bytes_b64` in this corpus was produced by canonicalizing the materialized preimage with `rfc8785` 0.1.4, the Trail of Bits reference implementation that `jcs_edge_v1` also names, and independently reproduced with a second serializer before being pinned.

## Source and attribution

The two boundary cases are drawn from [`agent-evidence-vectors`](https://github.com/astrogilda/agent-evidence-vectors), which carries them as statement-level vectors in a suite you can run with `uvx agent-evidence-vectors`; each vector here records the corpus in its `trace` field, and the two with a direct counterpart carry that vector's identifier. `PROVENANCE.json` pins the source suite revision and corpus digest alongside a SHA-256 for each file in this directory.

Authored for this repository under Apache-2.0, the license the surrounding repository and the sibling `jcs_edge_v1` corpus both use. `jcs_edge_v1` is retained byte-verbatim from its author; this corpus is not a retention of anything, so it carries no upstream `LICENSE` or `NOTICE` to travel with it.
