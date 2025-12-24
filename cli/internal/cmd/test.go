package cmd

import (
	"fmt"
	"os"
	"time"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
	"github.com/a2aproject/a2a/cli/internal/client"
	"github.com/a2aproject/a2a/cli/internal/output"
	"github.com/spf13/cobra"
)

var (
	testTimeout   time.Duration
	testInsecure  bool
	testFetchCard bool
)

// NewTestCmd creates the test command.
func NewTestCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "test <url-or-file>",
		Short: "Test connectivity to an agent endpoint",
		Long: `Test connectivity to an agent endpoint and verify A2A compliance.

The test checks:
  - Endpoint reachability
  - Response time
  - TLS certificate validity
  - Agent Card availability (optional)

Examples:
  # Test URL directly
  a2a test https://agent.example.com

  # Test endpoint from Agent Card file
  a2a test agent-card.json

  # Test with custom timeout
  a2a test -t 10s https://agent.example.com

  # Test without TLS verification (development)
  a2a test -k https://localhost:8080`,
		Args: cobra.ExactArgs(1),
		RunE: runTest,
	}

	cmd.Flags().DurationVarP(&testTimeout, "timeout", "t", 30*time.Second,
		"Connection timeout")
	cmd.Flags().BoolVarP(&testInsecure, "insecure", "k", false,
		"Skip TLS certificate verification")
	cmd.Flags().BoolVar(&testFetchCard, "fetch-card", true,
		"Attempt to fetch agent card from endpoint")

	return cmd
}

func runTest(cmd *cobra.Command, args []string) error {
	input := args[0]
	var targetURL string

	// Determine if input is a URL or file
	if agentcard.IsURL(input) {
		targetURL = input
	} else {
		// Parse agent card file to get URL
		card, err := agentcard.ParseFile(input)
		if err != nil {
			return fmt.Errorf("failed to parse file: %w", err)
		}

		if len(card.SupportedInterfaces) == 0 {
			return fmt.Errorf("no supported interfaces found in agent card")
		}

		targetURL = card.SupportedInterfaces[0].URL
	}

	// Create client
	config := client.ClientConfig{
		Timeout:            testTimeout,
		InsecureSkipVerify: testInsecure,
		UserAgent:          "a2a-cli/1.0",
	}
	c := client.New(config)

	// Show progress
	if verbose {
		fmt.Fprintf(os.Stderr, "Testing connection to %s...\n", targetURL)
	}

	// Test connection
	result, err := c.TestConnection(targetURL, testFetchCard)
	if err != nil {
		return fmt.Errorf("connection test failed: %w", err)
	}

	// Determine output format
	outputFmt, _ := output.ParseFormat(outputFormat)

	// Output results
	switch outputFmt {
	case output.FormatJSON:
		output.WriteJSON(os.Stdout, formatTestResultForJSON(result), true)
	case output.FormatYAML:
		output.WriteYAML(os.Stdout, formatTestResultForJSON(result))
	default:
		printTestResultText(result)
	}

	// Return error if not reachable
	if !result.Reachable {
		return fmt.Errorf("endpoint not reachable: %s", result.Error)
	}

	return nil
}

// TestResultJSON is the JSON-friendly version of ConnectionTestResult.
type TestResultJSON struct {
	URL          string            `json:"url"`
	Reachable    bool              `json:"reachable"`
	ResponseTime string            `json:"responseTime"`
	StatusCode   int               `json:"statusCode,omitempty"`
	Error        string            `json:"error,omitempty"`
	TLSValid     bool              `json:"tlsValid,omitempty"`
	TLSExpiry    string            `json:"tlsExpiry,omitempty"`
	AgentCard    *AgentCardSummary `json:"agentCard,omitempty"`
}

// AgentCardSummary is a summary of an agent card for JSON output.
type AgentCardSummary struct {
	Name    string `json:"name"`
	Version string `json:"version"`
	Skills  int    `json:"skills"`
}

func formatTestResultForJSON(result *agentcard.ConnectionTestResult) *TestResultJSON {
	r := &TestResultJSON{
		URL:          result.URL,
		Reachable:    result.Reachable,
		ResponseTime: result.ResponseTime.String(),
		StatusCode:   result.StatusCode,
		Error:        result.Error,
		TLSValid:     result.TLSValid,
	}

	if result.TLSExpiry != nil {
		r.TLSExpiry = result.TLSExpiry.Format(time.RFC3339)
	}

	if result.AgentCard != nil {
		r.AgentCard = &AgentCardSummary{
			Name:    result.AgentCard.Name,
			Version: result.AgentCard.Version,
			Skills:  len(result.AgentCard.Skills),
		}
	}

	return r
}

func printTestResultText(result *agentcard.ConnectionTestResult) {
	if result.Reachable {
		output.PrintSuccess(os.Stdout, "Connection successful")
	} else {
		output.PrintError(os.Stdout, "Connection failed")
	}
	fmt.Println()

	// Print details
	fmt.Printf("URL:           %s\n", result.URL)

	if result.Reachable {
		fmt.Printf("Status:        %d\n", result.StatusCode)
		fmt.Printf("Response Time: %s\n", result.ResponseTime.Round(time.Millisecond))

		if result.TLSValid {
			if result.TLSExpiry != nil {
				days := client.DaysUntilExpiry(*result.TLSExpiry)
				fmt.Printf("TLS:           Valid (expires in %d days)\n", days)
			} else {
				fmt.Printf("TLS:           Valid\n")
			}
		}

		if result.AgentCard != nil {
			fmt.Printf("Agent Card:    \u2713 Retrieved\n")
			fmt.Printf("  Name:        %s\n", result.AgentCard.Name)
			fmt.Printf("  Version:     %s\n", result.AgentCard.Version)
			fmt.Printf("  Skills:      %d\n", len(result.AgentCard.Skills))
		} else if testFetchCard {
			fmt.Printf("Agent Card:    \u2717 Not retrieved\n")
		}
	} else {
		fmt.Printf("Error:         %s\n", result.Error)
	}
}

func init() {
	AddCommand(NewTestCmd())
}
