// Original file: ../specification/grpc/a2a.proto


/**
 * --8<-- [start:DeleteTaskPushNotificationConfigRequest]
 */
export interface DeleteTaskPushNotificationConfigRequest {
  /**
   * The resource name of the config to delete.
   * Format: tasks/{task_id}/pushNotificationConfigs/{config_id}
   */
  'name'?: (string);
}

/**
 * --8<-- [start:DeleteTaskPushNotificationConfigRequest]
 */
export interface DeleteTaskPushNotificationConfigRequest__Output {
  /**
   * The resource name of the config to delete.
   * Format: tasks/{task_id}/pushNotificationConfigs/{config_id}
   */
  'name': (string);
}
