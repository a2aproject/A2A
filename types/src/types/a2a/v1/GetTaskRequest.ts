// Original file: ../specification/grpc/a2a.proto


/**
 * --8<-- [start:GetTaskRequest]
 */
export interface GetTaskRequest {
  /**
   * The resource name of the task.
   * Format: tasks/{task_id}
   */
  'name'?: (string);
  /**
   * The number of most recent messages from the task's history to retrieve.
   */
  'history_length'?: (number);
}

/**
 * --8<-- [start:GetTaskRequest]
 */
export interface GetTaskRequest__Output {
  /**
   * The resource name of the task.
   * Format: tasks/{task_id}
   */
  'name': (string);
  /**
   * The number of most recent messages from the task's history to retrieve.
   */
  'history_length': (number);
}
