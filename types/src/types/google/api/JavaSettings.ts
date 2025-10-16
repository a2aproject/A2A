// Original file: node_modules/google-proto-files/google/api/client.proto

import type {
  CommonLanguageSettings as _google_api_CommonLanguageSettings,
  CommonLanguageSettings__Output as _google_api_CommonLanguageSettings__Output,
} from "../../google/api/CommonLanguageSettings";

/**
 * Settings for Java client libraries.
 */
export interface JavaSettings {
  /**
   * The package name to use in Java. Clobbers the java_package option
   * set in the protobuf. This should be used **only** by APIs
   * who have already set the language_settings.java.package_name" field
   * in gapic.yaml. API teams should use the protobuf java_package option
   * where possible.
   *
   * Example of a YAML configuration::
   *
   * publishing:
   * java_settings:
   * library_package: com.google.cloud.pubsub.v1
   */
  library_package?: string;
  /**
   * Configure the Java class name to use instead of the service's for its
   * corresponding generated GAPIC client. Keys are fully-qualified
   * service names as they appear in the protobuf (including the full
   * the language_settings.java.interface_names" field in gapic.yaml. API
   * teams should otherwise use the service name as it appears in the
   * protobuf.
   *
   * Example of a YAML configuration::
   *
   * publishing:
   * java_settings:
   * service_class_names:
   * - google.pubsub.v1.Publisher: TopicAdmin
   * - google.pubsub.v1.Subscriber: SubscriptionAdmin
   */
  service_class_names?: { [key: string]: string };
  /**
   * Some settings.
   */
  common?: _google_api_CommonLanguageSettings | null;
}

/**
 * Settings for Java client libraries.
 */
export interface JavaSettings__Output {
  /**
   * The package name to use in Java. Clobbers the java_package option
   * set in the protobuf. This should be used **only** by APIs
   * who have already set the language_settings.java.package_name" field
   * in gapic.yaml. API teams should use the protobuf java_package option
   * where possible.
   *
   * Example of a YAML configuration::
   *
   * publishing:
   * java_settings:
   * library_package: com.google.cloud.pubsub.v1
   */
  library_package: string;
  /**
   * Configure the Java class name to use instead of the service's for its
   * corresponding generated GAPIC client. Keys are fully-qualified
   * service names as they appear in the protobuf (including the full
   * the language_settings.java.interface_names" field in gapic.yaml. API
   * teams should otherwise use the service name as it appears in the
   * protobuf.
   *
   * Example of a YAML configuration::
   *
   * publishing:
   * java_settings:
   * service_class_names:
   * - google.pubsub.v1.Publisher: TopicAdmin
   * - google.pubsub.v1.Subscriber: SubscriptionAdmin
   */
  service_class_names: { [key: string]: string };
  /**
   * Some settings.
   */
  common: _google_api_CommonLanguageSettings__Output | null;
}
