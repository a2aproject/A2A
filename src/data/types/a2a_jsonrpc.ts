/* eslint-disable */
import {
  AgentCard,
  CancelTaskRequest,
  CreateTaskPushNotificationConfigRequest,
  DeleteTaskPushNotificationConfigRequest,
  GetAgentCardRequest,
  GetTaskPushNotificationConfigRequest,
  GetTaskRequest,
  ListTaskPushNotificationConfigRequest,
  ListTaskPushNotificationConfigResponse,
  SendMessageRequest,
  SendMessageResponse,
  Task,
  TaskPushNotificationConfig,
  TaskSubscriptionRequest,
} from "./a2a_core";

export const protobufPackage = "a2a.v1";

/** Older protoc compilers don't understand edition yet. */

export enum JSONRPCErrorCode {
  PARSE_ERROR = -32700,

  INVALID_REQUEST = -32600,

  METHOD_NOT_FOUND = -32601,

  INVALID_PARAMS = -32602,

  INTERNAL_ERROR = -32603,

  TASK_NOT_FOUND = -32001,

  TASK_NOT_CACHEABLE = -32002,

  PUSH_NOTIFICATION_NOT_SUPPORTED = -32003,

  UNSUPPORTED_OPERATION_ERROR = -32004,

  CONTENT_TYPE_NOT_SUPPORTED = -32005,

  INVALID_AGENT_RESPONSE = -32006,

  AUTHENTICATED_CARD_NOT_CONFIGURED = -32007,
}

/** A2AJsonRPCRequest represents a JSON-RPC request for the A2A protocol. */
export interface JSONRPCRequest {
  /** The JSON-RPC version, must be "2.0". */
  readonly jsonrpc: "2.0";
  /** The method to be invoked. */
  method: string;
  /** The identifier for this request. */
  id?: string | number;
  /** The parameters for the method. */
  params?:
    | SendMessageRequest 
    | GetTaskRequest 
    | CancelTaskRequest 
    | TaskSubscriptionRequest 
    | CreateTaskPushNotificationConfigRequest 
    | GetTaskPushNotificationConfigRequest 
    | ListTaskPushNotificationConfigRequest 
    | DeleteTaskPushNotificationConfigRequest 
    | GetAgentCardRequest
}

export type JSONRPCResponse = JSONRPCSuccessResponse | JSONRPCErrorResponse;

export interface JSONRPCSuccessResponse {
  /** The JSON-RPC version, must be "2.0". */
  readonly jsonrpc: "2.0";
  /** The identifier for this request. */
  id?: string | number;
  result:
    | SendMessageResponse
    | Task
    | ListTaskPushNotificationConfigResponse
    | TaskPushNotificationConfig
    | TaskPushNotificationConfig
    | AgentCard
}

export interface JSONRPCErrorResponse {
  /** The JSON-RPC version, must be "2.0". */
  readonly jsonrpc: "2.0";
  /** The identifier for this request. */
  id?: string | number;
  error: JSONRPCError;
}

export interface JSONRPCError {
  /** A number that indicates the error type that occurred. */
  code: JSONRPCErrorCode;
  /**A string providing a short description of the error.*/
  message: string;
  /** A primitive or structured value containing additional information about the error.
   * This may be omitted. */
  data: { [key: string]: any } | undefined;
}
