// Original file: node_modules/google-proto-files/google/api/client.proto

/**
 * To where should client libraries be published?
 */
export const ClientLibraryDestination = {
  /**
   * Client libraries will neither be generated nor published to package
   * managers.
   */
  CLIENT_LIBRARY_DESTINATION_UNSPECIFIED:
    "CLIENT_LIBRARY_DESTINATION_UNSPECIFIED",
  /**
   * Generate the client library in a repo under github.com/googleapis,
   * but don't publish it to package managers.
   */
  GITHUB: "GITHUB",
  /**
   * Publish the library to package managers like nuget.org and npmjs.com.
   */
  PACKAGE_MANAGER: "PACKAGE_MANAGER",
} as const;

/**
 * To where should client libraries be published?
 */
export type ClientLibraryDestination =
  /**
   * Client libraries will neither be generated nor published to package
   * managers.
   */
  | "CLIENT_LIBRARY_DESTINATION_UNSPECIFIED"
  | 0
  /**
   * Generate the client library in a repo under github.com/googleapis,
   * but don't publish it to package managers.
   */
  | "GITHUB"
  | 10
  /**
   * Publish the library to package managers like nuget.org and npmjs.com.
   */
  | "PACKAGE_MANAGER"
  | 20;

/**
 * To where should client libraries be published?
 */
export type ClientLibraryDestination__Output =
  (typeof ClientLibraryDestination)[keyof typeof ClientLibraryDestination];
