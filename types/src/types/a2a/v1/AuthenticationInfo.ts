// Original file: ../specification/grpc/a2a.proto

/**
 * --8<-- [start:PushNotificationAuthenticationInfo]
 * Defines authentication details, used for push notifications.
 */
export interface AuthenticationInfo {
  /**
   * Supported authentication schemes - e.g. Basic, Bearer, etc
   */
  schemes?: string[];
  /**
   * Optional credentials
   */
  credentials?: string;
}

/**
 * --8<-- [start:PushNotificationAuthenticationInfo]
 * Defines authentication details, used for push notifications.
 */
export interface AuthenticationInfo__Output {
  /**
   * Supported authentication schemes - e.g. Basic, Bearer, etc
   */
  schemes: string[];
  /**
   * Optional credentials
   */
  credentials: string;
}
