// Original file: ../specification/grpc/a2a.proto

export const Role = {
  ROLE_UNSPECIFIED: "ROLE_UNSPECIFIED",
  /**
   * USER role refers to communication from the client to the server.
   */
  ROLE_USER: "ROLE_USER",
  /**
   * AGENT role refers to communication from the server to the client.
   */
  ROLE_AGENT: "ROLE_AGENT",
} as const;

export type Role =
  | "ROLE_UNSPECIFIED"
  | 0
  /**
   * USER role refers to communication from the client to the server.
   */
  | "ROLE_USER"
  | 1
  /**
   * AGENT role refers to communication from the server to the client.
   */
  | "ROLE_AGENT"
  | 2;

export type Role__Output = (typeof Role)[keyof typeof Role];
