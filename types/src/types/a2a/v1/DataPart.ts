// Original file: ../specification/grpc/a2a.proto

import type {
  Struct as _google_protobuf_Struct,
  Struct__Output as _google_protobuf_Struct__Output,
} from "../../google/protobuf/Struct";

/**
 * --8<-- [start:DataPart]
 * DataPart represents a structured blob. This is most commonly a JSON payload.
 */
export interface DataPart {
  data?: _google_protobuf_Struct | null;
}

/**
 * --8<-- [start:DataPart]
 * DataPart represents a structured blob. This is most commonly a JSON payload.
 */
export interface DataPart__Output {
  data: _google_protobuf_Struct__Output | null;
}
