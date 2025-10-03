# Changelog

## [0.4.0](https://github.com/a2aproject/A2A/compare/v0.3.0...v0.4.0) (2025-09-15)

### Features

* **spec:** Add `tasks/list` method for retrieving and filtering tasks with pagination

## [0.3.0](https://github.com/a2aproject/A2A/compare/v0.2.6...v0.3.0) (2025-07-30)


### ⚠ BREAKING CHANGES

* Add mTLS to SecuritySchemes, add oauth2 metadata url field, allow Skills to specify Security ([#901](https://github.com/a2aproject/A2A/issues/901))
* Change Well-Known URI for Agent Card hosting from `agent.json` to `agent-card.json` ([#841](https://github.com/a2aproject/A2A/issues/841))
* Add method for fetching extended card ([#929](https://github.com/a2aproject/A2A/issues/929))

### Features

* Add `signatures` to the `AgentCard` ([#917](https://github.com/a2aproject/A2A/issues/917)) ([ef4a305](https://github.com/a2aproject/A2A/commit/ef4a30505381e99b20103724cabef024389bacef))
* Add method for fetching extended card ([#929](https://github.com/a2aproject/A2A/issues/929)) ([2cd7d98](https://github.com/a2aproject/A2A/commit/2cd7d98bc8566601b9a18ca8afe92a0b4d203248))
* Add mTLS to SecuritySchemes, add oauth2 metadata url field, allow Skills to specify Security ([#901](https://github.com/a2aproject/A2A/issues/901)) ([e162c0c](https://github.com/a2aproject/A2A/commit/e162c0c6c4f609d2f4eef9042466d176ec75ebda))


### Bug Fixes

* **spec:** Add `SendMessageRequest.request` `json_name` mapping to `message` ([#904](https://github.com/a2aproject/A2A/issues/904)) ([2eef3f6](https://github.com/a2aproject/A2A/commit/2eef3f6113851e690cee70a1b1643e1ffd6d2a60))
* **spec:** Add Transport enum to specification ([#909](https://github.com/a2aproject/A2A/issues/909)) ([e834347](https://github.com/a2aproject/A2A/commit/e834347c279186d9d7873b352298e8b19737dd5a))


### Code Refactoring

* Change Well-Known URI for Agent Card hosting from `agent.json` to `agent-card.json` ([#841](https://github.com/a2aproject/A2A/issues/841)) ([0858ddb](https://github.com/a2aproject/A2A/commit/0858ddb884dc4671681fd819648dfd697176abb3))

## [0.2.6](https://github.com/a2aproject/A2A/compare/v0.2.5...v0.2.6) (2025-07-17)


### Bug Fixes

* Type fix and doc clarification ([#877](https://github.com/a2aproject/A2A/issues/877)) ([6f1d17b](https://github.com/a2aproject/A2A/commit/6f1d17ba806c32f2b6fbe465be93ec13bfe7d83c))
* Update json names of gRPC objects for proper transcoding  ([#847](https://github.com/a2aproject/A2A/issues/847)) ([6ba72f0](https://github.com/a2aproject/A2A/commit/6ba72f0d51c2e3d0728f84e9743b6d0e88730b51))

## [0.2.5](https://github.com/a2aproject/A2A/compare/v0.2.4...v0.2.5) (2025-06-30)


### ⚠ BREAKING CHANGES

* **spec:** Add a required protocol version to the agent card. ([#802](https://github.com/a2aproject/A2A/issues/802))
* Support for multiple pushNotification config per task ([#738](https://github.com/a2aproject/A2A/issues/738)) ([f355d3e](https://github.com/a2aproject/A2A/commit/f355d3e922de61ba97873fe2989a8987fc89eec2))


### Features

* **spec:** Add a required protocol version to the agent card. ([#802](https://github.com/a2aproject/A2A/issues/802)) ([90fa642](https://github.com/a2aproject/A2A/commit/90fa64209498948b329a7b2ac6ec38942369157a))
* **spec:** Support for multiple pushNotification config per task ([#738](https://github.com/a2aproject/A2A/issues/738)) ([f355d3e](https://github.com/a2aproject/A2A/commit/f355d3e922de61ba97873fe2989a8987fc89eec2))


### Documentation

* update spec & doc topic with non-restartable tasks ([#770](https://github.com/a2aproject/A2A/issues/770)) ([ebc4157](https://github.com/a2aproject/A2A/commit/ebc4157ca87ae08d1c55e38e522a1a17201f2854))

## [0.2.4](https://github.com/a2aproject/A2A/compare/v0.2.3...v0.2.4) (2025-06-30)


### Features

* feat: Add support for multiple transport announcement in AgentCard ([#749](https://github.com/a2aproject/A2A/issues/749)) ([b35485e](https://github.com/a2aproject/A2A/commit/b35485e02e796d15232dec01acfab93fc858c3ec))

## [0.2.3](https://github.com/a2aproject/A2A/compare/v0.2.2...v0.2.3) (2025-06-12)


### Bug Fixes

* Address some typos in gRPC annotations ([#747](https://github.com/a2aproject/A2A/issues/747)) ([f506881](https://github.com/a2aproject/A2A/commit/f506881c9b8ff0632d7c7107d5c426646ae31592))

## [0.2.2](https://github.com/a2aproject/A2A/compare/v0.2.1...v0.2.2) (2025-06-09)


### ⚠ BREAKING CHANGES

* Resolve spec inconsistencies with JSON-RPC 2.0

### Features

* Add gRPC and REST definitions to A2A protocol specifications ([#695](https://github.com/a2aproject/A2A/issues/695)) ([89bb5b8](https://github.com/a2aproject/A2A/commit/89bb5b82438b74ff7bb0fafbe335db7100a0ac57))
* Add protocol support for extensions ([#716](https://github.com/a2aproject/A2A/issues/716)) ([70f1e2b](https://github.com/a2aproject/A2A/commit/70f1e2b0c68a3631888091ce9460a9f7fbfbdff2))
* **spec:** Add an optional iconUrl field to the AgentCard ([#687](https://github.com/a2aproject/A2A/issues/687)) ([9f3bb51](https://github.com/a2aproject/A2A/commit/9f3bb51257f008bd878d85e00ec5e88357016039))


### Bug Fixes

* Protocol should released as 0.2.2 ([22e7541](https://github.com/a2aproject/A2A/commit/22e7541be082c4f0845ff7fa044992cda05b437e))
* Resolve spec inconsistencies with JSON-RPC 2.0 ([628380e](https://github.com/a2aproject/A2A/commit/628380e7e392bc8f1778ae991d4719bd787c17a9))

## [0.2.1](https://github.com/a2aproject/A2A/compare/v0.2.0...v0.2.1) (2025-05-27)

### Features

* Add a new boolean for supporting authenticated extended cards ([#618](https://github.com/a2aproject/A2A/issues/618)) ([e0a3070](https://github.com/a2aproject/A2A/commit/e0a3070fc289110d43faf2e91b4ffe3c29ef81da))
* Add optional referenceTaskIds for task followups ([#608](https://github.com/a2aproject/A2A/issues/608)) ([5368e77](https://github.com/a2aproject/A2A/commit/5368e7728cb523caf1a9218fda0b1646325f524b))
