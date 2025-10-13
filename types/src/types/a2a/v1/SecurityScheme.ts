// Original file: ../specification/grpc/a2a.proto

import type {
  APIKeySecurityScheme as _a2a_v1_APIKeySecurityScheme,
  APIKeySecurityScheme__Output as _a2a_v1_APIKeySecurityScheme__Output,
} from "../../a2a/v1/APIKeySecurityScheme";
import type {
  HTTPAuthSecurityScheme as _a2a_v1_HTTPAuthSecurityScheme,
  HTTPAuthSecurityScheme__Output as _a2a_v1_HTTPAuthSecurityScheme__Output,
} from "../../a2a/v1/HTTPAuthSecurityScheme";
import type {
  OAuth2SecurityScheme as _a2a_v1_OAuth2SecurityScheme,
  OAuth2SecurityScheme__Output as _a2a_v1_OAuth2SecurityScheme__Output,
} from "../../a2a/v1/OAuth2SecurityScheme";
import type {
  OpenIdConnectSecurityScheme as _a2a_v1_OpenIdConnectSecurityScheme,
  OpenIdConnectSecurityScheme__Output as _a2a_v1_OpenIdConnectSecurityScheme__Output,
} from "../../a2a/v1/OpenIdConnectSecurityScheme";
import type {
  MutualTlsSecurityScheme as _a2a_v1_MutualTlsSecurityScheme,
  MutualTlsSecurityScheme__Output as _a2a_v1_MutualTlsSecurityScheme__Output,
} from "../../a2a/v1/MutualTlsSecurityScheme";

/**
 * --8<-- [start:SecurityScheme]
 */
export interface SecurityScheme {
  api_key_security_scheme?: _a2a_v1_APIKeySecurityScheme | null;
  http_auth_security_scheme?: _a2a_v1_HTTPAuthSecurityScheme | null;
  oauth2_security_scheme?: _a2a_v1_OAuth2SecurityScheme | null;
  open_id_connect_security_scheme?: _a2a_v1_OpenIdConnectSecurityScheme | null;
  mtls_security_scheme?: _a2a_v1_MutualTlsSecurityScheme | null;
  scheme?:
    | "api_key_security_scheme"
    | "http_auth_security_scheme"
    | "oauth2_security_scheme"
    | "open_id_connect_security_scheme"
    | "mtls_security_scheme";
}

/**
 * --8<-- [start:SecurityScheme]
 */
export interface SecurityScheme__Output {
  api_key_security_scheme?: _a2a_v1_APIKeySecurityScheme__Output | null;
  http_auth_security_scheme?: _a2a_v1_HTTPAuthSecurityScheme__Output | null;
  oauth2_security_scheme?: _a2a_v1_OAuth2SecurityScheme__Output | null;
  open_id_connect_security_scheme?: _a2a_v1_OpenIdConnectSecurityScheme__Output | null;
  mtls_security_scheme?: _a2a_v1_MutualTlsSecurityScheme__Output | null;
  scheme?:
    | "api_key_security_scheme"
    | "http_auth_security_scheme"
    | "oauth2_security_scheme"
    | "open_id_connect_security_scheme"
    | "mtls_security_scheme";
}
