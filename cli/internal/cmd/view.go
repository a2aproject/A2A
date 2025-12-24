package cmd

import (
	"fmt"
	"os"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
	"github.com/a2aproject/a2a/cli/internal/output"
	"github.com/spf13/cobra"
)

var (
	viewSkills       bool
	viewCapabilities bool
	viewSecurity     bool
)

// NewViewCmd creates the view command.
func NewViewCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "view <file-or-url>",
		Short: "View agent capabilities and skills",
		Long: `View agent capabilities and skills in a human-readable format.

The view command displays:
  - Agent overview (name, version, description)
  - Capabilities (streaming, push notifications, etc.)
  - Skills with descriptions
  - Security configuration (optional)

Examples:
  # View agent overview
  a2a view agent-card.json

  # View from remote URL
  a2a view https://agent.example.com/.well-known/agent-card.json

  # View detailed skills
  a2a view -s agent-card.json

  # View capabilities only
  a2a view -c agent-card.json

  # View security configuration
  a2a view --security agent-card.json`,
		Args: cobra.ExactArgs(1),
		RunE: runView,
	}

	cmd.Flags().BoolVarP(&viewSkills, "skills", "s", false,
		"Show detailed skill information")
	cmd.Flags().BoolVarP(&viewCapabilities, "capabilities", "c", false,
		"Show capabilities only")
	cmd.Flags().BoolVar(&viewSecurity, "security", false,
		"Show security configuration")

	return cmd
}

func runView(cmd *cobra.Command, args []string) error {
	input := args[0]

	// Parse agent card from file or URL
	opts := agentcard.DefaultParseOptions()
	card, err := agentcard.ParseFileOrURL(input, opts)
	if err != nil {
		if agentcard.IsURL(input) {
			return fmt.Errorf("failed to fetch URL: %w", err)
		}
		return fmt.Errorf("failed to parse file: %w", err)
	}

	// Determine output format
	outputFmt, _ := output.ParseFormat(outputFormat)

	// JSON/YAML output - always output the full card
	if outputFmt == output.FormatJSON {
		output.WriteJSON(os.Stdout, card, true)
		return nil
	}
	if outputFmt == output.FormatYAML {
		output.WriteYAML(os.Stdout, card)
		return nil
	}

	// Text output - respect view options
	if viewCapabilities {
		output.WriteCapabilities(os.Stdout, &card.Capabilities)
		return nil
	}

	if viewSkills {
		output.WriteSkillsTable(os.Stdout, card.Skills)
		return nil
	}

	if viewSecurity {
		output.WriteSecurityConfig(os.Stdout, card)
		return nil
	}

	// Default: show overview
	output.WriteAgentCardOverview(os.Stdout, card)

	return nil
}

func init() {
	AddCommand(NewViewCmd())
}
