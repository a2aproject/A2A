// Original file: node_modules/google-proto-files/google/api/client.proto

import type { ClientLibraryDestination as _google_api_ClientLibraryDestination, ClientLibraryDestination__Output as _google_api_ClientLibraryDestination__Output } from '../../google/api/ClientLibraryDestination';

/**
 * Required information for every language.
 */
export interface CommonLanguageSettings {
  /**
   * Link to automatically generated reference documentation.  Example:
   * https://cloud.google.com/nodejs/docs/reference/asset/latest
   * @deprecated
   */
  'reference_docs_uri'?: (string);
  /**
   * The destination where API teams want this client library to be published.
   */
  'destinations'?: (_google_api_ClientLibraryDestination)[];
}

/**
 * Required information for every language.
 */
export interface CommonLanguageSettings__Output {
  /**
   * Link to automatically generated reference documentation.  Example:
   * https://cloud.google.com/nodejs/docs/reference/asset/latest
   * @deprecated
   */
  'reference_docs_uri': (string);
  /**
   * The destination where API teams want this client library to be published.
   */
  'destinations': (_google_api_ClientLibraryDestination__Output)[];
}
