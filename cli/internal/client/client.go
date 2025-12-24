// Package client provides HTTP client utilities for A2A operations.
package client

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
)

// ClientConfig configures the HTTP client.
type ClientConfig struct {
	Timeout            time.Duration
	InsecureSkipVerify bool
	UserAgent          string
}

// DefaultClientConfig returns default client configuration.
func DefaultClientConfig() ClientConfig {
	return ClientConfig{
		Timeout:            30 * time.Second,
		InsecureSkipVerify: false,
		UserAgent:          "a2a-cli/1.0",
	}
}

// Client is an HTTP client for A2A operations.
type Client struct {
	httpClient *http.Client
	config     ClientConfig
}

// New creates a new A2A client.
func New(config ClientConfig) *Client {
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{
			InsecureSkipVerify: config.InsecureSkipVerify,
		},
		TLSHandshakeTimeout: 10 * time.Second,
		DisableKeepAlives:   false,
		MaxIdleConns:        10,
		IdleConnTimeout:     30 * time.Second,
	}

	return &Client{
		httpClient: &http.Client{
			Timeout:   config.Timeout,
			Transport: transport,
		},
		config: config,
	}
}

// TestConnection tests connectivity to an endpoint.
func (c *Client) TestConnection(url string, fetchCard bool) (*agentcard.ConnectionTestResult, error) {
	result := &agentcard.ConnectionTestResult{
		URL: url,
	}

	// Measure response time
	start := time.Now()

	// Make the request
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		result.Error = fmt.Sprintf("failed to create request: %v", err)
		return result, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("User-Agent", c.config.UserAgent)
	req.Header.Set("Accept", "application/json, application/yaml, text/yaml")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		result.Error = fmt.Sprintf("connection failed: %v", err)
		return result, fmt.Errorf("connection failed: %w", err)
	}
	defer resp.Body.Close()

	result.ResponseTime = time.Since(start)
	result.Reachable = true
	result.StatusCode = resp.StatusCode

	// Check TLS info
	if resp.TLS != nil {
		result.TLSValid = true
		if len(resp.TLS.PeerCertificates) > 0 {
			cert := resp.TLS.PeerCertificates[0]
			expiry := cert.NotAfter
			result.TLSExpiry = &expiry
		}
	}

	// Optionally fetch agent card
	if fetchCard && resp.StatusCode == http.StatusOK {
		body, err := io.ReadAll(resp.Body)
		if err == nil {
			card, err := agentcard.Parse(body, agentcard.FormatJSON)
			if err == nil {
				result.AgentCard = card
			}
		}
	}

	return result, nil
}

// FetchAgentCard fetches an agent card from the well-known location.
func (c *Client) FetchAgentCard(baseURL string) (*agentcard.AgentCard, error) {
	url := baseURL + "/.well-known/agent-card.json"

	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("User-Agent", c.config.UserAgent)
	req.Header.Set("Accept", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch agent card: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	return agentcard.Parse(body, agentcard.FormatJSON)
}

// GetTLSCertInfo gets TLS certificate information for a URL.
func (c *Client) GetTLSCertInfo(url string) (*x509.Certificate, error) {
	req, err := http.NewRequest(http.MethodHead, url, nil)
	if err != nil {
		return nil, err
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.TLS == nil || len(resp.TLS.PeerCertificates) == 0 {
		return nil, fmt.Errorf("no TLS certificate found")
	}

	return resp.TLS.PeerCertificates[0], nil
}

// DaysUntilExpiry calculates days until a certificate expires.
func DaysUntilExpiry(expiry time.Time) int {
	return int(time.Until(expiry).Hours() / 24)
}
