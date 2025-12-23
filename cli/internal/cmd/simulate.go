package cmd

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
	"github.com/a2aproject/a2a/cli/internal/client"
	"github.com/a2aproject/a2a/cli/internal/output"
	"github.com/spf13/cobra"
)

var (
	simMessage   string
	simContextID string
	simTaskID    string
	simTimeout   time.Duration
	simStream    bool
	simLogFile   string
)

// NewSimulateCmd creates the simulate command.
func NewSimulateCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "simulate <url-or-file>",
		Short: "Simulate client/server interaction with an agent",
		Long: `Simulate client/server interaction with an A2A agent endpoint.

The simulate command allows you to:
  - Send messages to an agent and receive responses
  - Maintain conversation context across multiple exchanges
  - Stream responses in real-time
  - Save session logs for debugging

Modes:
  - Single message: Use -m to send one message and exit
  - Interactive: Start a REPL for multi-turn conversation

Interactive Commands:
  /exit, /quit    Exit the simulation
  /history        Show conversation history
  /clear          Clear conversation history
  /status         Show session status
  /save <file>    Save session to file
  /help           Show help

Examples:
  # Send a single message
  a2a simulate -m "What can you do?" https://agent.example.com

  # Start interactive session
  a2a simulate https://agent.example.com

  # Continue existing conversation
  a2a simulate --context-id abc123 https://agent.example.com

  # Stream responses
  a2a simulate --stream -m "Tell me a story" https://agent.example.com

  # Log session to file
  a2a simulate --log session.json https://agent.example.com`,
		Args: cobra.ExactArgs(1),
		RunE: runSimulate,
	}

	cmd.Flags().StringVarP(&simMessage, "message", "m", "",
		"Message to send (non-interactive mode)")
	cmd.Flags().StringVar(&simContextID, "context-id", "",
		"Continue with existing context ID")
	cmd.Flags().StringVar(&simTaskID, "task-id", "",
		"Continue with existing task ID")
	cmd.Flags().DurationVarP(&simTimeout, "timeout", "t", 60*time.Second,
		"Request timeout")
	cmd.Flags().BoolVar(&simStream, "stream", false,
		"Enable streaming responses")
	cmd.Flags().StringVar(&simLogFile, "log", "",
		"Save session log to file")

	return cmd
}

func runSimulate(cmd *cobra.Command, args []string) error {
	input := args[0]
	var targetURL string

	// Determine if input is a URL or file
	if agentcard.IsURL(input) {
		targetURL = input
	} else {
		// Parse agent card file to get URL
		card, err := agentcard.ParseFile(input)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error: failed to parse file: %v\n", err)
			os.Exit(ExitFileNotFound)
		}

		if len(card.SupportedInterfaces) == 0 {
			fmt.Fprintf(os.Stderr, "Error: no supported interfaces found in agent card\n")
			os.Exit(ExitInvalidArguments)
		}

		targetURL = card.SupportedInterfaces[0].URL
	}

	// Create client
	config := client.ClientConfig{
		Timeout:            simTimeout,
		InsecureSkipVerify: false,
		UserAgent:          "a2a-cli/1.0",
	}
	a2aClient := client.NewA2AClient(targetURL, config)

	// Create session manager
	var sessionMgr *client.SessionManager
	if simContextID != "" || simTaskID != "" {
		sessionMgr = client.NewSessionManagerWithIDs(simContextID, simTaskID)
	} else {
		sessionMgr = client.NewSessionManager()
	}

	// Determine output format
	outputFmt, _ := output.ParseFormat(outputFormat)

	if verbose {
		fmt.Fprintf(os.Stderr, "Connecting to %s...\n", targetURL)
		fmt.Fprintf(os.Stderr, "Session ID: %s\n", sessionMgr.Session().ID)
		if simContextID != "" {
			fmt.Fprintf(os.Stderr, "Context ID: %s\n", simContextID)
		}
	}

	// Non-interactive mode: send single message
	if simMessage != "" {
		return sendSingleMessage(a2aClient, sessionMgr, outputFmt)
	}

	// Interactive mode
	return runInteractiveMode(a2aClient, sessionMgr, outputFmt)
}

func sendSingleMessage(a2aClient *client.A2AClient, sessionMgr *client.SessionManager, outputFmt output.Format) error {
	if simStream {
		return sendStreamingMessage(a2aClient, sessionMgr, simMessage, outputFmt)
	}

	resp, err := a2aClient.SendMessage(sessionMgr.Session(), simMessage)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(ExitNetworkError)
	}

	// Output response
	switch outputFmt {
	case output.FormatJSON:
		output.WriteJSON(os.Stdout, resp, true)
	case output.FormatYAML:
		output.WriteYAML(os.Stdout, resp)
	default:
		printTaskResponse(resp)
	}

	// Save session if requested
	if simLogFile != "" {
		if err := sessionMgr.SaveToFile(simLogFile); err != nil {
			fmt.Fprintf(os.Stderr, "Warning: failed to save session: %v\n", err)
		}
	}

	return nil
}

func sendStreamingMessage(a2aClient *client.A2AClient, sessionMgr *client.SessionManager, message string, outputFmt output.Format) error {
	events, err := a2aClient.SendMessageStream(sessionMgr.Session(), message)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(ExitNetworkError)
	}

	for event := range events {
		if event.Error != "" {
			fmt.Fprintf(os.Stderr, "Error: %s\n", event.Error)
			continue
		}

		switch outputFmt {
		case output.FormatJSON:
			output.WriteJSON(os.Stdout, event, false)
			fmt.Println()
		case output.FormatYAML:
			output.WriteYAML(os.Stdout, event)
		default:
			// Print streaming text
			if event.Message != nil {
				for _, part := range event.Message.Parts {
					if part.Text != "" {
						fmt.Print(part.Text)
					}
				}
			}
			// Print status updates
			if event.Status != nil && verbose {
				fmt.Fprintf(os.Stderr, "[Status: %s]\n", event.Status.State)
			}
		}
	}

	// Add newline at end of streaming
	if outputFmt == output.FormatText {
		fmt.Println()
	}

	return nil
}

