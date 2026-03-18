# Extension and Protocol Binding Governance

The A2A organization uses a unified governance framework for both
[Extensions](extensions.md) and [Custom Protocol Bindings](custom-protocol-bindings.md).
This document defines the formal process for proposing, developing, promoting,
and maintaining these artifacts within the A2A organization.

Anyone may develop and publish extensions or custom protocol bindings
independently. The tiers and lifecycle described here apply specifically to
those hosted under the `a2aproject` GitHub organization.

## Tiers

Both extensions and custom protocol bindings use a two-tier system within the
`a2aproject` organization. Repository naming and URI prefixes differ by type:

|                          | Extensions                                      | Custom Protocol Bindings                       |
| :----------------------- | :---------------------------------------------- | :--------------------------------------------- |
| Official repo prefix     | `ext-{name}`                                    | `cpb-{name}`                                   |
| Experimental repo prefix | `experimental-ext-{name}`                       | `experimental-cpb-{name}`                      |
| Official URI prefix      | `https://a2a-protocol.org/extensions/`          | `https://a2a-protocol.org/bindings/`           |

### Official

Official artifacts are developed and maintained under the `a2aproject` GitHub
organization, officially recommended by the TSC. Each repository has designated
maintainers identified in `MAINTAINERS.md`.

**Requirements:**

- Specifications MUST use the same language as the core specification
    ([RFC 2119](https://tools.ietf.org/html/rfc2119))
- MUST be licensed under Apache 2.0
- MUST have at least one reference implementation
- SHOULD have associated documentation on the A2A website

### Experimental

Experimental artifacts provide an incubation pathway for community contributors
to prototype and collaborate on ideas before graduation to official status.

**Creation Requirements:**

- An experimental repository can ONLY be created with sponsorship from an A2A
    Maintainer
- The sponsoring Maintainer is responsible for initial oversight of the
    experimental artifact
- Experimental repositories MUST clearly indicate their experimental/non-official
    status in the README
- Any published packages MUST use naming that clearly indicates experimental
    status
- The TSC retains oversight, including the ability to archive or remove
    experimental repositories

## Lifecycle

Extensions and custom protocol bindings progress through the following phases.

### Proposal Phase

Any community member may propose an extension or custom protocol binding:

1. **Open an Issue**: Create an issue in the main `a2aproject/A2A` repository
    describing:
    - An abstract describing the extension's purpose or the binding's transport
        and use case
    - Motivation explaining why this cannot be achieved with the core protocol
        or existing standard bindings
    - An initial technical approach or specification draft
2. **Community Discussion**: The proposal is open for community feedback and
    refinement

### Maintainer Sponsorship

For a proposal to proceed to experimental status:

1. **Secure a Sponsor**: An A2A Maintainer must agree to sponsor the proposal
2. **Repository Creation**: The sponsoring Maintainer creates the
    `experimental-ext-*` or `experimental-cpb-*` repository under `a2aproject`
3. **Oversight**: The sponsoring Maintainer provides initial oversight and
    ensures alignment with A2A design principles

### Experimental Development

While in experimental status:

- Contributors iterate on the specification and reference implementations
- The experimental artifact MAY be used by early adopters with the
    understanding that breaking changes are expected
- Community feedback is gathered and incorporated
- The experimental repository MUST clearly indicate its non-official status

### Graduation to Official Status

To graduate an experimental extension or binding to official status:

1. **Maturity Requirements**:
    - At least one production-quality reference implementation
    - Documentation meeting A2A standards
    - Evidence of community adoption or interest
    - Clear maintainer commitment for ongoing maintenance
2. **Graduation Proposal**: Open an issue in `a2aproject/A2A` with:
    - Reference to the experimental repository and its implementations
    - Summary of community feedback and adoption
    - Proposed maintainers for the official artifact
3. **TSC Vote**:
    - The proposal is added to the TSC meeting agenda
    - **Quorum Requirement**: At least 50% of TSC voting members must be
        present
    - **Approval**: Requires majority vote of those in attendance (per A2A
        governance)
    - The TSC may request revisions before a final vote
4. **Acceptance**:
    - (Extensions) The repository is renamed from `experimental-ext-*` to
        `ext-*`; documentation is added to the A2A website's extensions page
    - (Custom Protocol Bindings) The repository is renamed from
        `experimental-cpb-*` to `cpb-*`; documentation is added to the A2A
        website's custom protocol bindings page

### Official Iteration

Once official, extensions and bindings may be iterated on:

- Repository maintainers are responsible for day-to-day governance
- Changes SHOULD be coordinated via the relevant working group if one exists
- Breaking changes require a new identifier
- Breaking changes require TSC review
- Maintainers SHOULD coordinate with SDK maintainers for implementation updates

### Promotion to Core Protocol

Some extensions may eventually transition to core protocol features, and some
custom protocol bindings may transition to core bindings. This is governed
through the existing A2A specification enhancement process:

- A proposal is submitted following the standard specification change process
- The proposal references the official extension or binding and its adoption
- TSC vote with standard quorum and majority requirements applies
- Not all extensions or bindings are suitable for core inclusion; many will
    remain as extensions or custom bindings indefinitely

## SDK Support

SDK support requirements differ between extensions and official custom protocol
bindings, reflecting their different roles in the protocol ecosystem.

**Extensions**: A2A SDKs MAY implement extensions. Where implemented:

- Extensions MUST be disabled by default and require explicit opt-in
- SDK documentation SHOULD list supported extensions
- SDK maintainers have full autonomy over extension support decisions
- Extension support is not required for protocol conformance

**Official Custom Protocol Bindings**: A2A SDKs SHOULD implement official
custom protocol bindings. Where implemented:

- Custom protocol bindings MUST be disabled by default and require explicit
    opt-in
- SDK documentation SHOULD list supported custom protocol bindings
- SDK maintainers have full autonomy over binding support decisions
- Custom protocol binding support is not required for protocol conformance

## Legal Requirements

### Licensing

Official extensions and custom protocol bindings MUST be available under the
Apache 2.0 license, consistent with the core A2A project.

### Contributor License Grant

By submitting a contribution to an official A2A extension or custom protocol
binding repository, contributors represent that:

1. They have the legal authority to grant the rights
2. The contribution is original work or they have sufficient rights to submit it
3. They grant to the Linux Foundation and recipients a perpetual, worldwide,
    non-exclusive, royalty-free license to use, reproduce, modify, and
    distribute the contribution

### Antitrust

Extension and custom protocol binding developers acknowledge that:

- They may compete with other participants
- They have no obligation to implement any extension or binding
- They are free to develop competing extensions or bindings
- Status as an official extension or binding does not create an exclusive
    relationship
