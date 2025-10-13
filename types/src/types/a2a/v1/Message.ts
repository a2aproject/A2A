// Original file: ../specification/grpc/a2a.proto

import type { Role as _a2a_v1_Role, Role__Output as _a2a_v1_Role__Output } from '../../a2a/v1/Role';
import type { Part as _a2a_v1_Part, Part__Output as _a2a_v1_Part__Output } from '../../a2a/v1/Part';
import type { Struct as _google_protobuf_Struct, Struct__Output as _google_protobuf_Struct__Output } from '../../google/protobuf/Struct';

/**
 * --8<-- [start:Message]
 * Message is one unit of communication between client and server. It is
 * associated with a context and optionally a task. Since the server is
 * responsible for the context definition, it must always provide a context_id
 * in its messages. The client can optionally provide the context_id if it
 * knows the context to associate the message to. Similarly for task_id,
 * except the server decides if a task is created and whether to include the
 * task_id.
 */
export interface Message {
  /**
   * The unique identifier (e.g. UUID)of the message. This is required and
   * created by the message creator.
   */
  'message_id'?: (string);
  /**
   * The context id of the message. This is optional and if set, the message
   * will be associated with the given context.
   */
  'context_id'?: (string);
  /**
   * The task id of the message. This is optional and if set, the message
   * will be associated with the given task.
   */
  'task_id'?: (string);
  /**
   * A role for the message.
   */
  'role'?: (_a2a_v1_Role);
  /**
   * protolint:disable REPEATED_FIELD_NAMES_PLURALIZED
   * Content is the container of the message content.
   */
  'content'?: (_a2a_v1_Part)[];
  /**
   * protolint:enable REPEATED_FIELD_NAMES_PLURALIZED
   * Any optional metadata to provide along with the message.
   */
  'metadata'?: (_google_protobuf_Struct | null);
  /**
   * The URIs of extensions that are present or contributed to this Message.
   */
  'extensions'?: (string)[];
}

/**
 * --8<-- [start:Message]
 * Message is one unit of communication between client and server. It is
 * associated with a context and optionally a task. Since the server is
 * responsible for the context definition, it must always provide a context_id
 * in its messages. The client can optionally provide the context_id if it
 * knows the context to associate the message to. Similarly for task_id,
 * except the server decides if a task is created and whether to include the
 * task_id.
 */
export interface Message__Output {
  /**
   * The unique identifier (e.g. UUID)of the message. This is required and
   * created by the message creator.
   */
  'message_id': (string);
  /**
   * The context id of the message. This is optional and if set, the message
   * will be associated with the given context.
   */
  'context_id': (string);
  /**
   * The task id of the message. This is optional and if set, the message
   * will be associated with the given task.
   */
  'task_id': (string);
  /**
   * A role for the message.
   */
  'role': (_a2a_v1_Role__Output);
  /**
   * protolint:disable REPEATED_FIELD_NAMES_PLURALIZED
   * Content is the container of the message content.
   */
  'content': (_a2a_v1_Part__Output)[];
  /**
   * protolint:enable REPEATED_FIELD_NAMES_PLURALIZED
   * Any optional metadata to provide along with the message.
   */
  'metadata': (_google_protobuf_Struct__Output | null);
  /**
   * The URIs of extensions that are present or contributed to this Message.
   */
  'extensions': (string)[];
}
