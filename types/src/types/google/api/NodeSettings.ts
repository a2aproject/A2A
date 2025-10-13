// Original file: node_modules/google-proto-files/google/api/client.proto

import type {
  CommonLanguageSettings as _google_api_CommonLanguageSettings,
  CommonLanguageSettings__Output as _google_api_CommonLanguageSettings__Output,
} from "../../google/api/CommonLanguageSettings";

/**
 * Settings for Node client libraries.
 */
export interface NodeSettings {
  /**
   * Some settings.
   */
  common?: _google_api_CommonLanguageSettings | null;
}

/**
 * Settings for Node client libraries.
 */
export interface NodeSettings__Output {
  /**
   * Some settings.
   */
  common: _google_api_CommonLanguageSettings__Output | null;
}
