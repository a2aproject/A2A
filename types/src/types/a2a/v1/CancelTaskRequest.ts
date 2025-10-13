// Original file: ../specification/grpc/a2a.proto

/**
 * --8<-- [start:CancelTaskRequest]
 */
export interface CancelTaskRequest {
  /**
   * The resource name of the task to cancel.
   * Format: tasks/{task_id}
   */
  name?: string;
}

/**
 * --8<-- [start:CancelTaskRequest]
 */
export interface CancelTaskRequest__Output {
  /**
   * The resource name of the task to cancel.
   * Format: tasks/{task_id}
   */
  name: string;
}
