# A2A JSON Artifact

`a2a.json` is a **non-normative build artifact** derived from the canonical proto definition at `specification/grpc/a2a.proto`. It is generated during builds and intentionally **not** committed to source control.

Generation pipeline:

1. `protoc` + `protoc-gen-openapiv2` produce `specification/grpc/openapi/a2a.swagger.json`.
2. `scripts/extract_json_schema.sh` extracts `definitions` into an ephemeral `a2a.json` (draft-07 schema bundle) copied to `docs/spec-json/a2a.json` for site publishing.

Removed artifact: `a2a-openapi-schemas.json` (an intermediate OpenAPI schema expansion) previously committed during early tooling iteration has been deleted to avoid tracking generated content. Only source (`a2a.proto`) and scripts remain under version control.

The artifact is generated automatically in:

- Local docs builds (`scripts/build_docs.sh`)
- CI workflow (`.github/workflows/generate-a2a-json.yml`) on proto changes

## Do Not Edit

Do **NOT** edit `a2a.json` manually. Update the proto instead. The file is transient and will be regenerated.

## Future Work

Planned improvements include:

- Optional OpenAPI v3 conversion and publishing a draft 2020-12 `components.schemas` bundle.
- Automatic alias injection for deprecated names (anyOf wrapper) to ease migrations.
- Validation step ensuring no generated artifacts are reintroduced into git.
