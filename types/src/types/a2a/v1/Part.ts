// Original file: ../specification/grpc/a2a.proto

import type { FilePart as _a2a_v1_FilePart, FilePart__Output as _a2a_v1_FilePart__Output } from '../../a2a/v1/FilePart';
import type { DataPart as _a2a_v1_DataPart, DataPart__Output as _a2a_v1_DataPart__Output } from '../../a2a/v1/DataPart';
import type { Struct as _google_protobuf_Struct, Struct__Output as _google_protobuf_Struct__Output } from '../../google/protobuf/Struct';

/**
 * --8<-- [start:Part]
 * Part represents a container for a section of communication content.
 * Parts can be purely textual, some sort of file (image, video, etc) or
 * a structured data blob (i.e. JSON).
 */
export interface Part {
  'text'?: (string);
  'file'?: (_a2a_v1_FilePart | null);
  'data'?: (_a2a_v1_DataPart | null);
  /**
   * Optional metadata associated with this part.
   */
  'metadata'?: (_google_protobuf_Struct | null);
  'part'?: "text"|"file"|"data";
}

/**
 * --8<-- [start:Part]
 * Part represents a container for a section of communication content.
 * Parts can be purely textual, some sort of file (image, video, etc) or
 * a structured data blob (i.e. JSON).
 */
export interface Part__Output {
  'text'?: (string);
  'file'?: (_a2a_v1_FilePart__Output | null);
  'data'?: (_a2a_v1_DataPart__Output | null);
  /**
   * Optional metadata associated with this part.
   */
  'metadata': (_google_protobuf_Struct__Output | null);
  'part'?: "text"|"file"|"data";
}
