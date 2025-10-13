// Original file: node_modules/google-proto-files/google/api/launch_stage.proto

/**
 * The launch stage as defined by [Google Cloud Platform
 * Launch Stages](https://cloud.google.com/terms/launch-stages).
 */
export const LaunchStage = {
  /**
   * Do not use this default value.
   */
  LAUNCH_STAGE_UNSPECIFIED: "LAUNCH_STAGE_UNSPECIFIED",
  /**
   * The feature is not yet implemented. Users can not use it.
   */
  UNIMPLEMENTED: "UNIMPLEMENTED",
  /**
   * Prelaunch features are hidden from users and are only visible internally.
   */
  PRELAUNCH: "PRELAUNCH",
  /**
   * Early Access features are limited to a closed group of testers. To use
   * these features, you must sign up in advance and sign a Trusted Tester
   * agreement (which includes confidentiality provisions). These features may
   * be unstable, changed in backward-incompatible ways, and are not
   * guaranteed to be released.
   */
  EARLY_ACCESS: "EARLY_ACCESS",
  /**
   * Alpha is a limited availability test for releases before they are cleared
   * for widespread use. By Alpha, all significant design issues are resolved
   * and we are in the process of verifying functionality. Alpha customers
   * need to apply for access, agree to applicable terms, and have their
   * projects allowlisted. Alpha releases don't have to be feature complete,
   * no SLAs are provided, and there are no technical support obligations, but
   * they will be far enough along that customers can actually use them in
   * test environments or for limited-use tests -- just like they would in
   * normal production cases.
   */
  ALPHA: "ALPHA",
  /**
   * Beta is the point at which we are ready to open a release for any
   * customer to use. There are no SLA or technical support obligations in a
   * Beta release. Products will be complete from a feature perspective, but
   * may have some open outstanding issues. Beta releases are suitable for
   * limited production use cases.
   */
  BETA: "BETA",
  /**
   * GA features are open to all developers and are considered stable and
   * fully qualified for production use.
   */
  GA: "GA",
  /**
   * Deprecated features are scheduled to be shut down and removed. For more
   * information, see the "Deprecation Policy" section of our [Terms of
   * Service](https://cloud.google.com/terms/)
   * and the [Google Cloud Platform Subject to the Deprecation
   * Policy](https://cloud.google.com/terms/deprecation) documentation.
   */
  DEPRECATED: "DEPRECATED",
} as const;

/**
 * The launch stage as defined by [Google Cloud Platform
 * Launch Stages](https://cloud.google.com/terms/launch-stages).
 */
export type LaunchStage =
  /**
   * Do not use this default value.
   */
  | "LAUNCH_STAGE_UNSPECIFIED"
  | 0
  /**
   * The feature is not yet implemented. Users can not use it.
   */
  | "UNIMPLEMENTED"
  | 6
  /**
   * Prelaunch features are hidden from users and are only visible internally.
   */
  | "PRELAUNCH"
  | 7
  /**
   * Early Access features are limited to a closed group of testers. To use
   * these features, you must sign up in advance and sign a Trusted Tester
   * agreement (which includes confidentiality provisions). These features may
   * be unstable, changed in backward-incompatible ways, and are not
   * guaranteed to be released.
   */
  | "EARLY_ACCESS"
  | 1
  /**
   * Alpha is a limited availability test for releases before they are cleared
   * for widespread use. By Alpha, all significant design issues are resolved
   * and we are in the process of verifying functionality. Alpha customers
   * need to apply for access, agree to applicable terms, and have their
   * projects allowlisted. Alpha releases don't have to be feature complete,
   * no SLAs are provided, and there are no technical support obligations, but
   * they will be far enough along that customers can actually use them in
   * test environments or for limited-use tests -- just like they would in
   * normal production cases.
   */
  | "ALPHA"
  | 2
  /**
   * Beta is the point at which we are ready to open a release for any
   * customer to use. There are no SLA or technical support obligations in a
   * Beta release. Products will be complete from a feature perspective, but
   * may have some open outstanding issues. Beta releases are suitable for
   * limited production use cases.
   */
  | "BETA"
  | 3
  /**
   * GA features are open to all developers and are considered stable and
   * fully qualified for production use.
   */
  | "GA"
  | 4
  /**
   * Deprecated features are scheduled to be shut down and removed. For more
   * information, see the "Deprecation Policy" section of our [Terms of
   * Service](https://cloud.google.com/terms/)
   * and the [Google Cloud Platform Subject to the Deprecation
   * Policy](https://cloud.google.com/terms/deprecation) documentation.
   */
  | "DEPRECATED"
  | 5;

/**
 * The launch stage as defined by [Google Cloud Platform
 * Launch Stages](https://cloud.google.com/terms/launch-stages).
 */
export type LaunchStage__Output =
  (typeof LaunchStage)[keyof typeof LaunchStage];
