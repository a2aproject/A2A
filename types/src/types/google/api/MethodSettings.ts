// Original file: node_modules/google-proto-files/google/api/client.proto

import type { Duration as _google_protobuf_Duration, Duration__Output as _google_protobuf_Duration__Output } from '../../google/protobuf/Duration';

/**
 * Describes settings to use when generating API methods that use the
 * long-running operation pattern.
 * All default values below are from those used in the client library
 * generators (e.g.
 * [Java](https://github.com/googleapis/gapic-generator-java/blob/04c2faa191a9b5a10b92392fe8482279c4404803/src/main/java/com/google/api/generator/gapic/composer/common/RetrySettingsComposer.java)).
 */
export interface _google_api_MethodSettings_LongRunning {
  /**
   * Initial delay after which the first poll request will be made.
   * Default value: 5 seconds.
   */
  'initial_poll_delay'?: (_google_protobuf_Duration | null);
  /**
   * Multiplier to gradually increase delay between subsequent polls until it
   * reaches max_poll_delay.
   * Default value: 1.5.
   */
  'poll_delay_multiplier'?: (number | string);
  /**
   * Maximum time between two subsequent poll requests.
   * Default value: 45 seconds.
   */
  'max_poll_delay'?: (_google_protobuf_Duration | null);
  /**
   * Total polling timeout.
   * Default value: 5 minutes.
   */
  'total_poll_timeout'?: (_google_protobuf_Duration | null);
}

/**
 * Describes settings to use when generating API methods that use the
 * long-running operation pattern.
 * All default values below are from those used in the client library
 * generators (e.g.
 * [Java](https://github.com/googleapis/gapic-generator-java/blob/04c2faa191a9b5a10b92392fe8482279c4404803/src/main/java/com/google/api/generator/gapic/composer/common/RetrySettingsComposer.java)).
 */
export interface _google_api_MethodSettings_LongRunning__Output {
  /**
   * Initial delay after which the first poll request will be made.
   * Default value: 5 seconds.
   */
  'initial_poll_delay': (_google_protobuf_Duration__Output | null);
  /**
   * Multiplier to gradually increase delay between subsequent polls until it
   * reaches max_poll_delay.
   * Default value: 1.5.
   */
  'poll_delay_multiplier': (number);
  /**
   * Maximum time between two subsequent poll requests.
   * Default value: 45 seconds.
   */
  'max_poll_delay': (_google_protobuf_Duration__Output | null);
  /**
   * Total polling timeout.
   * Default value: 5 minutes.
   */
  'total_poll_timeout': (_google_protobuf_Duration__Output | null);
}

/**
 * Describes the generator configuration for a method.
 */
export interface MethodSettings {
  /**
   * The fully qualified name of the method, for which the options below apply.
   * This is used to find the method to apply the options.
   */
  'selector'?: (string);
  /**
   * Describes settings to use for long-running operations when generating
   * API methods for RPCs. Complements RPCs that use the annotations in
   * google/longrunning/operations.proto.
   * 
   * Example of a YAML configuration::
   * 
   * publishing:
   * method_behavior:
   * - selector: CreateAdDomain
   * long_running:
   * initial_poll_delay:
   * seconds: 60 # 1 minute
   * poll_delay_multiplier: 1.5
   * max_poll_delay:
   * seconds: 360 # 6 minutes
   * total_poll_timeout:
   * seconds: 54000 # 90 minutes
   */
  'long_running'?: (_google_api_MethodSettings_LongRunning | null);
}

/**
 * Describes the generator configuration for a method.
 */
export interface MethodSettings__Output {
  /**
   * The fully qualified name of the method, for which the options below apply.
   * This is used to find the method to apply the options.
   */
  'selector': (string);
  /**
   * Describes settings to use for long-running operations when generating
   * API methods for RPCs. Complements RPCs that use the annotations in
   * google/longrunning/operations.proto.
   * 
   * Example of a YAML configuration::
   * 
   * publishing:
   * method_behavior:
   * - selector: CreateAdDomain
   * long_running:
   * initial_poll_delay:
   * seconds: 60 # 1 minute
   * poll_delay_multiplier: 1.5
   * max_poll_delay:
   * seconds: 360 # 6 minutes
   * total_poll_timeout:
   * seconds: 54000 # 90 minutes
   */
  'long_running': (_google_api_MethodSettings_LongRunning__Output | null);
}
