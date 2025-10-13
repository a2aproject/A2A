// Original file: ../specification/grpc/a2a.proto

import type { TaskStatus as _a2a_v1_TaskStatus, TaskStatus__Output as _a2a_v1_TaskStatus__Output } from '../../a2a/v1/TaskStatus';
import type { Struct as _google_protobuf_Struct, Struct__Output as _google_protobuf_Struct__Output } from '../../google/protobuf/Struct';

/**
 * --8<-- [start:TaskStatusUpdateEvent]
 * TaskStatusUpdateEvent is a delta even on a task indicating that a task
 * has changed.
 */
export interface TaskStatusUpdateEvent {
  /**
   * The id of the task that is changed
   */
  'task_id'?: (string);
  /**
   * The id of the context that the task belongs to
   */
  'context_id'?: (string);
  /**
   * The new status of the task.
   */
  'status'?: (_a2a_v1_TaskStatus | null);
  /**
   * Whether this is the last status update expected for this task.
   */
  'final'?: (boolean);
  /**
   * Optional metadata to associate with the task update.
   */
  'metadata'?: (_google_protobuf_Struct | null);
}

/**
 * --8<-- [start:TaskStatusUpdateEvent]
 * TaskStatusUpdateEvent is a delta even on a task indicating that a task
 * has changed.
 */
export interface TaskStatusUpdateEvent__Output {
  /**
   * The id of the task that is changed
   */
  'task_id': (string);
  /**
   * The id of the context that the task belongs to
   */
  'context_id': (string);
  /**
   * The new status of the task.
   */
  'status': (_a2a_v1_TaskStatus__Output | null);
  /**
   * Whether this is the last status update expected for this task.
   */
  'final': (boolean);
  /**
   * Optional metadata to associate with the task update.
   */
  'metadata': (_google_protobuf_Struct__Output | null);
}
