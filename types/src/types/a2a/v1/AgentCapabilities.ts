// Original file: ../specification/grpc/a2a.proto

import type {
  AgentExtension as _a2a_v1_AgentExtension,
  AgentExtension__Output as _a2a_v1_AgentExtension__Output,
} from "../../a2a/v1/AgentExtension";

/**
 * --8<-- [start:AgentCapabilities]
 * Defines the A2A feature set supported by the agent
 */
export interface AgentCapabilities {
  /**
   * If the agent will support streaming responses
   */
  streaming?: boolean;
  /**
   * If the agent can send push notifications to the clients webhook
   */
  push_notifications?: boolean;
  /**
   * Extensions supported by this agent.
   */
  extensions?: _a2a_v1_AgentExtension[];
}

/**
 * --8<-- [start:AgentCapabilities]
 * Defines the A2A feature set supported by the agent
 */
export interface AgentCapabilities__Output {
  /**
   * If the agent will support streaming responses
   */
  streaming: boolean;
  /**
   * If the agent can send push notifications to the clients webhook
   */
  push_notifications: boolean;
  /**
   * Extensions supported by this agent.
   */
  extensions: _a2a_v1_AgentExtension__Output[];
}
