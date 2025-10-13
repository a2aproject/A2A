// Original file: ../specification/grpc/a2a.proto


/**
 * --8<-- [start:AgentProvider]
 * Represents information about the service provider of an agent.
 */
export interface AgentProvider {
  /**
   * The providers reference url
   * Example: "https://ai.google.dev"
   */
  'url'?: (string);
  /**
   * The providers organization name
   * Example: "Google"
   */
  'organization'?: (string);
}

/**
 * --8<-- [start:AgentProvider]
 * Represents information about the service provider of an agent.
 */
export interface AgentProvider__Output {
  /**
   * The providers reference url
   * Example: "https://ai.google.dev"
   */
  'url': (string);
  /**
   * The providers organization name
   * Example: "Google"
   */
  'organization': (string);
}
