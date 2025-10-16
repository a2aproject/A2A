// Original file: ../specification/grpc/a2a.proto

import type {
  Message as _a2a_v1_Message,
  Message__Output as _a2a_v1_Message__Output,
} from "../../a2a/v1/Message";
import type {
  SendMessageConfiguration as _a2a_v1_SendMessageConfiguration,
  SendMessageConfiguration__Output as _a2a_v1_SendMessageConfiguration__Output,
} from "../../a2a/v1/SendMessageConfiguration";
import type {
  Struct as _google_protobuf_Struct,
  Struct__Output as _google_protobuf_Struct__Output,
} from "../../google/protobuf/Struct";

/**
 * Request Messages ///////////
 * --8<-- [start:MessageSendParams]
 */
export interface SendMessageRequest {
  /**
   * The message to send to the agent.
   */
  request?: _a2a_v1_Message | null;
  /**
   * Configuration for the send request.
   */
  configuration?: _a2a_v1_SendMessageConfiguration | null;
  /**
   * Optional metadata for the request.
   */
  metadata?: _google_protobuf_Struct | null;
}

/**
 * Request Messages ///////////
 * --8<-- [start:MessageSendParams]
 */
export interface SendMessageRequest__Output {
  /**
   * The message to send to the agent.
   */
  request: _a2a_v1_Message__Output | null;
  /**
   * Configuration for the send request.
   */
  configuration: _a2a_v1_SendMessageConfiguration__Output | null;
  /**
   * Optional metadata for the request.
   */
  metadata: _google_protobuf_Struct__Output | null;
}
