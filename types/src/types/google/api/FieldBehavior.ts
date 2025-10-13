// Original file: node_modules/google-proto-files/google/api/field_behavior.proto

/**
 * An indicator of the behavior of a given field (for example, that a field
 * is required in requests, or given as output but ignored as input).
 * This **does not** change the behavior in protocol buffers itself; it only
 * denotes the behavior and may affect how API tooling handles the field.
 * 
 * Note: This enum **may** receive new values in the future.
 */
export const FieldBehavior = {
  /**
   * Conventional default for enums. Do not use this.
   */
  FIELD_BEHAVIOR_UNSPECIFIED: 'FIELD_BEHAVIOR_UNSPECIFIED',
  /**
   * Specifically denotes a field as optional.
   * While all fields in protocol buffers are optional, this may be specified
   * for emphasis if appropriate.
   */
  OPTIONAL: 'OPTIONAL',
  /**
   * Denotes a field as required.
   * This indicates that the field **must** be provided as part of the request,
   * and failure to do so will cause an error (usually `INVALID_ARGUMENT`).
   */
  REQUIRED: 'REQUIRED',
  /**
   * Denotes a field as output only.
   * This indicates that the field is provided in responses, but including the
   * field in a request does nothing (the server *must* ignore it and
   * *must not* throw an error as a result of the field's presence).
   */
  OUTPUT_ONLY: 'OUTPUT_ONLY',
  /**
   * Denotes a field as input only.
   * This indicates that the field is provided in requests, and the
   * corresponding field is not included in output.
   */
  INPUT_ONLY: 'INPUT_ONLY',
  /**
   * Denotes a field as immutable.
   * This indicates that the field may be set once in a request to create a
   * resource, but may not be changed thereafter.
   */
  IMMUTABLE: 'IMMUTABLE',
  /**
   * Denotes that a (repeated) field is an unordered list.
   * This indicates that the service may provide the elements of the list
   * in any arbitrary  order, rather than the order the user originally
   * provided. Additionally, the list's order may or may not be stable.
   */
  UNORDERED_LIST: 'UNORDERED_LIST',
  /**
   * Denotes that this field returns a non-empty default value if not set.
   * This indicates that if the user provides the empty value in a request,
   * a non-empty value will be returned. The user will not be aware of what
   * non-empty value to expect.
   */
  NON_EMPTY_DEFAULT: 'NON_EMPTY_DEFAULT',
} as const;

/**
 * An indicator of the behavior of a given field (for example, that a field
 * is required in requests, or given as output but ignored as input).
 * This **does not** change the behavior in protocol buffers itself; it only
 * denotes the behavior and may affect how API tooling handles the field.
 * 
 * Note: This enum **may** receive new values in the future.
 */
export type FieldBehavior =
  /**
   * Conventional default for enums. Do not use this.
   */
  | 'FIELD_BEHAVIOR_UNSPECIFIED'
  | 0
  /**
   * Specifically denotes a field as optional.
   * While all fields in protocol buffers are optional, this may be specified
   * for emphasis if appropriate.
   */
  | 'OPTIONAL'
  | 1
  /**
   * Denotes a field as required.
   * This indicates that the field **must** be provided as part of the request,
   * and failure to do so will cause an error (usually `INVALID_ARGUMENT`).
   */
  | 'REQUIRED'
  | 2
  /**
   * Denotes a field as output only.
   * This indicates that the field is provided in responses, but including the
   * field in a request does nothing (the server *must* ignore it and
   * *must not* throw an error as a result of the field's presence).
   */
  | 'OUTPUT_ONLY'
  | 3
  /**
   * Denotes a field as input only.
   * This indicates that the field is provided in requests, and the
   * corresponding field is not included in output.
   */
  | 'INPUT_ONLY'
  | 4
  /**
   * Denotes a field as immutable.
   * This indicates that the field may be set once in a request to create a
   * resource, but may not be changed thereafter.
   */
  | 'IMMUTABLE'
  | 5
  /**
   * Denotes that a (repeated) field is an unordered list.
   * This indicates that the service may provide the elements of the list
   * in any arbitrary  order, rather than the order the user originally
   * provided. Additionally, the list's order may or may not be stable.
   */
  | 'UNORDERED_LIST'
  | 6
  /**
   * Denotes that this field returns a non-empty default value if not set.
   * This indicates that if the user provides the empty value in a request,
   * a non-empty value will be returned. The user will not be aware of what
   * non-empty value to expect.
   */
  | 'NON_EMPTY_DEFAULT'
  | 7

/**
 * An indicator of the behavior of a given field (for example, that a field
 * is required in requests, or given as output but ignored as input).
 * This **does not** change the behavior in protocol buffers itself; it only
 * denotes the behavior and may affect how API tooling handles the field.
 * 
 * Note: This enum **may** receive new values in the future.
 */
export type FieldBehavior__Output = typeof FieldBehavior[keyof typeof FieldBehavior]
