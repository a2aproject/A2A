// Original file: ../specification/grpc/a2a.proto

import type {
  Struct as _google_protobuf_Struct,
  Struct__Output as _google_protobuf_Struct__Output,
} from "../../google/protobuf/Struct";

/**
 * --8<-- [start:AgentCardSignature]
 * AgentCardSignature represents a JWS signature of an AgentCard.
 * This follows the JSON format of an RFC 7515 JSON Web Signature (JWS).
 */
export interface AgentCardSignature {
  /**
   * The protected JWS header for the signature. This is always a
   * base64url-encoded JSON object. Required.
   */
  protected?: string;
  /**
   * The computed signature, base64url-encoded. Required.
   */
  signature?: string;
  /**
   * The unprotected JWS header values.
   */
  header?: _google_protobuf_Struct | null;
}

/**
 * --8<-- [start:AgentCardSignature]
 * AgentCardSignature represents a JWS signature of an AgentCard.
 * This follows the JSON format of an RFC 7515 JSON Web Signature (JWS).
 */
export interface AgentCardSignature__Output {
  /**
   * The protected JWS header for the signature. This is always a
   * base64url-encoded JSON object. Required.
   */
  protected: string;
  /**
   * The computed signature, base64url-encoded. Required.
   */
  signature: string;
  /**
   * The unprotected JWS header values.
   */
  header: _google_protobuf_Struct__Output | null;
}
