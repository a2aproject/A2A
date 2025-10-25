# A2A TypeScript Helper Types

This package contains historical TypeScript interfaces used for JSON Schema generation prior to adoption of the proto→OpenAPI→Schema pipeline.

## Current Status

The file `specification/grpc/a2a.proto` is now the **sole normative source** for protocol data models. The JSON artifact `specification/json/a2a.json` is generated (not committed) during documentation builds and CI using `protoc-gen-openapiv2` plus a schema extraction step.

These TypeScript interfaces remain for convenience in TypeScript SDK development but SHOULD NOT be treated as authoritative. Divergence should be resolved by updating the proto first, then syncing any needed TS helper types.

## Updating Types

1. Make changes to `specification/grpc/a2a.proto` (canonical).
2. Regenerate artifacts locally via `bash scripts/build_docs.sh` (or let CI update `a2a.json`).
3. Optionally reflect new/changed shapes in `types/src/types.ts` for developer ergonomics.

## Deprecation Notice

The previous `npm run generate` workflow (TypeScript → JSON Schema) is deprecated and will be removed in a future release. Do not rely on it for producing `a2a.json`.

## Do Not Edit

Do **NOT** edit `specification/json/a2a.json` directly; it is a build artifact.
