// Original file: ../specification/grpc/a2a.proto

import type {
  Security as _a2a_v1_Security,
  Security__Output as _a2a_v1_Security__Output,
} from "../../a2a/v1/Security";

/**
 * --8<-- [start:AgentSkill]
 * AgentSkill represents a unit of action/solution that the agent can perform.
 * One can think of this as a type of highly reliable solution that an agent
 * can be tasked to provide. Agents have the autonomy to choose how and when
 * to use specific skills, but clients should have confidence that if the
 * skill is defined that unit of action can be reliably performed.
 */
export interface AgentSkill {
  /**
   * Unique identifier of the skill within this agent.
   */
  id?: string;
  /**
   * A human readable name for the skill.
   */
  name?: string;
  /**
   * A human (or llm) readable description of the skill
   * details and behaviors.
   */
  description?: string;
  /**
   * A set of tags for the skill to enhance categorization/utilization.
   * Example: ["cooking", "customer support", "billing"]
   */
  tags?: string[];
  /**
   * A set of example queries that this skill is designed to address.
   * These examples should help the caller to understand how to craft requests
   * to the agent to achieve specific goals.
   * Example: ["I need a recipe for bread"]
   */
  examples?: string[];
  /**
   * Possible input modalities supported.
   */
  input_modes?: string[];
  /**
   * Possible output modalities produced
   */
  output_modes?: string[];
  /**
   * protolint:disable REPEATED_FIELD_NAMES_PLURALIZED
   * Security schemes necessary for the agent to leverage this skill.
   * As in the overall AgentCard.security, this list represents a logical OR of
   * security requirement objects. Each object is a set of security schemes
   * that must be used together (a logical AND).
   */
  security?: _a2a_v1_Security[];
}

/**
 * --8<-- [start:AgentSkill]
 * AgentSkill represents a unit of action/solution that the agent can perform.
 * One can think of this as a type of highly reliable solution that an agent
 * can be tasked to provide. Agents have the autonomy to choose how and when
 * to use specific skills, but clients should have confidence that if the
 * skill is defined that unit of action can be reliably performed.
 */
export interface AgentSkill__Output {
  /**
   * Unique identifier of the skill within this agent.
   */
  id: string;
  /**
   * A human readable name for the skill.
   */
  name: string;
  /**
   * A human (or llm) readable description of the skill
   * details and behaviors.
   */
  description: string;
  /**
   * A set of tags for the skill to enhance categorization/utilization.
   * Example: ["cooking", "customer support", "billing"]
   */
  tags: string[];
  /**
   * A set of example queries that this skill is designed to address.
   * These examples should help the caller to understand how to craft requests
   * to the agent to achieve specific goals.
   * Example: ["I need a recipe for bread"]
   */
  examples: string[];
  /**
   * Possible input modalities supported.
   */
  input_modes: string[];
  /**
   * Possible output modalities produced
   */
  output_modes: string[];
  /**
   * protolint:disable REPEATED_FIELD_NAMES_PLURALIZED
   * Security schemes necessary for the agent to leverage this skill.
   * As in the overall AgentCard.security, this list represents a logical OR of
   * security requirement objects. Each object is a set of security schemes
   * that must be used together (a logical AND).
   */
  security: _a2a_v1_Security__Output[];
}
