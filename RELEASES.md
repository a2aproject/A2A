# Agent2Agent (A2A) Release Checklist

This document describes the steps required to create a new release of the
Agent2Agent (A2A) protocol specification and associated documentation.

The process is inspired by the Open Container Initiative runtime-spec release
workflow and adapted for the A2A project.

---

# 1. Pre-Release Preparation

## 1.1 Define Release Scope
- [ ] Determine the type of release:
  - [ ] Patch (`vX.Y.Z`) – bug fixes, clarifications, editorial changes
  - [ ] Minor (`vX.Y.0`) – backward-compatible additions to the protocol
  - [ ] Major (`vX.0.0`) – breaking protocol or specification changes
- [ ] Confirm milestone issues and pull requests are complete
- [ ] Defer unfinished features to the next milestone
- [ ] Ensure consensus among maintainers for the release scope

## 1.2 Issue and Pull Request Review
- [ ] Ensure all release-targeted PRs are merged into `main`
- [ ] Verify each PR references an issue where appropriate
- [ ] Confirm there are no open blocking issues
- [ ] Close or retarget remaining issues to future milestones
- [ ] Confirm CI checks are passing for the main branch

## 1.3 Specification Review
- [ ] Review protocol specification for consistency
- [ ] Verify terminology matches the A2A glossary
- [ ] Validate all JSON examples
- [ ] Validate schema definitions
- [ ] Ensure message formats match the protocol description
- [ ] Verify task lifecycle documentation is accurate
- [ ] Confirm Agent Card structure matches the spec

## 1.4 Documentation Review
- [ ] Update `README.md` if necessary
- [ ] Ensure examples match the current protocol specification
- [ ] Verify documentation builds successfully
- [ ] Confirm diagrams and protocol flows are up to date
- [ ] Verify external links
- [ ] Confirm SDK references are accurate
- [ ] Ensure installation and quickstart instructions work

## 1.5 Version Updates
- [ ] Determine the next semantic version
- [ ] Update version numbers in:
  - [ ] Specification files
  - [ ] Documentation references
  - [ ] Schema files
  - [ ] Version badges if present
- [ ] Confirm version compatibility notes are accurate

---

# 2. Changelog Preparation

## 2.1 Update CHANGELOG
- [ ] Update `CHANGELOG.md`
- [ ] Organize entries under the upcoming version heading
- [ ] Group changes under standard sections:

Suggested sections:
- Added
- Changed
- Deprecated
- Removed
- Fixed
- Security

## 2.2 Review Changelog
- [ ] Confirm all merged PRs are included
- [ ] Ensure notable changes are highlighted
- [ ] Clearly document breaking changes
- [ ] Add migration notes if needed
- [ ] Ensure links to PRs or issues are correct

---

# 3. Validation

## 3.1 Specification Validation
- [ ] Validate all JSON examples
- [ ] Validate schemas
- [ ] Ensure protocol message examples parse correctly
- [ ] Verify field names and types match the spec

## 3.2 Documentation Build
- [ ] Build documentation locally
- [ ] Ensure there are no warnings or errors
- [ ] Verify generated pages render correctly
- [ ] Confirm navigation and links work

## 3.3 Protocol Validation
- [ ] Validate example agent interactions
- [ ] Confirm request/response flows match documentation
- [ ] Verify Agent Card examples are valid
- [ ] Ensure example tasks follow lifecycle definitions

## 3.4 Ecosystem Validation (Recommended)
- [ ] Verify official SDKs build against the new spec
- [ ] Confirm test suites pass
- [ ] Validate interoperability examples
- [ ] Run compliance tests if available

---

# 4. Release Candidate (Optional)

For major releases or releases with significant protocol changes.

- [ ] Create a release candidate tag (e.g., `vX.Y.Z-rc1`)
- [ ] Publish release candidate notes
- [ ] Announce RC to maintainers and community
- [ ] Allow time for community testing
- [ ] Collect feedback and bug reports
- [ ] Fix issues discovered during RC testing
- [ ] Publish additional RCs if necessary

---

# 5. Create the Release

## 5.1 Create Git Tag
Create an annotated git tag:
- [ ] Verify the tag points to the correct commit
- [ ] Confirm the tag appears on GitHub

## 5.2 Create GitHub Release
 Create a new GitHub release from the tag

- [ ]  Copy release notes from CHANGELOG.md
- [ ]  Highlight major changes
- [ ]  Highlight breaking changes and migrations
- [ ]  Mark the release as latest if appropriate

## 5.3 Verify Release Artifacts
Confirm GitHub generated source archives
- [ ] Verify release notes formatting
- [ ] Validate links included in the release
- [ ] Confirm the release tag matches the repository state

# 6. Post-Release Tasks
## 6.1 Documentation Deployment
- [ ] Deploy updated documentation site
- [ ] Verify the latest documentation reflects the new release
- [ ] Ensure versioned documentation remains accessible
- [ ]  Confirm examples in published docs are correct

## 6.2 Ecosystem Updates
- [ ] Notify maintainers of official SDKs
- [ ] Update SDK references to the new version
- [ ] Update compatibility matrices if present
- [ ] Ensure integrations referencing the spec remain compatible

## 6.3 Announcements
- [ ] Publish release announcement
- [ ] GitHub Discussions
- [ ] Project community channels
- [ ] Mailing list or newsletter
- [ ] Social media (if applicable)
- [ ] Highlight important new features
- [ ] Share migration guidance for implementers

## 7. Prepare for the Next Development Cycle
- [ ] Create a new milestone for the next release
- [ ] Reopen deferred issues
- [ ] Update project roadmap if necessary
- [ ]  Encourage new proposals and discussions
- [ ] Continue triaging issues and pull requests

## Appendix: Maintainer Guidelines
Prefer smaller, frequent releases rather than infrequent large releases.
Avoid breaking changes whenever possible.
Clearly document migration paths for protocol changes.
Encourage implementers to test against release candidates.
Maintain strong interoperability across A2A implementations.

