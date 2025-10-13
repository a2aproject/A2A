// Original file: ../specification/grpc/a2a.proto

import type { TaskPushNotificationConfig as _a2a_v1_TaskPushNotificationConfig, TaskPushNotificationConfig__Output as _a2a_v1_TaskPushNotificationConfig__Output } from '../../a2a/v1/TaskPushNotificationConfig';

/**
 * --8<-- [start:ListTaskPushNotificationConfigSuccessResponse]
 */
export interface ListTaskPushNotificationConfigResponse {
  /**
   * The list of push notification configurations.
   */
  'configs'?: (_a2a_v1_TaskPushNotificationConfig)[];
  /**
   * A token, which can be sent as `page_token` to retrieve the next page.
   * If this field is omitted, there are no subsequent pages.
   */
  'next_page_token'?: (string);
}

/**
 * --8<-- [start:ListTaskPushNotificationConfigSuccessResponse]
 */
export interface ListTaskPushNotificationConfigResponse__Output {
  /**
   * The list of push notification configurations.
   */
  'configs': (_a2a_v1_TaskPushNotificationConfig__Output)[];
  /**
   * A token, which can be sent as `page_token` to retrieve the next page.
   * If this field is omitted, there are no subsequent pages.
   */
  'next_page_token': (string);
}
