// Original file: node_modules/google-proto-files/google/api/client.proto

/**
 * The organization for which the client libraries are being published.
 * Affects the url where generated docs are published, etc.
 */
export const ClientLibraryOrganization = {
  /**
   * Not useful.
   */
  CLIENT_LIBRARY_ORGANIZATION_UNSPECIFIED:
    "CLIENT_LIBRARY_ORGANIZATION_UNSPECIFIED",
  /**
   * Google Cloud Platform Org.
   */
  CLOUD: "CLOUD",
  /**
   * Ads (Advertising) Org.
   */
  ADS: "ADS",
  /**
   * Photos Org.
   */
  PHOTOS: "PHOTOS",
  /**
   * Street View Org.
   */
  STREET_VIEW: "STREET_VIEW",
} as const;

/**
 * The organization for which the client libraries are being published.
 * Affects the url where generated docs are published, etc.
 */
export type ClientLibraryOrganization =
  /**
   * Not useful.
   */
  | "CLIENT_LIBRARY_ORGANIZATION_UNSPECIFIED"
  | 0
  /**
   * Google Cloud Platform Org.
   */
  | "CLOUD"
  | 1
  /**
   * Ads (Advertising) Org.
   */
  | "ADS"
  | 2
  /**
   * Photos Org.
   */
  | "PHOTOS"
  | 3
  /**
   * Street View Org.
   */
  | "STREET_VIEW"
  | 4;

/**
 * The organization for which the client libraries are being published.
 * Affects the url where generated docs are published, etc.
 */
export type ClientLibraryOrganization__Output =
  (typeof ClientLibraryOrganization)[keyof typeof ClientLibraryOrganization];
