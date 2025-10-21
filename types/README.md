# A2A Types

Core objects and method types for A2A Protocol (gRPC and JSONRpc)

## Steps to update

1. Clone this repository.
2. Run `npm install`
3. Update `specification/grpc/a2a_core.proto` with required changes
4. Run `npm run generate-types`, this will update the generated type `a2a_core.ts` in `src/types`.
3. Update `src/a2a_jsonrpc.ts` with required changes
5. Run `npm run generate`, this will update `a2a.json`, merging the changes from the `specification/grpc/a2a_core.proto` and the `src/a2a_jsonrpc.ts`.
6. Verify the updates and push to the repository.

**DO NOT DIRECTLY CHANGE `a2a.json` file. THIS MUST BE GENERATED USING `npm run generate`**
