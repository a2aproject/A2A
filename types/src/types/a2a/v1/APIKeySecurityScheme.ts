// Original file: ../specification/grpc/a2a.proto


/**
 * --8<-- [start:APIKeySecurityScheme]
 */
export interface APIKeySecurityScheme {
  /**
   * Description of this security scheme.
   */
  'description'?: (string);
  /**
   * Location of the API key, valid values are "query", "header", or "cookie"
   */
  'location'?: (string);
  /**
   * Name of the header, query or cookie parameter to be used.
   */
  'name'?: (string);
}

/**
 * --8<-- [start:APIKeySecurityScheme]
 */
export interface APIKeySecurityScheme__Output {
  /**
   * Description of this security scheme.
   */
  'description': (string);
  /**
   * Location of the API key, valid values are "query", "header", or "cookie"
   */
  'location': (string);
  /**
   * Name of the header, query or cookie parameter to be used.
   */
  'name': (string);
}
