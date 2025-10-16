// Original file: ../specification/grpc/a2a.proto

import type {
  AuthenticationInfo as _a2a_v1_AuthenticationInfo,
  AuthenticationInfo__Output as _a2a_v1_AuthenticationInfo__Output,
} from "../../a2a/v1/AuthenticationInfo";

/**
 * --8<-- [start:PushNotificationConfig]
 * Configuration for setting up push notifications for task updates.
 */
export interface PushNotificationConfig {
  /**
   * A unique identifier (e.g. UUID) for this push notification.
   */
  id?: string;
  /**
   * Url to send the notification too
   */
  url?: string;
  /**
   * Token unique for this task/session
   */
  token?: string;
  /**
   * Information about the authentication to sent with the notification
   */
  authentication?: _a2a_v1_AuthenticationInfo | null;
}

/**
 * --8<-- [start:PushNotificationConfig]
 * Configuration for setting up push notifications for task updates.
 */
export interface PushNotificationConfig__Output {
  /**
   * A unique identifier (e.g. UUID) for this push notification.
   */
  id: string;
  /**
   * Url to send the notification too
   */
  url: string;
  /**
   * Token unique for this task/session
   */
  token: string;
  /**
   * Information about the authentication to sent with the notification
   */
  authentication: _a2a_v1_AuthenticationInfo__Output | null;
}
