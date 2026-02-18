# Changelog

## [1.0.0](https://github.com/a2aproject/A2A/compare/v0.3.0...v1.0.0) (2026-02-18)


### ⚠ BREAKING CHANGES

* **spec:** remove duplicated ID from the create task push config request ([#1487](https://github.com/a2aproject/A2A/issues/1487))
* **spec:** pluralize configs in `ListTaskPushNotificationConfigs` ([#1486](https://github.com/a2aproject/A2A/issues/1486))
* **spec:** Add LF prefix to the package. ([#1474](https://github.com/a2aproject/A2A/issues/1474))
* **spec:** Switch to non-complex IDs in requests ([#1389](https://github.com/a2aproject/A2A/issues/1389))
* **spec:** Standardize spelling of "canceled" to use American Spelling throughout ([#1283](https://github.com/a2aproject/A2A/issues/1283))
* **spec:** Align enum format with ADR-001 ProtoJSON specification ([#1384](https://github.com/a2aproject/A2A/issues/1384))
* **spec:** Remove redundant `final` field from `TaskStatusUpdateEvent` ([#1308](https://github.com/a2aproject/A2A/issues/1308))
* **spec:** Move `extendedAgentCard` field to `AgentCapabilities` ([#1307](https://github.com/a2aproject/A2A/issues/1307))
* **spec:** Fixes for the last_updated_after field ([#1358](https://github.com/a2aproject/A2A/issues/1358))
* **spec:** modernize oauth 2.0 flows - remove implicit/password, add device code / pkce ([#1303](https://github.com/a2aproject/A2A/issues/1303))
* **spec:** Make "message" field name consistent between protocol bindings ([#1302](https://github.com/a2aproject/A2A/issues/1302))
* **spec:** Remove deprecated fields from a2a.proto for v1.0 release ([#1301](https://github.com/a2aproject/A2A/issues/1301))
* **spec:** Rename `supportsAuthenticatedExtendedCard` to `supportsExtendedAgentCard` ([#1222](https://github.com/a2aproject/A2A/issues/1222))
* **spec:** Remove v1s from a2a url http bindings
* **spec:** Large refactor of specification to separate application protocol definition from mapping to transports

### Features

* **spec:** Add `tasks/list` method with filtering and pagination to the specification ([0a9f629](https://github.com/a2aproject/A2A/commit/0a9f629e801d4ae89f94991fc28afe9429c91cbc))
* **spec:** modernize oauth 2.0 flows - remove implicit/password, add device code / pkce ([#1303](https://github.com/a2aproject/A2A/issues/1303)) ([525ff38](https://github.com/a2aproject/A2A/commit/525ff38e5fe2a118f5be5d25189708b590616dd4))
* **spec:** Natively Support Multi-tenancy on gRPC through an additional scope field on the request. ([#1195](https://github.com/a2aproject/A2A/issues/1195)) ([cfbce32](https://github.com/a2aproject/A2A/commit/cfbce32cb0ac2a630597eb8b771691cac5b20a4b)), closes [#1148](https://github.com/a2aproject/A2A/issues/1148)
* **spec:** Provide ability for SDKs to be backwards compatible. ([#1401](https://github.com/a2aproject/A2A/issues/1401)) ([227e249](https://github.com/a2aproject/A2A/commit/227e2493c317004b7e6f7ef4a484e220ffd0b77e))
* **spec:** Remove v1s from a2a url http bindings ([1bd263f](https://github.com/a2aproject/A2A/commit/1bd263f5373fdc8fa7c17ec8bdb24088996b6828))


### Bug Fixes

* Add missing metadata field to Part message in gRPC specification ([#1019](https://github.com/a2aproject/A2A/issues/1019)) ([b3b266d](https://github.com/a2aproject/A2A/commit/b3b266d127dde3d1000ec103b252d1de81289e83)), closes [#1005](https://github.com/a2aproject/A2A/issues/1005)
* Add name field to FilePart protobuf message ([#983](https://github.com/a2aproject/A2A/issues/983)) ([2b7cb6f](https://github.com/a2aproject/A2A/commit/2b7cb6f8408e6324c48fb82c71839c67a18f1fab)), closes [#984](https://github.com/a2aproject/A2A/issues/984)
* Clarify blocking calls return on interrupted states ([#1403](https://github.com/a2aproject/A2A/issues/1403)) ([0655ff3](https://github.com/a2aproject/A2A/commit/0655ff324a93b7e0eaebc108666e6703998b4a9c))
* **doc:** Makes JSON-RPC SendMessage response clearer ([#1241](https://github.com/a2aproject/A2A/issues/1241)) ([5792804](https://github.com/a2aproject/A2A/commit/57928043727e5e002a1395dadfb5f699d0626b1c))
* **grpc:** Fix inconsistent property name between gRPC and JSON-RPC in Message object ([#1100](https://github.com/a2aproject/A2A/issues/1100)) ([2a1f819](https://github.com/a2aproject/A2A/commit/2a1f819aaa2540602ee81498e159ebe0192be818))
* **grpc:** missing field in gRPC spec - state_transition_history  ([#1138](https://github.com/a2aproject/A2A/issues/1138)) ([a2de798](https://github.com/a2aproject/A2A/commit/a2de7981cadeaa5197bee56cbd6ab7b2c5da2541)), closes [#1139](https://github.com/a2aproject/A2A/issues/1139)
* **grpc:** Update `CreateTaskPushNotificationConfig` endpoint to `/v1/{parent=tasks/*/pushNotificationConfigs}` ([#979](https://github.com/a2aproject/A2A/issues/979)) ([911f9b0](https://github.com/a2aproject/A2A/commit/911f9b059c52dd65497b76ccf63d196ca84c7f0e))
* **proto:** Add icon_url to a2a.proto ([#986](https://github.com/a2aproject/A2A/issues/986)) ([17e7f62](https://github.com/a2aproject/A2A/commit/17e7f62df9a3e4ca0768ab8d4f0bb7573b3d73e1))
* **proto:** Adds metadata field to A2A DataPart proto ([#1004](https://github.com/a2aproject/A2A/issues/1004)) ([a8b45dc](https://github.com/a2aproject/A2A/commit/a8b45dcc429a5571ef8a24c36336bf84b89bbd7f))
* Remove unimplemented state_transition_history capability field ([#1396](https://github.com/a2aproject/A2A/issues/1396)) ([c768a44](https://github.com/a2aproject/A2A/commit/c768a44da0f719595e375636f3cab9898ff6df75)), closes [#1228](https://github.com/a2aproject/A2A/issues/1228)
* Restore CreateTaskPushNotificationConfig method naming ([#1402](https://github.com/a2aproject/A2A/issues/1402)) ([d14f410](https://github.com/a2aproject/A2A/commit/d14f4107119bf0fe0dff9e2c577eb4ab70b51793))
* Revert "chore(gRPC): Update a2a.proto to include metadata on GetTaskRequest" ([#1000](https://github.com/a2aproject/A2A/issues/1000)) ([e6b8c65](https://github.com/a2aproject/A2A/commit/e6b8c654a86a6ee461bb5c7be5d5b81004b80a92))
* Simplify Part message structure by flattening FilePart and DataPart ([#1411](https://github.com/a2aproject/A2A/issues/1411)) ([bfae8f7](https://github.com/a2aproject/A2A/commit/bfae8f7791e019f21f6662dd73fce0b3ab261cd6))
* **spec:** Add LF prefix to the package. ([#1474](https://github.com/a2aproject/A2A/issues/1474)) ([a54e809](https://github.com/a2aproject/A2A/commit/a54e80904aa32c74a14bc2c3d21bf82936ccbbdd))
* **spec:** add metadata to `CancelTaskRequest` ([#1485](https://github.com/a2aproject/A2A/issues/1485)) ([c441b91](https://github.com/a2aproject/A2A/commit/c441b910b64d45514ae929a42e7367c2a9a2f6c3)), closes [#1484](https://github.com/a2aproject/A2A/issues/1484)
* **spec:** Added clarification on timestamps in HTTP query params ([#1425](https://github.com/a2aproject/A2A/issues/1425)) ([6292104](https://github.com/a2aproject/A2A/commit/6292104e359efca05bd8703174517b6f961ae4e1))
* **spec:** Added clarifying text around messages and artifacts ([#1424](https://github.com/a2aproject/A2A/issues/1424)) ([b03d141](https://github.com/a2aproject/A2A/commit/b03d141aeab6abd71a229e85c81f7e4c00b537ec))
* **spec:** Adjust field number for `ListTasksRequest.tenant` to prevent missing number ([#1470](https://github.com/a2aproject/A2A/issues/1470)) ([cd16c52](https://github.com/a2aproject/A2A/commit/cd16c5276b4c662ca1823678d07487a624cad606))
* **spec:** Clarify contextId behavior when message is sent with taskId but without contextId ([#1309](https://github.com/a2aproject/A2A/issues/1309)) ([a336a5a](https://github.com/a2aproject/A2A/commit/a336a5a4846fdf85079d4e310339ea0128922ee7))
* **spec:** Clarify versioning strategy and client responsibilities in protocol specification ([#1259](https://github.com/a2aproject/A2A/issues/1259)) ([a4afeea](https://github.com/a2aproject/A2A/commit/a4afeea788b3877101f7a63c2e50091709490058))
* **spec:** Fix/1251 clarify authentication scheme ([#1256](https://github.com/a2aproject/A2A/issues/1256)) ([3e6c7db](https://github.com/a2aproject/A2A/commit/3e6c7db90790c2d05dad3ab1a313de26debe5cb7))
* **spec:** Fixes for the last_updated_after field ([#1358](https://github.com/a2aproject/A2A/issues/1358)) ([0e204bf](https://github.com/a2aproject/A2A/commit/0e204bf878eb63619e205d3419ebc48d4cd35849))
* **spec:** Make "message" field name consistent between protocol bindings ([#1302](https://github.com/a2aproject/A2A/issues/1302)) ([1e5f462](https://github.com/a2aproject/A2A/commit/1e5f46206403982cc629a0dad535856b28c269aa)), closes [#1230](https://github.com/a2aproject/A2A/issues/1230)
* **spec:** make `history_length` optional ([#1071](https://github.com/a2aproject/A2A/issues/1071)) ([0572953](https://github.com/a2aproject/A2A/commit/057295311b8ddda63bdda56c82a694c76d307e37))
* **spec:** pluralize configs in `ListTaskPushNotificationConfigs` ([#1486](https://github.com/a2aproject/A2A/issues/1486)) ([cf735cb](https://github.com/a2aproject/A2A/commit/cf735cb87056ff6d62abd21a1a66ccb14a23c38e))
* **spec:** Remove deprecated fields from a2a.proto for v1.0 release ([#1301](https://github.com/a2aproject/A2A/issues/1301)) ([60f83c3](https://github.com/a2aproject/A2A/commit/60f83c3faac4770b231f038406c9e02282887a25)), closes [#1227](https://github.com/a2aproject/A2A/issues/1227)
* **spec:** remove duplicated ID from the create task push config request ([#1487](https://github.com/a2aproject/A2A/issues/1487)) ([393898d](https://github.com/a2aproject/A2A/commit/393898dfeefa37186aced5b61733c5d2c0d9c34a))
* **spec:** Remove metadata field from ListTasksRequest ([#1235](https://github.com/a2aproject/A2A/issues/1235)) ([b6ef9ee](https://github.com/a2aproject/A2A/commit/b6ef9eec558c877fb69024df090a8bb63c542a1c))
* **spec:** Remove reserved and fix tags ordering ([#1494](https://github.com/a2aproject/A2A/issues/1494)) ([1997c9d](https://github.com/a2aproject/A2A/commit/1997c9d63058ca0b89361a7d6e508f4641a6f68b))
* **spec:** Rename `supportsAuthenticatedExtendedCard` to `supportsExtendedAgentCard` ([#1222](https://github.com/a2aproject/A2A/issues/1222)) ([c196824](https://github.com/a2aproject/A2A/commit/c196824396bb4af4c595f30e2c503a5ab1dbac4b)), closes [#1215](https://github.com/a2aproject/A2A/issues/1215)
* **spec:** Standardize spelling of "canceled" to use American Spelling throughout ([#1283](https://github.com/a2aproject/A2A/issues/1283)) ([4dd980f](https://github.com/a2aproject/A2A/commit/4dd980f6ff1989177faffa631a695aba811c56ad))
* **spec:** Suggest Unique Identifier fields to be UUID ([#966](https://github.com/a2aproject/A2A/issues/966)) ([00cf76e](https://github.com/a2aproject/A2A/commit/00cf76e7bbc752842ef254f3d4136ed1b5751f6e))
* **spec:** Switch to non-complex IDs in requests ([#1389](https://github.com/a2aproject/A2A/issues/1389)) ([2596c1c](https://github.com/a2aproject/A2A/commit/2596c1c5e0effd941880e8487d38d78b74b9c0bf)), closes [#1390](https://github.com/a2aproject/A2A/issues/1390)
* **spec:** Update security schemes example ([#1364](https://github.com/a2aproject/A2A/issues/1364)) ([f9a8f5b](https://github.com/a2aproject/A2A/commit/f9a8f5b85d5b07824c52d55d63f7d71ccc6303c5))
* Update the Java tutorials and descriptions ([#1181](https://github.com/a2aproject/A2A/issues/1181)) ([202aa06](https://github.com/a2aproject/A2A/commit/202aa069e66f701bacf2156d42d8916fc96a5188))


### Documentation

* **spec:** Align enum format with ADR-001 ProtoJSON specification ([#1384](https://github.com/a2aproject/A2A/issues/1384)) ([810eaa1](https://github.com/a2aproject/A2A/commit/810eaa1c6e6462f845a00774f8622b998272116e)), closes [#1344](https://github.com/a2aproject/A2A/issues/1344)


### Code Refactoring

* **spec:** Large refactor of specification to separate application protocol definition from mapping to transports ([b078419](https://github.com/a2aproject/A2A/commit/b0784199543eebf2e95dcb02e9336cb213923506))
* **spec:** Move `extendedAgentCard` field to `AgentCapabilities` ([#1307](https://github.com/a2aproject/A2A/issues/1307)) ([40d6286](https://github.com/a2aproject/A2A/commit/40d6286fbe29fb083d416b77e84122df8d70ae9d))
* **spec:** Remove redundant `final` field from `TaskStatusUpdateEvent` ([#1308](https://github.com/a2aproject/A2A/issues/1308)) ([5b101cc](https://github.com/a2aproject/A2A/commit/5b101cce0fff449c1120ad50ce360acf7c90bac3))

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

* Protocol should be released as 0.2.2 ([22e7541](https://github.com/a2aproject/A2A/commit/22e7541be082c4f0845ff7fa044992cda05b437e))
* Resolve spec inconsistencies with JSON-RPC 2.0 ([628380e](https://github.com/a2aproject/A2A/commit/628380e7e392bc8f1778ae991d4719bd787c17a9))

## [0.2.1](https://github.com/a2aproject/A2A/compare/v0.2.0...v0.2.1) (2025-05-27)

### Features

* Add a new boolean for supporting authenticated extended cards ([#618](https://github.com/a2aproject/A2A/issues/618)) ([e0a3070](https://github.com/a2aproject/A2A/commit/e0a3070fc289110d43faf2e91b4ffe3c29ef81da))
* Add optional referenceTaskIds for task followups ([#608](https://github.com/a2aproject/A2A/issues/608)) ([5368e77](https://github.com/a2aproject/A2A/commit/5368e7728cb523caf1a9218fda0b1646325f524b))
