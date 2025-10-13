// Original file: ../specification/grpc/a2a.proto

import type {
  Struct as _google_protobuf_Struct,
  Struct__Output as _google_protobuf_Struct__Output,
} from "../../google/protobuf/Struct";

/**
 * --8<-- [start:AgentExtension]
 * A declaration of an extension supported by an Agent.
 */
export interface AgentExtension {
  /**
   * The URI of the extension.
   * Example: "https://developers.google.com/identity/protocols/oauth2"
   */
  uri?: string;
  /**
   * A description of how this agent uses this extension.
   * Example: "Google OAuth 2.0 authentication"
   */
  description?: string;
  /**
   * Whether the client must follow specific requirements of the extension.
   * Example: false
   */
  required?: boolean;
  /**
   * Optional configuration for the extension.
   */
  params?: _google_protobuf_Struct | null;
}

/**
 * --8<-- [start:AgentExtension]
 * A declaration of an extension supported by an Agent.
 */
export interface AgentExtension__Output {
  /**
   * The URI of the extension.
   * Example: "https://developers.google.com/identity/protocols/oauth2"
   */
  uri: string;
  /**
   * A description of how this agent uses this extension.
   * Example: "Google OAuth 2.0 authentication"
   */
  description: string;
  /**
   * Whether the client must follow specific requirements of the extension.
   * Example: false
   */
  required: boolean;
  /**
   * Optional configuration for the extension.
   */
  params: _google_protobuf_Struct__Output | null;
}
