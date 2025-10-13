// Original file: ../specification/grpc/a2a.proto


/**
 * --8<-- [start:GetTaskPushNotificationConfigRequest]
 */
export interface GetTaskPushNotificationConfigRequest {
  /**
   * The resource name of the config to retrieve.
   * Format: tasks/{task_id}/pushNotificationConfigs/{config_id}
   */
  'name'?: (string);
}

/**
 * --8<-- [start:GetTaskPushNotificationConfigRequest]
 */
export interface GetTaskPushNotificationConfigRequest__Output {
  /**
   * The resource name of the config to retrieve.
   * Format: tasks/{task_id}/pushNotificationConfigs/{config_id}
   */
  'name': (string);
}
