// Original file: ../specification/grpc/a2a.proto

import type {
  AuthorizationCodeOAuthFlow as _a2a_v1_AuthorizationCodeOAuthFlow,
  AuthorizationCodeOAuthFlow__Output as _a2a_v1_AuthorizationCodeOAuthFlow__Output,
} from "../../a2a/v1/AuthorizationCodeOAuthFlow";
import type {
  ClientCredentialsOAuthFlow as _a2a_v1_ClientCredentialsOAuthFlow,
  ClientCredentialsOAuthFlow__Output as _a2a_v1_ClientCredentialsOAuthFlow__Output,
} from "../../a2a/v1/ClientCredentialsOAuthFlow";
import type {
  ImplicitOAuthFlow as _a2a_v1_ImplicitOAuthFlow,
  ImplicitOAuthFlow__Output as _a2a_v1_ImplicitOAuthFlow__Output,
} from "../../a2a/v1/ImplicitOAuthFlow";
import type {
  PasswordOAuthFlow as _a2a_v1_PasswordOAuthFlow,
  PasswordOAuthFlow__Output as _a2a_v1_PasswordOAuthFlow__Output,
} from "../../a2a/v1/PasswordOAuthFlow";

/**
 * --8<-- [start:OAuthFlows]
 */
export interface OAuthFlows {
  authorization_code?: _a2a_v1_AuthorizationCodeOAuthFlow | null;
  client_credentials?: _a2a_v1_ClientCredentialsOAuthFlow | null;
  implicit?: _a2a_v1_ImplicitOAuthFlow | null;
  password?: _a2a_v1_PasswordOAuthFlow | null;
  flow?: "authorization_code" | "client_credentials" | "implicit" | "password";
}

/**
 * --8<-- [start:OAuthFlows]
 */
export interface OAuthFlows__Output {
  authorization_code?: _a2a_v1_AuthorizationCodeOAuthFlow__Output | null;
  client_credentials?: _a2a_v1_ClientCredentialsOAuthFlow__Output | null;
  implicit?: _a2a_v1_ImplicitOAuthFlow__Output | null;
  password?: _a2a_v1_PasswordOAuthFlow__Output | null;
  flow?: "authorization_code" | "client_credentials" | "implicit" | "password";
}
