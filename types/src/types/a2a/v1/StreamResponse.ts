// Original file: ../specification/grpc/a2a.proto

import type { Task as _a2a_v1_Task, Task__Output as _a2a_v1_Task__Output } from '../../a2a/v1/Task';
import type { Message as _a2a_v1_Message, Message__Output as _a2a_v1_Message__Output } from '../../a2a/v1/Message';
import type { TaskStatusUpdateEvent as _a2a_v1_TaskStatusUpdateEvent, TaskStatusUpdateEvent__Output as _a2a_v1_TaskStatusUpdateEvent__Output } from '../../a2a/v1/TaskStatusUpdateEvent';
import type { TaskArtifactUpdateEvent as _a2a_v1_TaskArtifactUpdateEvent, TaskArtifactUpdateEvent__Output as _a2a_v1_TaskArtifactUpdateEvent__Output } from '../../a2a/v1/TaskArtifactUpdateEvent';

/**
 * --8<-- [start:SendStreamingMessageSuccessResponse]
 * The stream response for a message. The stream should be one of the following
 * sequences:
 * If the response is a message, the stream should contain one, and only one,
 * message and then close
 * If the response is a task lifecycle, the first response should be a Task
 * object followed by zero or more TaskStatusUpdateEvents and
 * TaskArtifactUpdateEvents. The stream should complete when the Task
 * if in an interrupted or terminal state. A stream that ends before these
 * conditions are met are
 */
export interface StreamResponse {
  'task'?: (_a2a_v1_Task | null);
  'msg'?: (_a2a_v1_Message | null);
  'status_update'?: (_a2a_v1_TaskStatusUpdateEvent | null);
  'artifact_update'?: (_a2a_v1_TaskArtifactUpdateEvent | null);
  'payload'?: "task"|"msg"|"status_update"|"artifact_update";
}

/**
 * --8<-- [start:SendStreamingMessageSuccessResponse]
 * The stream response for a message. The stream should be one of the following
 * sequences:
 * If the response is a message, the stream should contain one, and only one,
 * message and then close
 * If the response is a task lifecycle, the first response should be a Task
 * object followed by zero or more TaskStatusUpdateEvents and
 * TaskArtifactUpdateEvents. The stream should complete when the Task
 * if in an interrupted or terminal state. A stream that ends before these
 * conditions are met are
 */
export interface StreamResponse__Output {
  'task'?: (_a2a_v1_Task__Output | null);
  'msg'?: (_a2a_v1_Message__Output | null);
  'status_update'?: (_a2a_v1_TaskStatusUpdateEvent__Output | null);
  'artifact_update'?: (_a2a_v1_TaskArtifactUpdateEvent__Output | null);
  'payload'?: "task"|"msg"|"status_update"|"artifact_update";
}
