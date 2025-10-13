// Original file: ../specification/grpc/a2a.proto

import type { TaskPushNotificationConfig as _a2a_v1_TaskPushNotificationConfig, TaskPushNotificationConfig__Output as _a2a_v1_TaskPushNotificationConfig__Output } from '../../a2a/v1/TaskPushNotificationConfig';

/**
 * --8<-- [start:SetTaskPushNotificationConfigRequest]
 */
export interface CreateTaskPushNotificationConfigRequest {
  /**
   * The parent task resource for this config.
   * Format: tasks/{task_id}
   */
  'parent'?: (string);
  /**
   * The ID for the new config.
   */
  'config_id'?: (string);
  /**
   * The configuration to create.
   */
  'config'?: (_a2a_v1_TaskPushNotificationConfig | null);
}

/**
 * --8<-- [start:SetTaskPushNotificationConfigRequest]
 */
export interface CreateTaskPushNotificationConfigRequest__Output {
  /**
   * The parent task resource for this config.
   * Format: tasks/{task_id}
   */
  'parent': (string);
  /**
   * The ID for the new config.
   */
  'config_id': (string);
  /**
   * The configuration to create.
   */
  'config': (_a2a_v1_TaskPushNotificationConfig__Output | null);
}
