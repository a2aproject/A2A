// Original file: ../specification/grpc/a2a.proto

import type {
  PushNotificationConfig as _a2a_v1_PushNotificationConfig,
  PushNotificationConfig__Output as _a2a_v1_PushNotificationConfig__Output,
} from "../../a2a/v1/PushNotificationConfig";

/**
 * --8<-- [start:TaskPushNotificationConfig]
 */
export interface TaskPushNotificationConfig {
  /**
   * The resource name of the config.
   * Format: tasks/{task_id}/pushNotificationConfigs/{config_id}
   */
  name?: string;
  /**
   * The push notification configuration details.
   */
  push_notification_config?: _a2a_v1_PushNotificationConfig | null;
}

/**
 * --8<-- [start:TaskPushNotificationConfig]
 */
export interface TaskPushNotificationConfig__Output {
  /**
   * The resource name of the config.
   * Format: tasks/{task_id}/pushNotificationConfigs/{config_id}
   */
  name: string;
  /**
   * The push notification configuration details.
   */
  push_notification_config: _a2a_v1_PushNotificationConfig__Output | null;
}
