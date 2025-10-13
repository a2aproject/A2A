// Original file: node_modules/google-proto-files/google/api/client.proto

import type { LaunchStage as _google_api_LaunchStage, LaunchStage__Output as _google_api_LaunchStage__Output } from '../../google/api/LaunchStage';
import type { JavaSettings as _google_api_JavaSettings, JavaSettings__Output as _google_api_JavaSettings__Output } from '../../google/api/JavaSettings';
import type { CppSettings as _google_api_CppSettings, CppSettings__Output as _google_api_CppSettings__Output } from '../../google/api/CppSettings';
import type { PhpSettings as _google_api_PhpSettings, PhpSettings__Output as _google_api_PhpSettings__Output } from '../../google/api/PhpSettings';
import type { PythonSettings as _google_api_PythonSettings, PythonSettings__Output as _google_api_PythonSettings__Output } from '../../google/api/PythonSettings';
import type { NodeSettings as _google_api_NodeSettings, NodeSettings__Output as _google_api_NodeSettings__Output } from '../../google/api/NodeSettings';
import type { DotnetSettings as _google_api_DotnetSettings, DotnetSettings__Output as _google_api_DotnetSettings__Output } from '../../google/api/DotnetSettings';
import type { RubySettings as _google_api_RubySettings, RubySettings__Output as _google_api_RubySettings__Output } from '../../google/api/RubySettings';
import type { GoSettings as _google_api_GoSettings, GoSettings__Output as _google_api_GoSettings__Output } from '../../google/api/GoSettings';

/**
 * Details about how and where to publish client libraries.
 */
export interface ClientLibrarySettings {
  /**
   * Version of the API to apply these settings to.
   */
  'version'?: (string);
  /**
   * Launch stage of this version of the API.
   */
  'launch_stage'?: (_google_api_LaunchStage);
  /**
   * When using transport=rest, the client request will encode enums as
   * numbers rather than strings.
   */
  'rest_numeric_enums'?: (boolean);
  /**
   * Settings for legacy Java features, supported in the Service YAML.
   */
  'java_settings'?: (_google_api_JavaSettings | null);
  /**
   * Settings for C++ client libraries.
   */
  'cpp_settings'?: (_google_api_CppSettings | null);
  /**
   * Settings for PHP client libraries.
   */
  'php_settings'?: (_google_api_PhpSettings | null);
  /**
   * Settings for Python client libraries.
   */
  'python_settings'?: (_google_api_PythonSettings | null);
  /**
   * Settings for Node client libraries.
   */
  'node_settings'?: (_google_api_NodeSettings | null);
  /**
   * Settings for .NET client libraries.
   */
  'dotnet_settings'?: (_google_api_DotnetSettings | null);
  /**
   * Settings for Ruby client libraries.
   */
  'ruby_settings'?: (_google_api_RubySettings | null);
  /**
   * Settings for Go client libraries.
   */
  'go_settings'?: (_google_api_GoSettings | null);
}

/**
 * Details about how and where to publish client libraries.
 */
export interface ClientLibrarySettings__Output {
  /**
   * Version of the API to apply these settings to.
   */
  'version': (string);
  /**
   * Launch stage of this version of the API.
   */
  'launch_stage': (_google_api_LaunchStage__Output);
  /**
   * When using transport=rest, the client request will encode enums as
   * numbers rather than strings.
   */
  'rest_numeric_enums': (boolean);
  /**
   * Settings for legacy Java features, supported in the Service YAML.
   */
  'java_settings': (_google_api_JavaSettings__Output | null);
  /**
   * Settings for C++ client libraries.
   */
  'cpp_settings': (_google_api_CppSettings__Output | null);
  /**
   * Settings for PHP client libraries.
   */
  'php_settings': (_google_api_PhpSettings__Output | null);
  /**
   * Settings for Python client libraries.
   */
  'python_settings': (_google_api_PythonSettings__Output | null);
  /**
   * Settings for Node client libraries.
   */
  'node_settings': (_google_api_NodeSettings__Output | null);
  /**
   * Settings for .NET client libraries.
   */
  'dotnet_settings': (_google_api_DotnetSettings__Output | null);
  /**
   * Settings for Ruby client libraries.
   */
  'ruby_settings': (_google_api_RubySettings__Output | null);
  /**
   * Settings for Go client libraries.
   */
  'go_settings': (_google_api_GoSettings__Output | null);
}
