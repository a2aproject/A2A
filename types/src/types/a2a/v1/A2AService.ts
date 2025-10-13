// Original file: ../specification/grpc/a2a.proto

import type * as grpc from "@grpc/grpc-js";
import type { MethodDefinition } from "@grpc/proto-loader";
import type {
  AgentCard as _a2a_v1_AgentCard,
  AgentCard__Output as _a2a_v1_AgentCard__Output,
} from "../../a2a/v1/AgentCard";
import type {
  CancelTaskRequest as _a2a_v1_CancelTaskRequest,
  CancelTaskRequest__Output as _a2a_v1_CancelTaskRequest__Output,
} from "../../a2a/v1/CancelTaskRequest";
import type {
  CreateTaskPushNotificationConfigRequest as _a2a_v1_CreateTaskPushNotificationConfigRequest,
  CreateTaskPushNotificationConfigRequest__Output as _a2a_v1_CreateTaskPushNotificationConfigRequest__Output,
} from "../../a2a/v1/CreateTaskPushNotificationConfigRequest";
import type {
  DeleteTaskPushNotificationConfigRequest as _a2a_v1_DeleteTaskPushNotificationConfigRequest,
  DeleteTaskPushNotificationConfigRequest__Output as _a2a_v1_DeleteTaskPushNotificationConfigRequest__Output,
} from "../../a2a/v1/DeleteTaskPushNotificationConfigRequest";
import type {
  Empty as _google_protobuf_Empty,
  Empty__Output as _google_protobuf_Empty__Output,
} from "../../google/protobuf/Empty";
import type {
  GetAgentCardRequest as _a2a_v1_GetAgentCardRequest,
  GetAgentCardRequest__Output as _a2a_v1_GetAgentCardRequest__Output,
} from "../../a2a/v1/GetAgentCardRequest";
import type {
  GetTaskPushNotificationConfigRequest as _a2a_v1_GetTaskPushNotificationConfigRequest,
  GetTaskPushNotificationConfigRequest__Output as _a2a_v1_GetTaskPushNotificationConfigRequest__Output,
} from "../../a2a/v1/GetTaskPushNotificationConfigRequest";
import type {
  GetTaskRequest as _a2a_v1_GetTaskRequest,
  GetTaskRequest__Output as _a2a_v1_GetTaskRequest__Output,
} from "../../a2a/v1/GetTaskRequest";
import type {
  ListTaskPushNotificationConfigRequest as _a2a_v1_ListTaskPushNotificationConfigRequest,
  ListTaskPushNotificationConfigRequest__Output as _a2a_v1_ListTaskPushNotificationConfigRequest__Output,
} from "../../a2a/v1/ListTaskPushNotificationConfigRequest";
import type {
  ListTaskPushNotificationConfigResponse as _a2a_v1_ListTaskPushNotificationConfigResponse,
  ListTaskPushNotificationConfigResponse__Output as _a2a_v1_ListTaskPushNotificationConfigResponse__Output,
} from "../../a2a/v1/ListTaskPushNotificationConfigResponse";
import type {
  SendMessageRequest as _a2a_v1_SendMessageRequest,
  SendMessageRequest__Output as _a2a_v1_SendMessageRequest__Output,
} from "../../a2a/v1/SendMessageRequest";
import type {
  SendMessageResponse as _a2a_v1_SendMessageResponse,
  SendMessageResponse__Output as _a2a_v1_SendMessageResponse__Output,
} from "../../a2a/v1/SendMessageResponse";
import type {
  StreamResponse as _a2a_v1_StreamResponse,
  StreamResponse__Output as _a2a_v1_StreamResponse__Output,
} from "../../a2a/v1/StreamResponse";
import type {
  Task as _a2a_v1_Task,
  Task__Output as _a2a_v1_Task__Output,
} from "../../a2a/v1/Task";
import type {
  TaskPushNotificationConfig as _a2a_v1_TaskPushNotificationConfig,
  TaskPushNotificationConfig__Output as _a2a_v1_TaskPushNotificationConfig__Output,
} from "../../a2a/v1/TaskPushNotificationConfig";
import type {
  TaskSubscriptionRequest as _a2a_v1_TaskSubscriptionRequest,
  TaskSubscriptionRequest__Output as _a2a_v1_TaskSubscriptionRequest__Output,
} from "../../a2a/v1/TaskSubscriptionRequest";

