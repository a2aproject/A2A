// Original file: ../specification/grpc/a2a.proto

import type { PushNotificationConfig as _a2a_v1_PushNotificationConfig, PushNotificationConfig__Output as _a2a_v1_PushNotificationConfig__Output } from '../../a2a/v1/PushNotificationConfig';

/**
 * --8<-- [start:MessageSendConfiguration]
 * Configuration of a send message request.
 */
export interface SendMessageConfiguration {
  /**
   * The output modes that the agent is expected to respond with.
   */
  'accepted_output_modes'?: (string)[];
  /**
   * A configuration of a webhook that can be used to receive updates
   */
  'push_notification'?: (_a2a_v1_PushNotificationConfig | null);
  /**
   * The maximum number of messages to include in the history. if 0, the
   * history will be unlimited.
   */
  'history_length'?: (number);
  /**
   * If true, the message will be blocking until the task is completed. If
   * false, the message will be non-blocking and the task will be returned
   * immediately. It is the caller's responsibility to check for any task
   * updates.
   */
  'blocking'?: (boolean);
}

/**
 * --8<-- [start:MessageSendConfiguration]
 * Configuration of a send message request.
 */
export interface SendMessageConfiguration__Output {
  /**
   * The output modes that the agent is expected to respond with.
   */
  'accepted_output_modes': (string)[];
  /**
   * A configuration of a webhook that can be used to receive updates
   */
  'push_notification': (_a2a_v1_PushNotificationConfig__Output | null);
  /**
   * The maximum number of messages to include in the history. if 0, the
   * history will be unlimited.
   */
  'history_length': (number);
  /**
   * If true, the message will be blocking until the task is completed. If
   * false, the message will be non-blocking and the task will be returned
   * immediately. It is the caller's responsibility to check for any task
   * updates.
   */
  'blocking': (boolean);
}
