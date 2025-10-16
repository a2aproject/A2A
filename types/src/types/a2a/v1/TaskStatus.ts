// Original file: ../specification/grpc/a2a.proto

import type {
  TaskState as _a2a_v1_TaskState,
  TaskState__Output as _a2a_v1_TaskState__Output,
} from "../../a2a/v1/TaskState";
import type {
  Message as _a2a_v1_Message,
  Message__Output as _a2a_v1_Message__Output,
} from "../../a2a/v1/Message";
import type {
  Timestamp as _google_protobuf_Timestamp,
  Timestamp__Output as _google_protobuf_Timestamp__Output,
} from "../../google/protobuf/Timestamp";

/**
 * --8<-- [start:TaskStatus]
 * A container for the status of a task
 */
export interface TaskStatus {
  /**
   * The current state of this task
   */
  state?: _a2a_v1_TaskState;
  /**
   * A message associated with the status.
   */
  update?: _a2a_v1_Message | null;
  /**
   * Timestamp when the status was recorded.
   * Example: "2023-10-27T10:00:00Z"
   */
  timestamp?: _google_protobuf_Timestamp | null;
}

/**
 * --8<-- [start:TaskStatus]
 * A container for the status of a task
 */
export interface TaskStatus__Output {
  /**
   * The current state of this task
   */
  state: _a2a_v1_TaskState__Output;
  /**
   * A message associated with the status.
   */
  update: _a2a_v1_Message__Output | null;
  /**
   * Timestamp when the status was recorded.
   * Example: "2023-10-27T10:00:00Z"
   */
  timestamp: _google_protobuf_Timestamp__Output | null;
}