func runInteractiveMode(a2aClient *client.A2AClient, sessionMgr *client.SessionManager, outputFmt output.Format) error {
	reader := bufio.NewReader(os.Stdin)

	fmt.Println("A2A Interactive Simulation")
	fmt.Println("Type /help for commands, /exit to quit")
	fmt.Println()

	for {
		fmt.Print("> ")
		input, err := reader.ReadString('\n')
		if err != nil {
			break
		}

		input = strings.TrimSpace(input)
		if input == "" {
			continue
		}

		// Handle commands
		if strings.HasPrefix(input, "/") {
			if handleCommand(input, sessionMgr) {
				continue
			}
			// Exit command returns false
			break
		}

		// Send message
		if simStream {
			if err := sendStreamingMessage(a2aClient, sessionMgr, input, outputFmt); err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
			}
		} else {
			resp, err := a2aClient.SendMessage(sessionMgr.Session(), input)
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
				continue
			}

			switch outputFmt {
			case output.FormatJSON:
				output.WriteJSON(os.Stdout, resp, true)
			case output.FormatYAML:
				output.WriteYAML(os.Stdout, resp)
			default:
				printTaskResponse(resp)
			}
		}

		fmt.Println()
	}

	// Save session if requested
	if simLogFile != "" {
		if err := sessionMgr.SaveToFile(simLogFile); err != nil {
			fmt.Fprintf(os.Stderr, "Warning: failed to save session: %v\n", err)
		} else {
			fmt.Fprintf(os.Stderr, "Session saved to %s\n", simLogFile)
		}
	}

	return nil
}

func handleCommand(input string, sessionMgr *client.SessionManager) bool {
	parts := strings.Fields(input)
	if len(parts) == 0 {
		return true
	}

	cmd := strings.ToLower(parts[0])

	switch cmd {
	case "/exit", "/quit":
		fmt.Println("Goodbye!")
		return false

	case "/help":
		printInteractiveHelp()

	case "/history":
		printHistory(sessionMgr)

	case "/clear":
		sessionMgr.ClearHistory()
		fmt.Println("History cleared.")

	case "/status":
		printStatus(sessionMgr)

	case "/save":
		if len(parts) < 2 {
			fmt.Println("Usage: /save <filename>")
		} else {
			filename := parts[1]
			if err := sessionMgr.SaveToFile(filename); err != nil {
				fmt.Fprintf(os.Stderr, "Error: %v\n", err)
			} else {
				fmt.Printf("Session saved to %s\n", filename)
			}
		}

	default:
		fmt.Printf("Unknown command: %s (type /help for commands)\n", cmd)
	}

	return true
}

func printInteractiveHelp() {
	fmt.Println("Commands:")
	fmt.Println("  /exit, /quit    Exit the simulation")
	fmt.Println("  /history        Show conversation history")
	fmt.Println("  /clear          Clear conversation history")
	fmt.Println("  /status         Show session status")
	fmt.Println("  /save <file>    Save session to file")
	fmt.Println("  /help           Show this help")
}

func printHistory(sessionMgr *client.SessionManager) {
	history := sessionMgr.GetHistory()
	if len(history) == 0 {
		fmt.Println("No messages in history.")
		return
	}

	fmt.Printf("Conversation History (%d messages):\n", len(history))
	fmt.Println()

	for i, msg := range history {
		role := "User"
		if msg.Role == "agent" {
			role = "Agent"
		}
		fmt.Printf("[%d] %s:\n", i+1, role)
		// Truncate long messages
		content := msg.Content
		if len(content) > 200 {
			content = content[:197] + "..."
		}
		fmt.Printf("    %s\n", content)
		fmt.Println()
	}
}

func printStatus(sessionMgr *client.SessionManager) {
	status := sessionMgr.Status()
	fmt.Println("Session Status:")
	fmt.Printf("  Session ID:    %s\n", status.ID)
	if status.ContextID != "" {
		fmt.Printf("  Context ID:    %s\n", status.ContextID)
	}
	if status.TaskID != "" {
		fmt.Printf("  Task ID:       %s\n", status.TaskID)
	}
	fmt.Printf("  Messages:      %d\n", status.MessageCount)
	fmt.Printf("  Created:       %s\n", status.CreatedAt.Format(time.RFC3339))
	fmt.Printf("  Updated:       %s\n", status.UpdatedAt.Format(time.RFC3339))
}

func printTaskResponse(resp *client.TaskResponse) {
	// Print status
	fmt.Printf("[%s] ", strings.ToUpper(resp.Status.State))

	// Print agent message
	if resp.Status.Message != nil {
		for _, part := range resp.Status.Message.Parts {
			if part.Text != "" {
				fmt.Println(part.Text)
			}
		}
	}

	// Print error if any
	if resp.Status.Error != nil {
		fmt.Printf("Error: %s - %s\n", resp.Status.Error.Code, resp.Status.Error.Message)
	}

	// Print artifacts if any
	if len(resp.Artifacts) > 0 {
		fmt.Printf("\nArtifacts (%d):\n", len(resp.Artifacts))
		for _, artifact := range resp.Artifacts {
			fmt.Printf("  - %s: %s\n", artifact.Name, artifact.Description)
		}
	}
}

func init() {
	AddCommand(NewSimulateCmd())
}
