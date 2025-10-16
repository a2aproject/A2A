// Original file: ../specification/grpc/a2a.proto

import type {
  Artifact as _a2a_v1_Artifact,
  Artifact__Output as _a2a_v1_Artifact__Output,
} from "../../a2a/v1/Artifact";
import type {
  Struct as _google_protobuf_Struct,
  Struct__Output as _google_protobuf_Struct__Output,
} from "../../google/protobuf/Struct";

/**
 * --8<-- [start:TaskArtifactUpdateEvent]
 * TaskArtifactUpdateEvent represents a task delta where an artifact has
 * been generated.
 */
export interface TaskArtifactUpdateEvent {
  /**
   * The id of the task for this artifact
   */
  task_id?: string;
  /**
   * The id of the context that this task belongs too
   */
  context_id?: string;
  /**
   * The artifact itself
   */
  artifact?: _a2a_v1_Artifact | null;
  /**
   * Whether this should be appended to a prior one produced
   */
  append?: boolean;
  /**
   * Whether this represents the last part of an artifact
   */
  last_chunk?: boolean;
  /**
   * Optional metadata associated with the artifact update.
   */
  metadata?: _google_protobuf_Struct | null;
}

/**
 * --8<-- [start:TaskArtifactUpdateEvent]
 * TaskArtifactUpdateEvent represents a task delta where an artifact has
 * been generated.
 */
export interface TaskArtifactUpdateEvent__Output {
  /**
   * The id of the task for this artifact
   */
  task_id: string;
  /**
   * The id of the context that this task belongs too
   */
  context_id: string;
  /**
   * The artifact itself
   */
  artifact: _a2a_v1_Artifact__Output | null;
  /**
   * Whether this should be appended to a prior one produced
   */
  append: boolean;
  /**
   * Whether this represents the last part of an artifact
   */
  last_chunk: boolean;
  /**
   * Optional metadata associated with the artifact update.
   */
  metadata: _google_protobuf_Struct__Output | null;
}
