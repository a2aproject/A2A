// Original file: ../specification/grpc/a2a.proto

import type {
  Part as _a2a_v1_Part,
  Part__Output as _a2a_v1_Part__Output,
} from "../../a2a/v1/Part";
import type {
  Struct as _google_protobuf_Struct,
  Struct__Output as _google_protobuf_Struct__Output,
} from "../../google/protobuf/Struct";

/**
 * --8<-- [start:Artifact]
 * Artifacts are the container for task completed results. These are similar
 * to Messages but are intended to be the product of a task, as opposed to
 * point-to-point communication.
 */
export interface Artifact {
  /**
   * Unique identifier (e.g. UUID) for the artifact. It must be at least unique
   * within a task.
   */
  artifact_id?: string;
  /**
   * A human readable name for the artifact.
   */
  name?: string;
  /**
   * A human readable description of the artifact, optional.
   */
  description?: string;
  /**
   * The content of the artifact.
   */
  parts?: _a2a_v1_Part[];
  /**
   * Optional metadata included with the artifact.
   */
  metadata?: _google_protobuf_Struct | null;
  /**
   * The URIs of extensions that are present or contributed to this Artifact.
   */
  extensions?: string[];
}

/**
 * --8<-- [start:Artifact]
 * Artifacts are the container for task completed results. These are similar
 * to Messages but are intended to be the product of a task, as opposed to
 * point-to-point communication.
 */
export interface Artifact__Output {
  /**
   * Unique identifier (e.g. UUID) for the artifact. It must be at least unique
   * within a task.
   */
  artifact_id: string;
  /**
   * A human readable name for the artifact.
   */
  name: string;
  /**
   * A human readable description of the artifact, optional.
   */
  description: string;
  /**
   * The content of the artifact.
   */
  parts: _a2a_v1_Part__Output[];
  /**
   * Optional metadata included with the artifact.
   */
  metadata: _google_protobuf_Struct__Output | null;
  /**
   * The URIs of extensions that are present or contributed to this Artifact.
   */
  extensions: string[];
}
