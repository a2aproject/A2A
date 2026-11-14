# Specification Enhancement Proposals

A Specification Enhancement Proposal (SEP) is how a change to the A2A
specification is proposed and decided. The
[Technical Steering Committee](https://github.com/a2aproject/A2A/blob/main/GOVERNANCE.md)
owns those changes, so a pull request alone cannot make one: review can correct
an implementation, but only the committee can change what a conforming
implementation must do.

## When to submit a SEP

Submit a SEP when the change alters what a conforming implementation must do:

- **Normative text.** Anything in the [specification](specification.md) that
    adds, removes, or rewords a MUST, SHOULD, or MAY.
- **The protocol definition.** Any change to `specification/a2a.proto`: new or
    removed fields, messages, operations, error codes, or enum values.
- **Conformance.** A change that would alter what the
    [Technology Compatibility Kit](https://github.com/a2aproject/a2a-tck)
    asserts, or that would make an already conforming implementation
    non-conforming.
- **New capability.** An optional feature whose presence other implementations
    must be able to detect and negotiate.

## When a SEP is not needed

- Editorial fixes: typos, broken links, formatting, and reordering that leave
    every requirement's meaning intact.
- Documentation outside the specification: tutorials, conceptual topics, and
    blog posts.
- SDK changes that leave the wire format unchanged.
- Clarifications that remove ambiguity without changing what is required.

If you are unsure which side of that line your change falls on, open an issue
and ask before writing the pull request. A question costs one comment; a
proposal that arrives as finished code and is then rejected costs a review cycle
from both sides.

## Submitting

1. Open an issue with the
    [feature request](https://github.com/a2aproject/A2A/issues/new?template=feature-request.yml)
    template. Describe the problem first, then the change.
1. Discuss it in the issue. Alternatives and their trade-offs belong in this
    discussion, not in a pull request description.
1. The issue is labelled `TSC Review` once it is ready for a committee decision.
    An issue without that label has not been scheduled for one.
1. The committee runs its vote on the issue, recorded with the `gitvote` labels
    described below.

## What a SEP must contain

| Section | What it answers |
| :--- | :--- |
| Problem | What breaks or is ambiguous today, naming the specification text and what it fails to settle |
| Proposed change | The exact normative sentence or proto diff, not a description of one |
| Alternatives | What else was considered, and why each was rejected |
| Compatibility | Whether existing implementations break, and the migration path if they do |
| Conformance impact | Which TCK requirements change, and which conforming implementations would newly fail |
| Evidence | A reference implementation, conformance results, or interoperability reports |

A proposal that states the change in prose but not in normative language hands
the design work to its reviewers. One that links a working implementation is
arguing from evidence, and is the shape most likely to be accepted quickly.

## Decision

The TSC decides by vote under its
[voting rules](https://github.com/a2aproject/A2A/blob/main/GOVERNANCE.md): one
vote per voting member, and a decision taken by electronic vote without a
meeting requires a majority of all voting members. The vote is run in the open
on the issue, and its state is recorded there:

| Label | Meaning |
| :--- | :--- |
| `gitvote/open` | A vote is in progress |
| `gitvote/passed` | The proposal was accepted |
| `gitvote/failed` | The proposal was rejected |
| `gitvote/closed` | The vote has concluded |

Discussion continues until the vote closes. A proposal that changes materially
during a vote should have the vote restarted rather than concluded, so that the
record reflects what was actually decided.

## After a decision

A passed proposal proceeds as a specification pull request that references the
issue, following the normal
[contribution workflow](https://github.com/a2aproject/A2A/blob/main/CONTRIBUTING.md).
A rejected proposal is closed with the reasoning recorded on the issue, so the
same ground is not re-argued without new information.

A rejected proposal is not a rejected contribution. The behaviour can still ship
as an [extension](topics/extensions.md) or a
[custom protocol binding](topics/custom-protocol-bindings.md), each of which has
its own [governance process](topics/extension-and-binding-governance.md) and does
not change what the core specification requires.
