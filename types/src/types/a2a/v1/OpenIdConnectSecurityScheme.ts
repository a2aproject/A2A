// Original file: ../specification/grpc/a2a.proto

/**
 * --8<-- [start:OpenIdConnectSecurityScheme]
 */
export interface OpenIdConnectSecurityScheme {
  /**
   * Description of this security scheme.
   */
  description?: string;
  /**
   * Well-known URL to discover the [[OpenID-Connect-Discovery]] provider
   * metadata.
   */
  open_id_connect_url?: string;
}

/**
 * --8<-- [start:OpenIdConnectSecurityScheme]
 */
export interface OpenIdConnectSecurityScheme__Output {
  /**
   * Description of this security scheme.
   */
  description: string;
  /**
   * Well-known URL to discover the [[OpenID-Connect-Discovery]] provider
   * metadata.
   */
  open_id_connect_url: string;
}
