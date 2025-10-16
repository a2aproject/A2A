// Original file: ../specification/grpc/a2a.proto

import type {
  AgentProvider as _a2a_v1_AgentProvider,
  AgentProvider__Output as _a2a_v1_AgentProvider__Output,
} from "../../a2a/v1/AgentProvider";
import type {
  AgentCapabilities as _a2a_v1_AgentCapabilities,
  AgentCapabilities__Output as _a2a_v1_AgentCapabilities__Output,
} from "../../a2a/v1/AgentCapabilities";
import type {
  SecurityScheme as _a2a_v1_SecurityScheme,
  SecurityScheme__Output as _a2a_v1_SecurityScheme__Output,
} from "../../a2a/v1/SecurityScheme";
import type {
  Security as _a2a_v1_Security,
  Security__Output as _a2a_v1_Security__Output,
} from "../../a2a/v1/Security";
import type {
  AgentSkill as _a2a_v1_AgentSkill,
  AgentSkill__Output as _a2a_v1_AgentSkill__Output,
} from "../../a2a/v1/AgentSkill";
import type {
  AgentInterface as _a2a_v1_AgentInterface,
  AgentInterface__Output as _a2a_v1_AgentInterface__Output,
} from "../../a2a/v1/AgentInterface";
import type {
  AgentCardSignature as _a2a_v1_AgentCardSignature,
  AgentCardSignature__Output as _a2a_v1_AgentCardSignature__Output,
} from "../../a2a/v1/AgentCardSignature";

/**
 * --8<-- [start:AgentCard]
 * AgentCard conveys key information:
 * - Overall details (version, name, description, uses)
 * - Skills; a set of actions/solutions the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 * Next ID: 19
 */
export interface AgentCard {
  /**
   * A human readable name for the agent.
   * Example: "Recipe Agent"
   */
  name?: string;
  /**
   * A description of the agent's domain of action/solution space.
   * Example: "Agent that helps users with recipes and cooking."
   */
  description?: string;
  /**
   * A URL to the address the agent is hosted at. This represents the
   * preferred endpoint as declared by the agent.
   */
  url?: string;
  /**
   * The service provider of the agent.
   */
  provider?: _a2a_v1_AgentProvider | null;
  /**
   * The version of the agent.
   * Example: "1.0.0"
   */
  version?: string;
  /**
   * A url to provide additional documentation about the agent.
   */
  documentation_url?: string;
  /**
   * A2A Capability set supported by the agent.
   */
  capabilities?: _a2a_v1_AgentCapabilities | null;
  /**
   * The security scheme details used for authenticating with this agent.
   */
  security_schemes?: { [key: string]: _a2a_v1_SecurityScheme };
  /**
   * protolint:disable REPEATED_FIELD_NAMES_PLURALIZED
   * Security requirements for contacting the agent.
   * This list can be seen as an OR of ANDs. Each object in the list describes
   * one possible set of security requirements that must be present on a
   * request. This allows specifying, for example, "callers must either use
   * OAuth OR an API Key AND mTLS."
   * Example:
   * security {
   * schemes { key: "oauth" value { list: ["read"] } }
   * }
   * security {
   * schemes { key: "api-key" }
   * schemes { key: "mtls" }
   * }
   */
  security?: _a2a_v1_Security[];
  /**
   * protolint:enable REPEATED_FIELD_NAMES_PLURALIZED
   * The set of interaction modes that the agent supports across all skills.
   * This can be overridden per skill. Defined as mime types.
   */
  default_input_modes?: string[];
  /**
   * The mime types supported as outputs from this agent.
   */
  default_output_modes?: string[];
  /**
   * Skills represent a unit of ability an agent can perform. This may
   * somewhat abstract but represents a more focused set of actions that the
   * agent is highly likely to succeed at.
   */
  skills?: _a2a_v1_AgentSkill[];
  /**
   * Whether the agent supports providing an extended agent card when
   * the user is authenticated, i.e. is the card from .well-known
   * different than the card from GetAgentCard.
   */
  supports_authenticated_extended_card?: boolean;
  /**
   * The transport of the preferred endpoint. If empty, defaults to JSONRPC.
   */
  preferred_transport?: string;
  /**
   * Announcement of additional supported transports. Client can use any of
   * the supported transports.
   */
  additional_interfaces?: _a2a_v1_AgentInterface[];
  /**
   * The version of the A2A protocol this agent supports.
   */
  protocol_version?: string;
  /**
   * JSON Web Signatures computed for this AgentCard.
   */
  signatures?: _a2a_v1_AgentCardSignature[];
  /**
   * An optional URL to an icon for the agent.
   */
  icon_url?: string;
}

