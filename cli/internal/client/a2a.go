// Package client provides HTTP client utilities for A2A operations.
package client

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
	"github.com/google/uuid"
)

// A2AClient handles A2A protocol interactions.
type A2AClient struct {
	httpClient *http.Client
	config     ClientConfig
	baseURL    string
}

// NewA2AClient creates a new A2A protocol client.
func NewA2AClient(baseURL string, config ClientConfig) *A2AClient {
	return &A2AClient{
		httpClient: New(config).httpClient,
		config:     config,
		baseURL:    strings.TrimSuffix(baseURL, "/"),
	}
}

// JSONRPCRequest represents a JSON-RPC 2.0 request.
type JSONRPCRequest struct {
	JSONRPC string      `json:"jsonrpc"`
	ID      string      `json:"id"`
	Method  string      `json:"method"`
	Params  interface{} `json:"params,omitempty"`
}

// JSONRPCResponse represents a JSON-RPC 2.0 response.
type JSONRPCResponse struct {
	JSONRPC string           `json:"jsonrpc"`
	ID      string           `json:"id,omitempty"`
	Result  *json.RawMessage `json:"result,omitempty"`
	Error   *JSONRPCError    `json:"error,omitempty"`
}

// JSONRPCError represents a JSON-RPC error.
type JSONRPCError struct {
	Code    int         `json:"code"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

// SendMessageParams represents parameters for message/send.
type SendMessageParams struct {
	Message            MessagePayload `json:"message"`
	Configuration      *TaskConfig    `json:"configuration,omitempty"`
	Metadata           interface{}    `json:"metadata,omitempty"`
	HistoryLength      int            `json:"historyLength,omitempty"`
	AcceptedOutputMode []string       `json:"acceptedOutputMode,omitempty"`
	PushNotification   *PushConfig    `json:"pushNotification,omitempty"`
}

// MessagePayload represents an A2A message payload.
type MessagePayload struct {
	Role       string `json:"role"`
	Parts      []Part `json:"parts"`
	MessageID  string `json:"messageId,omitempty"`
	ContextID  string `json:"contextId,omitempty"`
	TaskID     string `json:"taskId,omitempty"`
	ReferToIDs string `json:"referToMessageId,omitempty"`
}

// Part represents a message part.
type Part struct {
	Type string `json:"type"` // "text", "file", "data"
	Text string `json:"text,omitempty"`
	File *File  `json:"file,omitempty"`
	Data *Data  `json:"data,omitempty"`
}

// File represents a file attachment.
type File struct {
	URI       string `json:"uri,omitempty"`
	Bytes     string `json:"bytes,omitempty"` // base64 encoded
	MediaType string `json:"mimeType,omitempty"`
	Name      string `json:"name,omitempty"`
}

// Data represents structured data.
type Data struct {
	MimeType string      `json:"mimeType"`
	Data     interface{} `json:"data"`
}

// TaskConfig represents task configuration.
type TaskConfig struct {
	Blocking         bool   `json:"blocking,omitempty"`
	HistoryLength    int    `json:"historyLength,omitempty"`
	AcceptedModes    string `json:"acceptedOutputModes,omitempty"`
	PushNotification bool   `json:"pushNotification,omitempty"`
}

// PushConfig represents push notification configuration.
type PushConfig struct {
	URL   string `json:"url"`
	Token string `json:"token,omitempty"`
}

// TaskResponse represents a task response from the agent.
type TaskResponse struct {
	ID          string           `json:"id"`
	ContextID   string           `json:"contextId"`
	Status      TaskStatus       `json:"status"`
	History     []MessagePayload `json:"history,omitempty"`
	Artifacts   []Artifact       `json:"artifacts,omitempty"`
	Metadata    interface{}      `json:"metadata,omitempty"`
	CreatedTime string           `json:"createdTime,omitempty"`
	UpdatedTime string           `json:"updatedTime,omitempty"`
}

// TaskStatus represents task status.
type TaskStatus struct {
	State   string          `json:"state"` // "submitted", "working", "input-required", "completed", "canceled", "failed", "unknown"
	Message *MessagePayload `json:"message,omitempty"`
	Error   *TaskError      `json:"error,omitempty"`
}

// TaskError represents a task error.
type TaskError struct {
	Code    string `json:"code"`
	Message string `json:"message"`
}

// Artifact represents a task artifact.
type Artifact struct {
	Name        string `json:"name"`
	Description string `json:"description,omitempty"`
	Parts       []Part `json:"parts"`
	Index       int    `json:"index"`
	Append      bool   `json:"append,omitempty"`
	LastChunk   bool   `json:"lastChunk,omitempty"`
}

// StreamEvent represents a server-sent event.
type StreamEvent struct {
	Type    string          `json:"type"` // "task", "status", "artifact", "message"
	Task    *TaskResponse   `json:"task,omitempty"`
	Status  *TaskStatus     `json:"status,omitempty"`
	Message *MessagePayload `json:"message,omitempty"`
	Error   string          `json:"error,omitempty"`
}

// buildMessageParams creates SendMessageParams for a text message with session context.
func buildMessageParams(session *agentcard.SimulationSession, content string) SendMessageParams {
	params := SendMessageParams{
		Message: MessagePayload{
			Role: "user",
			Parts: []Part{
				{Type: "text", Text: content},
			},
			MessageID: uuid.New().String(),
		},
	}

	if session.ContextID != "" {
		params.Message.ContextID = session.ContextID
	}
	if session.TaskID != "" {
		params.Message.TaskID = session.TaskID
	}

	return params
}

// SendMessage sends a message to the agent and returns the response.
func (c *A2AClient) SendMessage(session *agentcard.SimulationSession, content string) (*TaskResponse, error) {
	params := buildMessageParams(session, content)

	// Build JSON-RPC request
	req := JSONRPCRequest{
		JSONRPC: "2.0",
		ID:      uuid.New().String(),
		Method:  "message/send",
		Params:  params,
	}

	// Send request
	resp, err := c.doRequest(req)
	if err != nil {
		return nil, err
	}

	// Parse response
	if resp.Error != nil {
		return nil, fmt.Errorf("agent error [%d]: %s", resp.Error.Code, resp.Error.Message)
	}

	if resp.Result == nil {
		return nil, fmt.Errorf("empty response from agent")
	}

	var taskResp TaskResponse
	if err := json.Unmarshal(*resp.Result, &taskResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	// Update session
	session.TaskID = taskResp.ID
	session.ContextID = taskResp.ContextID
	session.UpdatedAt = time.Now()

	// Add user message to history
	session.Messages = append(session.Messages, agentcard.Message{
		Role:    "user",
		Content: content,
	})

	// Add agent response to history if available
	if taskResp.Status.Message != nil && len(taskResp.Status.Message.Parts) > 0 {
		var agentContent strings.Builder
		for _, part := range taskResp.Status.Message.Parts {
			if part.Text != "" {
				agentContent.WriteString(part.Text)
			}
		}
		session.Messages = append(session.Messages, agentcard.Message{
			Role:    "agent",
			Content: agentContent.String(),
		})
	}

	return &taskResp, nil
}

// SendMessageStream sends a message and returns a channel of streaming events.
func (c *A2AClient) SendMessageStream(session *agentcard.SimulationSession, content string) (<-chan StreamEvent, error) {
	params := buildMessageParams(session, content)

	// Build JSON-RPC request
	req := JSONRPCRequest{
		JSONRPC: "2.0",
		ID:      uuid.New().String(),
		Method:  "message/stream",
		Params:  params,
	}

	// Add user message to history
	session.Messages = append(session.Messages, agentcard.Message{
		Role:    "user",
		Content: content,
	})

	events := make(chan StreamEvent, 10)

	go func() {
		defer close(events)

		resp, err := c.doStreamRequest(req)
		if err != nil {
			events <- StreamEvent{Type: "error", Error: err.Error()}
			return
		}
		defer resp.Body.Close()

		// Parse SSE stream
		reader := bufio.NewReader(resp.Body)
		var agentContent strings.Builder

		for {
			line, err := reader.ReadString('\n')
			if err != nil {
				if err != io.EOF {
					events <- StreamEvent{Type: "error", Error: err.Error()}
				}
				break
			}

			line = strings.TrimSpace(line)
			if line == "" {
				continue
			}

			// Parse SSE event
			if strings.HasPrefix(line, "data:") {
				data := strings.TrimPrefix(line, "data:")
				data = strings.TrimSpace(data)

				if data == "[DONE]" {
					break
				}

				var event StreamEvent
				if err := json.Unmarshal([]byte(data), &event); err != nil {
					events <- StreamEvent{Type: "error", Error: fmt.Sprintf("failed to parse event: %v", err)}
					continue
				}

				// Collect agent response text
				if event.Message != nil {
					for _, part := range event.Message.Parts {
						if part.Text != "" {
							agentContent.WriteString(part.Text)
						}
					}
				}

				// Update session on task response
				if event.Task != nil {
					session.TaskID = event.Task.ID
					session.ContextID = event.Task.ContextID
					session.UpdatedAt = time.Now()
				}

				events <- event
			}
		}

		// Add collected agent response to history
		if agentContent.Len() > 0 {
			session.Messages = append(session.Messages, agentcard.Message{
				Role:    "agent",
				Content: agentContent.String(),
			})
		}
	}()

	return events, nil
}

// GetTaskStatus retrieves the current status of a task.
func (c *A2AClient) GetTaskStatus(taskID string) (*TaskResponse, error) {
	req := JSONRPCRequest{
		JSONRPC: "2.0",
		ID:      uuid.New().String(),
		Method:  "tasks/get",
		Params:  map[string]string{"id": taskID},
	}

	resp, err := c.doRequest(req)
	if err != nil {
		return nil, err
	}

	if resp.Error != nil {
		return nil, fmt.Errorf("agent error [%d]: %s", resp.Error.Code, resp.Error.Message)
	}

	if resp.Result == nil {
		return nil, fmt.Errorf("empty response from agent")
	}

	var taskResp TaskResponse
	if err := json.Unmarshal(*resp.Result, &taskResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &taskResp, nil
}

// CancelTask cancels an in-progress task.
func (c *A2AClient) CancelTask(taskID string) error {
	req := JSONRPCRequest{
		JSONRPC: "2.0",
		ID:      uuid.New().String(),
		Method:  "tasks/cancel",
		Params:  map[string]string{"id": taskID},
	}

	resp, err := c.doRequest(req)
	if err != nil {
		return err
	}

	if resp.Error != nil {
		return fmt.Errorf("agent error [%d]: %s", resp.Error.Code, resp.Error.Message)
	}

	return nil
}

func (c *A2AClient) doRequest(req JSONRPCRequest) (*JSONRPCResponse, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	httpReq, err := http.NewRequest(http.MethodPost, c.baseURL, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Accept", "application/json")
	httpReq.Header.Set("User-Agent", c.config.UserAgent)

	httpResp, err := c.httpClient.Do(httpReq)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer httpResp.Body.Close()

	respBody, err := io.ReadAll(httpResp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	var resp JSONRPCResponse
	if err := json.Unmarshal(respBody, &resp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &resp, nil
}

func (c *A2AClient) doStreamRequest(req JSONRPCRequest) (*http.Response, error) {
	body, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	httpReq, err := http.NewRequest(http.MethodPost, c.baseURL, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Accept", "text/event-stream")
	httpReq.Header.Set("User-Agent", c.config.UserAgent)

	return c.httpClient.Do(httpReq)
}
