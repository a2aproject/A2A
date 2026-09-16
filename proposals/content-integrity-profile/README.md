# Content Integrity Profile: jcs_edge_v1 conformance appendix

## Purpose

Issue [#1140](https://github.com/a2aproject/A2A/issues/1140) proposes an optional Content Integrity Profile for A2A artifacts, anchored on RFC 8785 (JCS) canonicalization: `hash = "sha256:" + hex(SHA-256(JCS(artifact)))`. Discussion on that issue converged on a specific risk. Two conformant-looking JCS implementations can still hash the same artifact to different bytes, because plain "sorted keys" JSON serialization under-specifies string escaping, number formatting, and property-name ordering for characters outside the Basic Multilingual Plane. A self-check against one's own serializer cannot catch this; it takes an independent fixture set that pins the disputed cases and their expected output. This directory adds that fixture set, `jcs_edge_v1`, as a conformance appendix so any implementation of the profile, in any language, can verify its canonicalizer against the same ten vectors before claiming interoperability.

`jcs_edge_v1` was authored by chopmob-cloud (AlgoVoi) and posted to #1140 on 2026-07-19. It pins RFC 8785 sections 3.2.2.3 (`1.0` and `1` canonicalize to the same bytes), 3.2.3 (property names ordered by UTF-16 code unit, not Unicode code point, so a supplementary-plane key can sort before a Basic-Multilingual-Plane key), and 3.2.4 (U+2028 and U+2029 inside a string emit as literal UTF-8, not backslash-u escapes). Erik Newton reproduced all ten vectors byte-for-byte against an independent canonicalizer on 2026-07-19 and again as a standing CI check in the Concordia Protocol repository ([eriknewton/concordia-protocol#212](https://github.com/eriknewton/concordia-protocol/pull/212)). kuangmi-bit cross-referenced the Go JCS implementation in [a2a-go#368](https://github.com/a2aproject/a2a-go/issues/368) (`canonicalFloat`, already exercising RFC 8785 section 3.2.2.2) as a second, independently-authored canonicalizer expected to run this same corpus.

## Placement note

The Content Integrity Profile spec text itself has not landed in this repository; the original proposal ([PR #1141](https://github.com/a2aproject/A2A/pull/1141)) was closed without merging while the canonicalization approach was still under discussion. This appendix is therefore placed as a standalone proposal document rather than folded into `docs/specification.md` or an official `a2aproject/ext-*` extension repository. It can move into either location once the profile text itself is accepted; the vectors and their provenance do not change either way.

## Retention layout

This directory mirrors the retention layout established in `eriknewton/concordia-protocol#212`, which the #1140 thread named as the reusable pattern:

```text
proposals/content-integrity-profile/
├── README.md                              (this file)
└── vectors/jcs_edge_v1/
    ├── jcs_edge_v1.json                    (10 vectors, byte-verbatim from upstream)
    ├── LICENSE                             (upstream Apache-2.0 license, byte-verbatim)
    ├── NOTICE                              (upstream Apache-2.0 notice, byte-verbatim)
    └── PROVENANCE.json                     (source commit, SHA-256 pins, attribution)
```

Every file under `vectors/jcs_edge_v1/` is retained byte-verbatim as received; nothing here rewrites, reformats, or re-encodes them. `PROVENANCE.json` pins the upstream commit and a SHA-256 for each file, plus a note that this copy was taken from the Concordia retention rather than re-fetched, so the hashes trace back through one recorded hop instead of a fresh, unverified download. The upstream `LICENSE` and `NOTICE` travel with the vectors per Apache License 2.0 Section 4(d); authorship and copyright remain with chopmob-cloud (AlgoVoi).

## Attribution

- Vector authorship: chopmob-cloud (AlgoVoi), `chopmob-cloud/algovoi-jcs-conformance-vectors`, commit `f075640f4634bb21aefa679d4405d52f364d30ce`.
- Proposed and discussed in `a2aproject/A2A` issue [#1140](https://github.com/a2aproject/A2A/issues/1140).
- Retention pattern and standing CI check: `eriknewton/concordia-protocol` [PR #212](https://github.com/eriknewton/concordia-protocol/pull/212).

## How to run

The vectors are self-checking and language-neutral: each entry in `jcs_edge_v1.json` carries a `preimage` object, the expected canonical bytes (`expected_jcs_bytes_b64`), and the expected SHA-256 of those bytes (`expected_sha256`). To check a canonicalizer against the corpus:

1. For each vector, canonicalize `preimage` using your implementation of RFC 8785 (JSON Canonicalization Scheme).
2. Compare the resulting bytes, exactly, against `expected_jcs_bytes_b64` (base64-decoded).
3. Compute SHA-256 over those bytes and compare against `expected_sha256`.
4. A pass requires all ten vectors to match on both the byte comparison and the hash; a canonicalizer that only checks the hash can still pass on the wrong bytes if it happens to collide, so step 2 is not optional.

This sequence has no dependency on any particular language or library; any RFC 8785 implementation can be checked against the same fixed inputs and outputs.
