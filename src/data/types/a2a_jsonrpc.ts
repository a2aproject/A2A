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

// --8<-- [start:JSONRPCErrorCode]
/**
 * The set of ErrorCodes that can be used in A2A with JSONRpc protocol.
 */
export enum JSONRPCErrorCode {
  /** An error indicating that the server received invalid JSON. */
  PARSE_ERROR = -32700,
  /** An error indicating that the JSON sent is not a valid Request object. */
  INVALID_REQUEST = -32600,
  /** An error indicating that the requested method does not exist or is not available. */
  METHOD_NOT_FOUND = -32601,
  /** An error indicating that the method parameters are invalid. */
  INVALID_PARAMS = -32602,
  /** An error indicating an internal error on the server. */
  INTERNAL_ERROR = -32603,
  /** An A2A-specific error indicating that the requested task ID was not found. */
  TASK_NOT_FOUND = -32001,
  /** An A2A-specific error indicating that the task is in a state where it cannot be canceled. */
  TASK_NOT_CACHEABLE = -32002,
  /** An A2A-specific error indicating that the agent does not support push notifications. */
  PUSH_NOTIFICATION_NOT_SUPPORTED = -32003,
  /** An A2A-specific error indicating that the requested operation is not supported by the agent. */
  UNSUPPORTED_OPERATION_ERROR = -32004,
  /** An A2A-specific error indicating an incompatibility between the requested
  * content types and the agent's capabilities. */
  CONTENT_TYPE_NOT_SUPPORTED = -32005,
  /** An A2A-specific error indicating that the agent returned a response that
  * does not conform to the specification for the current method. */
  INVALID_AGENT_RESPONSE = -32006,
  /** An A2A-specific error indicating that the agent does not have an Authenticated Extended Card configured */
  AUTHENTICATED_CARD_NOT_CONFIGURED = -32007,
}
// --8<-- [end:JSONRPCErrorCode]

// --8<-- [start:JSONRPCRequest]
/**
 * Represents a JSON-RPC 2.0 Request object.
 */
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
// --8<-- [end:JSONRPCRequest]

export type JSONRPCResponse = JSONRPCSuccessResponse | JSONRPCErrorResponse;

// --8<-- [start:JSONRPCSuccessResponse]
/**
 * Represents a successful JSON-RPC 2.0 Response object.
 */
export interface JSONRPCSuccessResponse {
  /** The JSON-RPC version, must be "2.0". */
  readonly jsonrpc: "2.0";
  /** The identifier for this request. */
  id?: number | string | null;
  /**
  * This field MUST NOT exist in an success response.
  */
  error?: never;
  /**
  * The value of this member is determined by the method invoked on the Server.
  */
  result:
    | SendMessageResponse
    | Task
    | ListTaskPushNotificationConfigResponse
    | TaskPushNotificationConfig
    | TaskPushNotificationConfig
    | AgentCard
}
// --8<-- [end:JSONRPCSuccessResponse]

// --8<-- [start:JSONRPCErrorResponse]
/**
 * Represents a JSON-RPC 2.0 Error Response object.
 */
export interface JSONRPCErrorResponse {
  /** The JSON-RPC version, must be "2.0". */
  readonly jsonrpc: "2.0";
  /** The identifier for this request. */
  id?: number | string | null;
  /**
  * This field MUST NOT exist in an error response.
  */
  result?: never;
  /**
  * An object describing the error that occurred.
  */
  error: JSONRPCError;
}
// --8<-- [end:JSONRPCErrorResponse]

// --8<-- [start:JSONRPCError]
/**
 * Represents a JSON-RPC 2.0 Error object, included in an error response.
 */
export interface JSONRPCError {
  /** A number that indicates the error type that occurred. */
  code: JSONRPCErrorCode;
  /**A string providing a short description of the error.*/
  message: string;
  /** A primitive or structured value containing additional information about the error.
   * This may be omitted. */
  data: { [key: string]: any } | undefined;
}
// --8<-- [end:JSONRPCError]