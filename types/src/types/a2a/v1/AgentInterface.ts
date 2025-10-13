// Original file: ../specification/grpc/a2a.proto


/**
 * --8<-- [start:AgentInterface]
 * Defines additional transport information for the agent.
 */
export interface AgentInterface {
  /**
   * The url this interface is found at.
   */
  'url'?: (string);
  /**
   * The transport supported this url. This is an open form string, to be
   * easily extended for many transport protocols. The core ones officially
   * supported are JSONRPC, GRPC and HTTP+JSON.
   */
  'transport'?: (string);
}

/**
 * --8<-- [start:AgentInterface]
 * Defines additional transport information for the agent.
 */
export interface AgentInterface__Output {
  /**
   * The url this interface is found at.
   */
  'url': (string);
  /**
   * The transport supported this url. This is an open form string, to be
   * easily extended for many transport protocols. The core ones officially
   * supported are JSONRPC, GRPC and HTTP+JSON.
   */
  'transport': (string);
}
