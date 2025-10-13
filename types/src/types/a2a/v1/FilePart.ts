// Original file: ../specification/grpc/a2a.proto

/**
 * --8<-- [start:FilePart]
 * FilePart represents the different ways files can be provided. If files are
 * small, directly feeding the bytes is supported via file_with_bytes. If the
 * file is large, the agent should read the content as appropriate directly
 * from the file_with_uri source.
 */
export interface FilePart {
  file_with_uri?: string;
  file_with_bytes?: Buffer | Uint8Array | string;
  mime_type?: string;
  name?: string;
  file?: "file_with_uri" | "file_with_bytes";
}

/**
 * --8<-- [start:FilePart]
 * FilePart represents the different ways files can be provided. If files are
 * small, directly feeding the bytes is supported via file_with_bytes. If the
 * file is large, the agent should read the content as appropriate directly
 * from the file_with_uri source.
 */
export interface FilePart__Output {
  file_with_uri?: string;
  file_with_bytes?: Buffer;
  mime_type: string;
  name: string;
  file?: "file_with_uri" | "file_with_bytes";
}