/**
 * --8<-- [start:AgentCard]
 * AgentCard conveys key information:
 * - Overall details (version, name, description, uses)
 * - Skills; a set of actions/solutions the agent can perform
 * - Default modalities/content types supported by the agent.
 * - Authentication requirements
 * Next ID: 19
 */
export interface AgentCard__Output {
  /**
   * A human readable name for the agent.
   * Example: "Recipe Agent"
   */
  name: string;
  /**
   * A description of the agent's domain of action/solution space.
   * Example: "Agent that helps users with recipes and cooking."
   */
  description: string;
  /**
   * A URL to the address the agent is hosted at. This represents the
   * preferred endpoint as declared by the agent.
   */
  url: string;
  /**
   * The service provider of the agent.
   */
  provider: _a2a_v1_AgentProvider__Output | null;
  /**
   * The version of the agent.
   * Example: "1.0.0"
   */
  version: string;
  /**
   * A url to provide additional documentation about the agent.
   */
  documentation_url: string;
  /**
   * A2A Capability set supported by the agent.
   */
  capabilities: _a2a_v1_AgentCapabilities__Output | null;
  /**
   * The security scheme details used for authenticating with this agent.
   */
  security_schemes: { [key: string]: _a2a_v1_SecurityScheme__Output };
  /**
   * protolint:disable REPEATED_FIELD_NAMES_PLURALIZED
   * Security requirements for contacting the agent.
   * This list can be seen as an OR of ANDs. Each object in the list describes
   * one possible set of security requirements that must be present on a
   * request. This allows specifying, for example, "callers must either use
   * OAuth OR an API Key AND mTLS."
   * Example:
   * security {
   * schemes { key: "oauth" value { list: ["read"] } }
   * }
   * security {
   * schemes { key: "api-key" }
   * schemes { key: "mtls" }
   * }
   */
  security: _a2a_v1_Security__Output[];
  /**
   * protolint:enable REPEATED_FIELD_NAMES_PLURALIZED
   * The set of interaction modes that the agent supports across all skills.
   * This can be overridden per skill. Defined as mime types.
   */
  default_input_modes: string[];
  /**
   * The mime types supported as outputs from this agent.
   */
  default_output_modes: string[];
  /**
   * Skills represent a unit of ability an agent can perform. This may
   * somewhat abstract but represents a more focused set of actions that the
   * agent is highly likely to succeed at.
   */
  skills: _a2a_v1_AgentSkill__Output[];
  /**
   * Whether the agent supports providing an extended agent card when
   * the user is authenticated, i.e. is the card from .well-known
   * different than the card from GetAgentCard.
   */
  supports_authenticated_extended_card: boolean;
  /**
   * The transport of the preferred endpoint. If empty, defaults to JSONRPC.
   */
  preferred_transport: string;
  /**
   * Announcement of additional supported transports. Client can use any of
   * the supported transports.
   */
  additional_interfaces: _a2a_v1_AgentInterface__Output[];
  /**
   * The version of the A2A protocol this agent supports.
   */
  protocol_version: string;
  /**
   * JSON Web Signatures computed for this AgentCard.
   */
  signatures: _a2a_v1_AgentCardSignature__Output[];
  /**
   * An optional URL to an icon for the agent.
   */
  icon_url: string;
}