/**
 * A2AService defines the gRPC version of the A2A protocol. This has a slightly
 * different shape than the JSONRPC version to better conform to AIP-127,
 * where appropriate. The nouns are AgentCard, Message, Task and
 * TaskPushNotificationConfig.
 * - Messages are not a standard resource so there is no get/delete/update/list
 * interface, only a send and stream custom methods.
 * - Tasks have a get interface and custom cancel and subscribe methods.
 * - TaskPushNotificationConfig are a resource whose parent is a task.
 * They have get, list and create methods.
 * - AgentCard is a static resource with only a get method.
 */
export interface A2AServiceClient extends grpc.Client {
  /**
   * Cancel a task from the agent. If supported one should expect no
   * more task updates for the task.
   */
  CancelTask(
    argument: _a2a_v1_CancelTaskRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  CancelTask(
    argument: _a2a_v1_CancelTaskRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  CancelTask(
    argument: _a2a_v1_CancelTaskRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  CancelTask(
    argument: _a2a_v1_CancelTaskRequest,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  /**
   * Cancel a task from the agent. If supported one should expect no
   * more task updates for the task.
   */
  cancelTask(
    argument: _a2a_v1_CancelTaskRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  cancelTask(
    argument: _a2a_v1_CancelTaskRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  cancelTask(
    argument: _a2a_v1_CancelTaskRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  cancelTask(
    argument: _a2a_v1_CancelTaskRequest,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;

  /**
   * Set a push notification config for a task.
   */
  CreateTaskPushNotificationConfig(
    argument: _a2a_v1_CreateTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  CreateTaskPushNotificationConfig(
    argument: _a2a_v1_CreateTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  CreateTaskPushNotificationConfig(
    argument: _a2a_v1_CreateTaskPushNotificationConfigRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  CreateTaskPushNotificationConfig(
    argument: _a2a_v1_CreateTaskPushNotificationConfigRequest,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  /**
   * Set a push notification config for a task.
   */
  createTaskPushNotificationConfig(
    argument: _a2a_v1_CreateTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  createTaskPushNotificationConfig(
    argument: _a2a_v1_CreateTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  createTaskPushNotificationConfig(
    argument: _a2a_v1_CreateTaskPushNotificationConfigRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  createTaskPushNotificationConfig(
    argument: _a2a_v1_CreateTaskPushNotificationConfigRequest,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;

  /**
   * Delete a push notification config for a task.
   */
  DeleteTaskPushNotificationConfig(
    argument: _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_google_protobuf_Empty__Output>
  ): grpc.ClientUnaryCall;
  DeleteTaskPushNotificationConfig(
    argument: _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_google_protobuf_Empty__Output>
  ): grpc.ClientUnaryCall;
  DeleteTaskPushNotificationConfig(
    argument: _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_google_protobuf_Empty__Output>
  ): grpc.ClientUnaryCall;
  DeleteTaskPushNotificationConfig(
    argument: _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    callback: grpc.requestCallback<_google_protobuf_Empty__Output>
  ): grpc.ClientUnaryCall;
  /**
   * Delete a push notification config for a task.
   */
  deleteTaskPushNotificationConfig(
    argument: _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_google_protobuf_Empty__Output>
  ): grpc.ClientUnaryCall;
  deleteTaskPushNotificationConfig(
    argument: _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_google_protobuf_Empty__Output>
  ): grpc.ClientUnaryCall;
  deleteTaskPushNotificationConfig(
    argument: _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_google_protobuf_Empty__Output>
  ): grpc.ClientUnaryCall;
  deleteTaskPushNotificationConfig(
    argument: _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    callback: grpc.requestCallback<_google_protobuf_Empty__Output>
  ): grpc.ClientUnaryCall;

  /**
   * GetAgentCard returns the agent card for the agent.
   */
  GetAgentCard(
    argument: _a2a_v1_GetAgentCardRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_AgentCard__Output>
  ): grpc.ClientUnaryCall;
  GetAgentCard(
    argument: _a2a_v1_GetAgentCardRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_AgentCard__Output>
  ): grpc.ClientUnaryCall;
  GetAgentCard(
    argument: _a2a_v1_GetAgentCardRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_AgentCard__Output>
  ): grpc.ClientUnaryCall;
  GetAgentCard(
    argument: _a2a_v1_GetAgentCardRequest,
    callback: grpc.requestCallback<_a2a_v1_AgentCard__Output>
  ): grpc.ClientUnaryCall;
  /**
   * GetAgentCard returns the agent card for the agent.
   */
  getAgentCard(
    argument: _a2a_v1_GetAgentCardRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_AgentCard__Output>
  ): grpc.ClientUnaryCall;
  getAgentCard(
    argument: _a2a_v1_GetAgentCardRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_AgentCard__Output>
  ): grpc.ClientUnaryCall;
  getAgentCard(
    argument: _a2a_v1_GetAgentCardRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_AgentCard__Output>
  ): grpc.ClientUnaryCall;
  getAgentCard(
    argument: _a2a_v1_GetAgentCardRequest,
    callback: grpc.requestCallback<_a2a_v1_AgentCard__Output>
  ): grpc.ClientUnaryCall;

  /**
   * Get the current state of a task from the agent.
   */
  GetTask(
    argument: _a2a_v1_GetTaskRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  GetTask(
    argument: _a2a_v1_GetTaskRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  GetTask(
    argument: _a2a_v1_GetTaskRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  GetTask(
    argument: _a2a_v1_GetTaskRequest,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  /**
   * Get the current state of a task from the agent.
   */
  getTask(
    argument: _a2a_v1_GetTaskRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  getTask(
    argument: _a2a_v1_GetTaskRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  getTask(
    argument: _a2a_v1_GetTaskRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;
  getTask(
    argument: _a2a_v1_GetTaskRequest,
    callback: grpc.requestCallback<_a2a_v1_Task__Output>
  ): grpc.ClientUnaryCall;

  /**
   * Get a push notification config for a task.
   */
  GetTaskPushNotificationConfig(
    argument: _a2a_v1_GetTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  GetTaskPushNotificationConfig(
    argument: _a2a_v1_GetTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  GetTaskPushNotificationConfig(
    argument: _a2a_v1_GetTaskPushNotificationConfigRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  GetTaskPushNotificationConfig(
    argument: _a2a_v1_GetTaskPushNotificationConfigRequest,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  /**
   * Get a push notification config for a task.
   */
  getTaskPushNotificationConfig(
    argument: _a2a_v1_GetTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  getTaskPushNotificationConfig(
    argument: _a2a_v1_GetTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  getTaskPushNotificationConfig(
    argument: _a2a_v1_GetTaskPushNotificationConfigRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;
  getTaskPushNotificationConfig(
    argument: _a2a_v1_GetTaskPushNotificationConfigRequest,
    callback: grpc.requestCallback<_a2a_v1_TaskPushNotificationConfig__Output>
  ): grpc.ClientUnaryCall;

  /**
   * Get a list of push notifications configured for a task.
   */
  ListTaskPushNotificationConfig(
    argument: _a2a_v1_ListTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_ListTaskPushNotificationConfigResponse__Output>
  ): grpc.ClientUnaryCall;
  ListTaskPushNotificationConfig(
    argument: _a2a_v1_ListTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_ListTaskPushNotificationConfigResponse__Output>
  ): grpc.ClientUnaryCall;
  ListTaskPushNotificationConfig(
    argument: _a2a_v1_ListTaskPushNotificationConfigRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_ListTaskPushNotificationConfigResponse__Output>
  ): grpc.ClientUnaryCall;
  ListTaskPushNotificationConfig(
    argument: _a2a_v1_ListTaskPushNotificationConfigRequest,
    callback: grpc.requestCallback<_a2a_v1_ListTaskPushNotificationConfigResponse__Output>
  ): grpc.ClientUnaryCall;
  /**
   * Get a list of push notifications configured for a task.
   */
  listTaskPushNotificationConfig(
    argument: _a2a_v1_ListTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_ListTaskPushNotificationConfigResponse__Output>
  ): grpc.ClientUnaryCall;
  listTaskPushNotificationConfig(
    argument: _a2a_v1_ListTaskPushNotificationConfigRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_ListTaskPushNotificationConfigResponse__Output>
  ): grpc.ClientUnaryCall;
  listTaskPushNotificationConfig(
    argument: _a2a_v1_ListTaskPushNotificationConfigRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_ListTaskPushNotificationConfigResponse__Output>
  ): grpc.ClientUnaryCall;
  listTaskPushNotificationConfig(
    argument: _a2a_v1_ListTaskPushNotificationConfigRequest,
    callback: grpc.requestCallback<_a2a_v1_ListTaskPushNotificationConfigResponse__Output>
  ): grpc.ClientUnaryCall;

  /**
   * Send a message to the agent. This is a blocking call that will return the
   * task once it is completed, or a LRO if requested.
   */
  SendMessage(
    argument: _a2a_v1_SendMessageRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_SendMessageResponse__Output>
  ): grpc.ClientUnaryCall;
  SendMessage(
    argument: _a2a_v1_SendMessageRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_SendMessageResponse__Output>
  ): grpc.ClientUnaryCall;
  SendMessage(
    argument: _a2a_v1_SendMessageRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_SendMessageResponse__Output>
  ): grpc.ClientUnaryCall;
  SendMessage(
    argument: _a2a_v1_SendMessageRequest,
    callback: grpc.requestCallback<_a2a_v1_SendMessageResponse__Output>
  ): grpc.ClientUnaryCall;
  /**
   * Send a message to the agent. This is a blocking call that will return the
   * task once it is completed, or a LRO if requested.
   */
  sendMessage(
    argument: _a2a_v1_SendMessageRequest,
    metadata: grpc.Metadata,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_SendMessageResponse__Output>
  ): grpc.ClientUnaryCall;
  sendMessage(
    argument: _a2a_v1_SendMessageRequest,
    metadata: grpc.Metadata,
    callback: grpc.requestCallback<_a2a_v1_SendMessageResponse__Output>
  ): grpc.ClientUnaryCall;
  sendMessage(
    argument: _a2a_v1_SendMessageRequest,
    options: grpc.CallOptions,
    callback: grpc.requestCallback<_a2a_v1_SendMessageResponse__Output>
  ): grpc.ClientUnaryCall;
  sendMessage(
    argument: _a2a_v1_SendMessageRequest,
    callback: grpc.requestCallback<_a2a_v1_SendMessageResponse__Output>
  ): grpc.ClientUnaryCall;

  /**
   * SendStreamingMessage is a streaming call that will return a stream of
   * task update events until the Task is in an interrupted or terminal state.
   */
  SendStreamingMessage(
    argument: _a2a_v1_SendMessageRequest,
    metadata: grpc.Metadata,
    options?: grpc.CallOptions
  ): grpc.ClientReadableStream<_a2a_v1_StreamResponse__Output>;
  SendStreamingMessage(
    argument: _a2a_v1_SendMessageRequest,
    options?: grpc.CallOptions
  ): grpc.ClientReadableStream<_a2a_v1_StreamResponse__Output>;
  /**
   * SendStreamingMessage is a streaming call that will return a stream of
   * task update events until the Task is in an interrupted or terminal state.
   */
  sendStreamingMessage(
    argument: _a2a_v1_SendMessageRequest,
    metadata: grpc.Metadata,
    options?: grpc.CallOptions
  ): grpc.ClientReadableStream<_a2a_v1_StreamResponse__Output>;
  sendStreamingMessage(
    argument: _a2a_v1_SendMessageRequest,
    options?: grpc.CallOptions
  ): grpc.ClientReadableStream<_a2a_v1_StreamResponse__Output>;

  /**
   * TaskSubscription is a streaming call that will return a stream of task
   * update events. This attaches the stream to an existing in process task.
   * If the task is complete the stream will return the completed task (like
   * GetTask) and close the stream.
   */
  TaskSubscription(
    argument: _a2a_v1_TaskSubscriptionRequest,
    metadata: grpc.Metadata,
    options?: grpc.CallOptions
  ): grpc.ClientReadableStream<_a2a_v1_StreamResponse__Output>;
  TaskSubscription(
    argument: _a2a_v1_TaskSubscriptionRequest,
    options?: grpc.CallOptions
  ): grpc.ClientReadableStream<_a2a_v1_StreamResponse__Output>;
  /**
   * TaskSubscription is a streaming call that will return a stream of task
   * update events. This attaches the stream to an existing in process task.
   * If the task is complete the stream will return the completed task (like
   * GetTask) and close the stream.
   */
  taskSubscription(
    argument: _a2a_v1_TaskSubscriptionRequest,
    metadata: grpc.Metadata,
    options?: grpc.CallOptions
  ): grpc.ClientReadableStream<_a2a_v1_StreamResponse__Output>;
  taskSubscription(
    argument: _a2a_v1_TaskSubscriptionRequest,
    options?: grpc.CallOptions
  ): grpc.ClientReadableStream<_a2a_v1_StreamResponse__Output>;
}

/**
 * A2AService defines the gRPC version of the A2A protocol. This has a slightly
 * different shape than the JSONRPC version to better conform to AIP-127,
 * where appropriate. The nouns are AgentCard, Message, Task and
 * TaskPushNotificationConfig.
 * - Messages are not a standard resource so there is no get/delete/update/list
 * interface, only a send and stream custom methods.
 * - Tasks have a get interface and custom cancel and subscribe methods.
 * - TaskPushNotificationConfig are a resource whose parent is a task.
 * They have get, list and create methods.
 * - AgentCard is a static resource with only a get method.
 */
export interface A2AServiceHandlers extends grpc.UntypedServiceImplementation {
  /**
   * Cancel a task from the agent. If supported one should expect no
   * more task updates for the task.
   */
  CancelTask: grpc.handleUnaryCall<
    _a2a_v1_CancelTaskRequest__Output,
    _a2a_v1_Task
  >;

  /**
   * Set a push notification config for a task.
   */
  CreateTaskPushNotificationConfig: grpc.handleUnaryCall<
    _a2a_v1_CreateTaskPushNotificationConfigRequest__Output,
    _a2a_v1_TaskPushNotificationConfig
  >;

  /**
   * Delete a push notification config for a task.
   */
  DeleteTaskPushNotificationConfig: grpc.handleUnaryCall<
    _a2a_v1_DeleteTaskPushNotificationConfigRequest__Output,
    _google_protobuf_Empty
  >;

  /**
   * GetAgentCard returns the agent card for the agent.
   */
  GetAgentCard: grpc.handleUnaryCall<
    _a2a_v1_GetAgentCardRequest__Output,
    _a2a_v1_AgentCard
  >;

  /**
   * Get the current state of a task from the agent.
   */
  GetTask: grpc.handleUnaryCall<_a2a_v1_GetTaskRequest__Output, _a2a_v1_Task>;

  /**
   * Get a push notification config for a task.
   */
  GetTaskPushNotificationConfig: grpc.handleUnaryCall<
    _a2a_v1_GetTaskPushNotificationConfigRequest__Output,
    _a2a_v1_TaskPushNotificationConfig
  >;

  /**
   * Get a list of push notifications configured for a task.
   */
  ListTaskPushNotificationConfig: grpc.handleUnaryCall<
    _a2a_v1_ListTaskPushNotificationConfigRequest__Output,
    _a2a_v1_ListTaskPushNotificationConfigResponse
  >;

  /**
   * Send a message to the agent. This is a blocking call that will return the
   * task once it is completed, or a LRO if requested.
   */
  SendMessage: grpc.handleUnaryCall<
    _a2a_v1_SendMessageRequest__Output,
    _a2a_v1_SendMessageResponse
  >;

  /**
   * SendStreamingMessage is a streaming call that will return a stream of
   * task update events until the Task is in an interrupted or terminal state.
   */
  SendStreamingMessage: grpc.handleServerStreamingCall<
    _a2a_v1_SendMessageRequest__Output,
    _a2a_v1_StreamResponse
  >;

  /**
   * TaskSubscription is a streaming call that will return a stream of task
   * update events. This attaches the stream to an existing in process task.
   * If the task is complete the stream will return the completed task (like
   * GetTask) and close the stream.
   */
  TaskSubscription: grpc.handleServerStreamingCall<
    _a2a_v1_TaskSubscriptionRequest__Output,
    _a2a_v1_StreamResponse
  >;
}

export interface A2AServiceDefinition extends grpc.ServiceDefinition {
  CancelTask: MethodDefinition<
    _a2a_v1_CancelTaskRequest,
    _a2a_v1_Task,
    _a2a_v1_CancelTaskRequest__Output,
    _a2a_v1_Task__Output
  >;
  CreateTaskPushNotificationConfig: MethodDefinition<
    _a2a_v1_CreateTaskPushNotificationConfigRequest,
    _a2a_v1_TaskPushNotificationConfig,
    _a2a_v1_CreateTaskPushNotificationConfigRequest__Output,
    _a2a_v1_TaskPushNotificationConfig__Output
  >;
  DeleteTaskPushNotificationConfig: MethodDefinition<
    _a2a_v1_DeleteTaskPushNotificationConfigRequest,
    _google_protobuf_Empty,
    _a2a_v1_DeleteTaskPushNotificationConfigRequest__Output,
    _google_protobuf_Empty__Output
  >;
  GetAgentCard: MethodDefinition<
    _a2a_v1_GetAgentCardRequest,
    _a2a_v1_AgentCard,
    _a2a_v1_GetAgentCardRequest__Output,
    _a2a_v1_AgentCard__Output
  >;
  GetTask: MethodDefinition<
    _a2a_v1_GetTaskRequest,
    _a2a_v1_Task,
    _a2a_v1_GetTaskRequest__Output,
    _a2a_v1_Task__Output
  >;
  GetTaskPushNotificationConfig: MethodDefinition<
    _a2a_v1_GetTaskPushNotificationConfigRequest,
    _a2a_v1_TaskPushNotificationConfig,
    _a2a_v1_GetTaskPushNotificationConfigRequest__Output,
    _a2a_v1_TaskPushNotificationConfig__Output
  >;
  ListTaskPushNotificationConfig: MethodDefinition<
    _a2a_v1_ListTaskPushNotificationConfigRequest,
    _a2a_v1_ListTaskPushNotificationConfigResponse,
    _a2a_v1_ListTaskPushNotificationConfigRequest__Output,
    _a2a_v1_ListTaskPushNotificationConfigResponse__Output
  >;
  SendMessage: MethodDefinition<
    _a2a_v1_SendMessageRequest,
    _a2a_v1_SendMessageResponse,
    _a2a_v1_SendMessageRequest__Output,
    _a2a_v1_SendMessageResponse__Output
  >;
  SendStreamingMessage: MethodDefinition<
    _a2a_v1_SendMessageRequest,
    _a2a_v1_StreamResponse,
    _a2a_v1_SendMessageRequest__Output,
    _a2a_v1_StreamResponse__Output
  >;
  TaskSubscription: MethodDefinition<
    _a2a_v1_TaskSubscriptionRequest,
    _a2a_v1_StreamResponse,
    _a2a_v1_TaskSubscriptionRequest__Output,
    _a2a_v1_StreamResponse__Output
  >;
}
