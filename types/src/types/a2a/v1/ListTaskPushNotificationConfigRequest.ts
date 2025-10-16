// Original file: ../specification/grpc/a2a.proto

/**
 * --8<-- [start:ListTaskPushNotificationConfigRequest]
 */
export interface ListTaskPushNotificationConfigRequest {
  /**
   * The parent task resource.
   * Format: tasks/{task_id}
   */
  parent?: string;
  /**
   * For AIP-158 these fields are present. Usually not used/needed.
   * The maximum number of configurations to return.
   * If unspecified, all configs will be returned.
   */
  page_size?: number;
  /**
   * A page token received from a previous
   * ListTaskPushNotificationConfigRequest call.
   * Provide this to retrieve the subsequent page.
   * When paginating, all other parameters provided to
   * `ListTaskPushNotificationConfigRequest` must match the call that provided
   * the page token.
   */
  page_token?: string;
}

/**
 * --8<-- [start:ListTaskPushNotificationConfigRequest]
 */
export interface ListTaskPushNotificationConfigRequest__Output {
  /**
   * The parent task resource.
   * Format: tasks/{task_id}
   */
  parent: string;
  /**
   * For AIP-158 these fields are present. Usually not used/needed.
   * The maximum number of configurations to return.
   * If unspecified, all configs will be returned.
   */
  page_size: number;
  /**
   * A page token received from a previous
   * ListTaskPushNotificationConfigRequest call.
   * Provide this to retrieve the subsequent page.
   * When paginating, all other parameters provided to
   * `ListTaskPushNotificationConfigRequest` must match the call that provided
   * the page token.
   */
  page_token: string;
}
