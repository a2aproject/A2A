// Original file: ../specification/grpc/a2a.proto

/**
 * --8<-- [start:AuthorizationCodeOAuthFlow]
 */
export interface AuthorizationCodeOAuthFlow {
  /**
   * The authorization URL to be used for this flow. This MUST be in the
   * form of a URL. The OAuth2 standard requires the use of TLS
   */
  authorization_url?: string;
  /**
   * The token URL to be used for this flow. This MUST be in the form of a URL.
   * The OAuth2 standard requires the use of TLS.
   */
  token_url?: string;
  /**
   * The URL to be used for obtaining refresh tokens. This MUST be in the
   * form of a URL. The OAuth2 standard requires the use of TLS.
   */
  refresh_url?: string;
  /**
   * The available scopes for the OAuth2 security scheme. A map between the
   * scope name and a short description for it. The map MAY be empty.
   */
  scopes?: { [key: string]: string };
}

/**
 * --8<-- [start:AuthorizationCodeOAuthFlow]
 */
export interface AuthorizationCodeOAuthFlow__Output {
  /**
   * The authorization URL to be used for this flow. This MUST be in the
   * form of a URL. The OAuth2 standard requires the use of TLS
   */
  authorization_url: string;
  /**
   * The token URL to be used for this flow. This MUST be in the form of a URL.
   * The OAuth2 standard requires the use of TLS.
   */
  token_url: string;
  /**
   * The URL to be used for obtaining refresh tokens. This MUST be in the
   * form of a URL. The OAuth2 standard requires the use of TLS.
   */
  refresh_url: string;
  /**
   * The available scopes for the OAuth2 security scheme. A map between the
   * scope name and a short description for it. The map MAY be empty.
   */
  scopes: { [key: string]: string };
}
