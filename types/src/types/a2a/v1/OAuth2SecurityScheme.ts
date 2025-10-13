// Original file: ../specification/grpc/a2a.proto

import type {
  OAuthFlows as _a2a_v1_OAuthFlows,
  OAuthFlows__Output as _a2a_v1_OAuthFlows__Output,
} from "../../a2a/v1/OAuthFlows";

/**
 * --8<-- [start:OAuth2SecurityScheme]
 */
export interface OAuth2SecurityScheme {
  /**
   * Description of this security scheme.
   */
  description?: string;
  /**
   * An object containing configuration information for the flow types supported
   */
  flows?: _a2a_v1_OAuthFlows | null;
  /**
   * URL to the oauth2 authorization server metadata
   * [RFC8414](https://datatracker.ietf.org/doc/html/rfc8414). TLS is required.
   */
  oauth2_metadata_url?: string;
}

/**
 * --8<-- [start:OAuth2SecurityScheme]
 */
export interface OAuth2SecurityScheme__Output {
  /**
   * Description of this security scheme.
   */
  description: string;
  /**
   * An object containing configuration information for the flow types supported
   */
  flows: _a2a_v1_OAuthFlows__Output | null;
  /**
   * URL to the oauth2 authorization server metadata
   * [RFC8414](https://datatracker.ietf.org/doc/html/rfc8414). TLS is required.
   */
  oauth2_metadata_url: string;
}
