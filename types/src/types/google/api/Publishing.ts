// Original file: node_modules/google-proto-files/google/api/client.proto

import type {
  MethodSettings as _google_api_MethodSettings,
  MethodSettings__Output as _google_api_MethodSettings__Output,
} from "../../google/api/MethodSettings";
import type {
  ClientLibraryOrganization as _google_api_ClientLibraryOrganization,
  ClientLibraryOrganization__Output as _google_api_ClientLibraryOrganization__Output,
} from "../../google/api/ClientLibraryOrganization";
import type {
  ClientLibrarySettings as _google_api_ClientLibrarySettings,
  ClientLibrarySettings__Output as _google_api_ClientLibrarySettings__Output,
} from "../../google/api/ClientLibrarySettings";

/**
 * This message configures the settings for publishing [Google Cloud Client
 * libraries](https://cloud.google.com/apis/docs/cloud-client-libraries)
 * generated from the service config.
 */
export interface Publishing {
  /**
   * A list of API method settings, e.g. the behavior for methods that use the
   * long-running operation pattern.
   */
  method_settings?: _google_api_MethodSettings[];
  /**
   * Link to a place that API users can report issues.  Example:
   * https://issuetracker.google.com/issues/new?component=190865&template=1161103
   */
  new_issue_uri?: string;
  /**
   * Link to product home page.  Example:
   * https://cloud.google.com/asset-inventory/docs/overview
   */
  documentation_uri?: string;
  /**
   * Used as a tracking tag when collecting data about the APIs developer
   * relations artifacts like docs, packages delivered to package managers,
   * etc.  Example: "speech".
   */
  api_short_name?: string;
  /**
   * GitHub label to apply to issues and pull requests opened for this API.
   */
  github_label?: string;
  /**
   * GitHub teams to be added to CODEOWNERS in the directory in GitHub
   * containing source code for the client libraries for this API.
   */
  codeowner_github_teams?: string[];
  /**
   * A prefix used in sample code when demarking regions to be included in
   * documentation.
   */
  doc_tag_prefix?: string;
  /**
   * For whom the client library is being published.
   */
  organization?: _google_api_ClientLibraryOrganization;
  /**
   * Client library settings.  If the same version string appears multiple
   * times in this list, then the last one wins.  Settings from earlier
   * settings with the same version string are discarded.
   */
  library_settings?: _google_api_ClientLibrarySettings[];
}

/**
 * This message configures the settings for publishing [Google Cloud Client
 * libraries](https://cloud.google.com/apis/docs/cloud-client-libraries)
 * generated from the service config.
 */
export interface Publishing__Output {
  /**
   * A list of API method settings, e.g. the behavior for methods that use the
   * long-running operation pattern.
   */
  method_settings: _google_api_MethodSettings__Output[];
  /**
   * Link to a place that API users can report issues.  Example:
   * https://issuetracker.google.com/issues/new?component=190865&template=1161103
   */
  new_issue_uri: string;
  /**
   * Link to product home page.  Example:
   * https://cloud.google.com/asset-inventory/docs/overview
   */
  documentation_uri: string;
  /**
   * Used as a tracking tag when collecting data about the APIs developer
   * relations artifacts like docs, packages delivered to package managers,
   * etc.  Example: "speech".
   */
  api_short_name: string;
  /**
   * GitHub label to apply to issues and pull requests opened for this API.
   */
  github_label: string;
  /**
   * GitHub teams to be added to CODEOWNERS in the directory in GitHub
   * containing source code for the client libraries for this API.
   */
  codeowner_github_teams: string[];
  /**
   * A prefix used in sample code when demarking regions to be included in
   * documentation.
   */
  doc_tag_prefix: string;
  /**
   * For whom the client library is being published.
   */
  organization: _google_api_ClientLibraryOrganization__Output;
  /**
   * Client library settings.  If the same version string appears multiple
   * times in this list, then the last one wins.  Settings from earlier
   * settings with the same version string are discarded.
   */
  library_settings: _google_api_ClientLibrarySettings__Output[];
}
