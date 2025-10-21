# A2A Types

Core objects and method types for A2A Protocol (gRPC and JSONRpc)
This folder contains the data and transports schema for the A2A Protocol

## Steps to update

1. Clone this repository.
2. Run `npm install`
3. Update `data/a2a_core.proto` with required changes
4. Run `npm run generate-types`, this will update the generated type `a2a_core.ts` in `data/types`.
5. Update `src/a2a_jsonrpc.ts` with required changes
6. Run `npm run generate`, this will update `transports/json-rpc/a2a.json`, merging the changes from the `src/types/a2a_core.ts` and the `src/types/a2a_jsonrpc.ts`.
7. Verify the updates and push to the repository.

**DO NOT DIRECTLY CHANGE `a2a.json` file. THIS MUST BE GENERATED USING `npm run generate`**