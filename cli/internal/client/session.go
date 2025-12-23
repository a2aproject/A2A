package client

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
	"github.com/google/uuid"
)

// SessionManager handles simulation session lifecycle.
type SessionManager struct {
	session *agentcard.SimulationSession
}

// NewSessionManager creates a new session manager with a fresh session.
func NewSessionManager() *SessionManager {
	return &SessionManager{
		session: &agentcard.SimulationSession{
			ID:        uuid.New().String(),
			Messages:  []agentcard.Message{},
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
	}
}

// NewSessionManagerWithIDs creates a session manager with existing IDs.
func NewSessionManagerWithIDs(contextID, taskID string) *SessionManager {
	return &SessionManager{
		session: &agentcard.SimulationSession{
			ID:        uuid.New().String(),
			ContextID: contextID,
			TaskID:    taskID,
			Messages:  []agentcard.Message{},
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
	}
}

// Session returns the current session.
func (m *SessionManager) Session() *agentcard.SimulationSession {
	return m.session
}

// AddMessage adds a message to the session history.
func (m *SessionManager) AddMessage(role, content string) {
	m.session.Messages = append(m.session.Messages, agentcard.Message{
		Role:    role,
		Content: content,
	})
	m.session.UpdatedAt = time.Now()
}

// GetHistory returns the message history.
func (m *SessionManager) GetHistory() []agentcard.Message {
	return m.session.Messages
}

// ClearHistory clears the message history but keeps session IDs.
func (m *SessionManager) ClearHistory() {
	m.session.Messages = []agentcard.Message{}
	m.session.UpdatedAt = time.Now()
}

// UpdateContextID updates the context ID.
func (m *SessionManager) UpdateContextID(contextID string) {
	m.session.ContextID = contextID
	m.session.UpdatedAt = time.Now()
}

// UpdateTaskID updates the task ID.
func (m *SessionManager) UpdateTaskID(taskID string) {
	m.session.TaskID = taskID
	m.session.UpdatedAt = time.Now()
}

// MessageCount returns the number of messages in history.
func (m *SessionManager) MessageCount() int {
	return len(m.session.Messages)
}

// SaveToFile saves the session to a JSON file.
func (m *SessionManager) SaveToFile(filename string) error {
	data, err := json.MarshalIndent(m.session, "", "  ")
	if err != nil {
		return fmt.Errorf("failed to marshal session: %w", err)
	}

	if err := os.WriteFile(filename, data, 0644); err != nil {
		return fmt.Errorf("failed to write file: %w", err)
	}

	return nil
}

// LoadFromFile loads a session from a JSON file.
func (m *SessionManager) LoadFromFile(filename string) error {
	data, err := os.ReadFile(filename)
	if err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}

	var session agentcard.SimulationSession
	if err := json.Unmarshal(data, &session); err != nil {
		return fmt.Errorf("failed to parse session: %w", err)
	}

	m.session = &session
	return nil
}

// ToJSON returns the session as a JSON string.
func (m *SessionManager) ToJSON() (string, error) {
	data, err := json.MarshalIndent(m.session, "", "  ")
	if err != nil {
		return "", fmt.Errorf("failed to marshal session: %w", err)
	}
	return string(data), nil
}

// SessionStatus returns a summary of the session status.
type SessionStatus struct {
	ID           string    `json:"id"`
	ContextID    string    `json:"contextId,omitempty"`
	TaskID       string    `json:"taskId,omitempty"`
	MessageCount int       `json:"messageCount"`
	CreatedAt    time.Time `json:"createdAt"`
	UpdatedAt    time.Time `json:"updatedAt"`
}

// Status returns the current session status.
func (m *SessionManager) Status() SessionStatus {
	return SessionStatus{
		ID:           m.session.ID,
		ContextID:    m.session.ContextID,
		TaskID:       m.session.TaskID,
		MessageCount: len(m.session.Messages),
		CreatedAt:    m.session.CreatedAt,
		UpdatedAt:    m.session.UpdatedAt,
	}
}
