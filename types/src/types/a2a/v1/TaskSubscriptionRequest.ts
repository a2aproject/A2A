// Original file: ../specification/grpc/a2a.proto


/**
 * --8<-- [start:TaskResubscriptionRequest]
 */
export interface TaskSubscriptionRequest {
  /**
   * The resource name of the task to subscribe to.
   * Format: tasks/{task_id}
   */
  'name'?: (string);
}

/**
 * --8<-- [start:TaskResubscriptionRequest]
 */
export interface TaskSubscriptionRequest__Output {
  /**
   * The resource name of the task to subscribe to.
   * Format: tasks/{task_id}
   */
  'name': (string);
}
