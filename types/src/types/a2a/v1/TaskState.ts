// Original file: ../specification/grpc/a2a.proto

/**
 * --8<-- [start:TaskState]
 * The set of states a Task can be in.
 */
export const TaskState = {
  TASK_STATE_UNSPECIFIED: 'TASK_STATE_UNSPECIFIED',
  /**
   * Represents the status that acknowledges a task is created
   */
  TASK_STATE_SUBMITTED: 'TASK_STATE_SUBMITTED',
  /**
   * Represents the status that a task is actively being processed
   */
  TASK_STATE_WORKING: 'TASK_STATE_WORKING',
  /**
   * Represents the status a task is finished. This is a terminal state
   */
  TASK_STATE_COMPLETED: 'TASK_STATE_COMPLETED',
  /**
   * Represents the status a task is done but failed. This is a terminal state
   */
  TASK_STATE_FAILED: 'TASK_STATE_FAILED',
  /**
   * Represents the status a task was cancelled before it finished.
   * This is a terminal state.
   */
  TASK_STATE_CANCELLED: 'TASK_STATE_CANCELLED',
  /**
   * Represents the status that the task requires information to complete.
   * This is an interrupted state.
   */
  TASK_STATE_INPUT_REQUIRED: 'TASK_STATE_INPUT_REQUIRED',
  /**
   * Represents the status that the agent has decided to not perform the task.
   * This may be done during initial task creation or later once an agent
   * has determined it can't or won't proceed. This is a terminal state.
   */
  TASK_STATE_REJECTED: 'TASK_STATE_REJECTED',
  /**
   * Represents the state that some authentication is needed from the upstream
   * client. Authentication is expected to come out-of-band thus this is not
   * an interrupted or terminal state.
   */
  TASK_STATE_AUTH_REQUIRED: 'TASK_STATE_AUTH_REQUIRED',
} as const;

/**
 * --8<-- [start:TaskState]
 * The set of states a Task can be in.
 */
export type TaskState =
  | 'TASK_STATE_UNSPECIFIED'
  | 0
  /**
   * Represents the status that acknowledges a task is created
   */
  | 'TASK_STATE_SUBMITTED'
  | 1
  /**
   * Represents the status that a task is actively being processed
   */
  | 'TASK_STATE_WORKING'
  | 2
  /**
   * Represents the status a task is finished. This is a terminal state
   */
  | 'TASK_STATE_COMPLETED'
  | 3
  /**
   * Represents the status a task is done but failed. This is a terminal state
   */
  | 'TASK_STATE_FAILED'
  | 4
  /**
   * Represents the status a task was cancelled before it finished.
   * This is a terminal state.
   */
  | 'TASK_STATE_CANCELLED'
  | 5
  /**
   * Represents the status that the task requires information to complete.
   * This is an interrupted state.
   */
  | 'TASK_STATE_INPUT_REQUIRED'
  | 6
  /**
   * Represents the status that the agent has decided to not perform the task.
   * This may be done during initial task creation or later once an agent
   * has determined it can't or won't proceed. This is a terminal state.
   */
  | 'TASK_STATE_REJECTED'
  | 7
  /**
   * Represents the state that some authentication is needed from the upstream
   * client. Authentication is expected to come out-of-band thus this is not
   * an interrupted or terminal state.
   */
  | 'TASK_STATE_AUTH_REQUIRED'
  | 8

/**
 * --8<-- [start:TaskState]
 * The set of states a Task can be in.
 */
export type TaskState__Output = typeof TaskState[keyof typeof TaskState]
