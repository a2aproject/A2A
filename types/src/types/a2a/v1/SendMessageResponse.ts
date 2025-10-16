// Original file: ../specification/grpc/a2a.proto

import type {
  Task as _a2a_v1_Task,
  Task__Output as _a2a_v1_Task__Output,
} from "../../a2a/v1/Task";
import type {
  Message as _a2a_v1_Message,
  Message__Output as _a2a_v1_Message__Output,
} from "../../a2a/v1/Message";

/**
 * Response Messages ///////////
 * --8<-- [start:SendMessageSuccessResponse]
 */
export interface SendMessageResponse {
  task?: _a2a_v1_Task | null;
  msg?: _a2a_v1_Message | null;
  payload?: "task" | "msg";
}

/**
 * Response Messages ///////////
 * --8<-- [start:SendMessageSuccessResponse]
 */
export interface SendMessageResponse__Output {
  task?: _a2a_v1_Task__Output | null;
  msg?: _a2a_v1_Message__Output | null;
  payload?: "task" | "msg";
}
