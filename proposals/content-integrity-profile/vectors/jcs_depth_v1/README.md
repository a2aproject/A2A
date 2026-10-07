# Content Integrity Profile: jcs_depth_v1 conformance vectors

## What this corpus pins

`jcs_edge_v1` pins the bytes an RFC 8785 canonicalizer must produce. This corpus pins the input it must refuse.

The RFC specifies escaping, number form and property ordering. It specifies no limit on how deeply an input may nest, and that omission is deliberate. It still leaves a profile built on JCS with a gap the byte-level vectors cannot reach.

Two implementations that agree on every `jcs_edge_v1` vector can still disagree about whether a deeply nested artifact canonicalizes at all. One returns bytes, one returns an error, and one walks off the end of its call stack. All three conform to the RFC, so the profile has to state the bound itself or inherit whichever bound each implementation happened to pick.

The gap matters because canonicalization runs before signature verification: a verifier has to canonicalize a received artifact to learn what bytes the signature covers, so anyone who can hand the verifier an artifact reaches the recursive walk with no key, no prior trust and no earlier step at which the verifier could have refused the input.

A canonicalizer that recurses once per nesting level and carries no depth counter exhausts its stack on such input. In Go, stack exhaustion is not an exception a caller can catch. The Go runtime reports `fatal error: stack overflow` and terminates the process, and a deferred `recover` does not intercept it.

The widely used Go implementation `gowebpki/jcs` was built this way through v1.0.1, descending recursively through `parseElement`, `parseObject` and `parseArray` with no depth counter on any path, so the depth of the input set the depth of its call stack. In a measurement with v1.0.1 on `go1.25.5`, an input nested 10^7 levels deep, 20 MB of brackets, ended the process with that error, and one nested 10^5 levels, 200 KB of brackets, took about two minutes on one core. Its v1.0.2 release of 21 September adds a limit of 10,000 levels, the figure `encoding/json` uses, while `serde_json` stops at 128, so each library still picks its own bound.

A byte cap does not close this gap. Pure nesting costs a few bytes per level, so it passes any plausible stack long before it reaches any plausible size limit. The bound has to be checked before the walk begins.

## The bound

Depth counts **open containers**. The outermost brace or bracket is depth 1, and every object or array opened inside it adds one, an empty container included.

The counting rule matters as much as the number. Some counters charge a level on recursion into a child. An empty container has no child, so such a counter never charges it and lands one level off. Two implementations can hold the identical constant and still disagree across the boundary, which is the failure `jcs-depth-004` and `jcs-depth-103` exist to separate.

The bound in this corpus is **128**, and 128 is a proposed profile choice. The RFC states no depth limit, no adopted A2A rule states one, and [in-toto/attestation#570](https://github.com/in-toto/attestation/pull/570) has not merged, so the number is a requirement of none of the three.

It is the figure and the counting rule that pull request proposes, where it was chosen on two grounds: it is the recursion limit `serde_json` already enforces, and it sits far above real content. The deepest artifact in the corpus that prompted it nests seven levels.

Each vector states its depth as a `count` in a preimage rule, so a different bound regenerates the set by changing that integer alone. Implementations still have to agree on how they count, and the pair of vectors named above is where that shows.

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

Four `pair_invariants` in the corpus state the relations the individual vectors cannot. Each accept and its one-level-deeper reject locate the boundary exactly: an implementation that accepts both has no bound, and one that rejects both has the bound off by one.

`jcs-depth-104` is passed only when the implementation returns a rejection to its caller. A process that dies on that input has not rejected it.

## How to run

Preimages are given as nesting rules, so `jcs_depth_v1.json` stays four levels deep and a parser that enforces the bound it describes can still read it. To check the corpus, materialize each rule and run it against your canonicalizer in five steps.

1. For `i` from 0 to `count - 1`, emit an opener for `containers[i % len(containers)]`: `{"a":` for `object`, `[` for `array`.

2. Emit `leaf`, then the matching closers innermost first.

3. Compute SHA-256 over the materialized UTF-8 bytes and compare against `preimage_sha256`. Do this before canonicalizing anything, because a vector built wrong cross-checks cleanly against itself and proves nothing.

4. For an `accept` vector, canonicalize the preimage, compare the bytes exactly against the base64-decoded `expected_jcs_bytes_b64`, and compare SHA-256 of those bytes against `expected_sha256`.

5. For a `reject` vector, confirm your canonicalizer returns a rejection to the caller. No canonical bytes are published for these, since an implementation that produces bytes here has not applied the bound.

Every `expected_jcs_bytes_b64` in this corpus was produced by canonicalizing the materialized preimage with `rfc8785` 0.1.4, the Trail of Bits reference implementation that `jcs_edge_v1` also names.

The independent check is a third party's run against the Go canonicalizer in [a2aproject/a2a-go#368](https://github.com/a2aproject/a2a-go/pull/368) at `eddcf62`, reported on [#2219](https://github.com/a2aproject/A2A/pull/2219#issuecomment-5749126086), which pinned this corpus's digests before running anything and then reproduced the expected bytes and SHA-256 for all four accept vectors.

The same run shows what the `jcs-depth-104` row cannot tell you on its own. The Go implementation returned `exceeded max depth` to its caller, which the row scores as a pass.

That refusal came from a nesting cap of 10,000 in the `encoding/json` decoder, and not from the canonicalizer, whose walk is recursive and carries no counter.

An implementation can therefore pass `jcs-depth-104` on a property of its toolchain and still have no bound of its own. The reject vectors one level past the bound catch that case, and the same run accepted every one of them.

## Source and attribution

The two boundary cases are drawn from [`agent-evidence-vectors`](https://github.com/probityai/agent-evidence-vectors), which carries them as statement-level vectors in a suite you can run with `uvx agent-evidence-vectors`.

Each vector here records that corpus in its `trace` field, and the two with a direct counterpart carry that vector's identifier. `PROVENANCE.json` pins the source suite revision and corpus digest alongside a digest for each file in this directory.

The corpus is authored for this repository under Apache-2.0, the license the surrounding repository and the sibling `jcs_edge_v1` corpus both use. `jcs_edge_v1` is retained byte-verbatim from its author. This corpus retains nothing from elsewhere, so it carries no upstream `LICENSE` or `NOTICE`.
