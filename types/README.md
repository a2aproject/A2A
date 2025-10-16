# A2A Types

Core objects and method types for A2A Protocol

## Steps to update

1. Clone this repository.
2. Run `npm install`
3. Update `specification/grpc/a2a.proto` with required changes
4. Run `npm run generate-types`, this will update the generated types in `src/types`.
5. Run `npm run generate`, this will update `a2a.json`.
6. Verify the updates and push to the repository.

**DO NOT DIRECTLY CHANGE `a2a.json` file. THIS MUST BE GENERATED USING `npm run generate`**
