package cmd

import (
	"fmt"
	"os"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
	"github.com/a2aproject/a2a/cli/internal/output"
	"github.com/spf13/cobra"
)

var (
	generateName        string
	generateDescription string
	generateVersion     string
	generateURL         string
	generateSkills      []string
	generateFormat      string
	generateMinimal     bool
)

// NewGenerateCmd creates the generate command.
func NewGenerateCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "generate [output-file]",
		Short: "Generate an Agent Card template",
		Long: `Generate a valid Agent Card template with customizable parameters.

The generated template includes all required fields for the A2A protocol.
You can customize the agent name, description, version, and skills.

Examples:
  # Generate basic template to stdout
  a2a generate

  # Generate with custom name and save to file
  a2a generate -n "Recipe Agent" -d "Helps with cooking" agent-card.json

  # Generate YAML with skills
  a2a generate -f yaml -s "search:Search:Search for recipes" agent-card.yaml

  # Generate minimal template
  a2a generate --minimal`,
		Args: cobra.MaximumNArgs(1),
		RunE: runGenerate,
	}

	// Flags
	cmd.Flags().StringVarP(&generateName, "name", "n", "My Agent",
		"Agent name")
	cmd.Flags().StringVarP(&generateDescription, "description", "d", "An A2A agent",
		"Agent description")
	cmd.Flags().StringVar(&generateVersion, "version", "1.0.0",
		"Agent version")
	cmd.Flags().StringVarP(&generateURL, "url", "u", "",
		"Agent endpoint URL")
	cmd.Flags().StringArrayVarP(&generateSkills, "skill", "s", nil,
		"Add skill (format: id:name:description)")
	cmd.Flags().StringVarP(&generateFormat, "format", "f", "json",
		"Output format: json, yaml")
	cmd.Flags().BoolVarP(&generateMinimal, "minimal", "m", false,
		"Generate minimal template (required fields only)")

	return cmd
}

func runGenerate(cmd *cobra.Command, args []string) error {
	// Parse format
	format, err := output.ParseFormat(generateFormat)
	if err != nil {
		return fmt.Errorf("invalid format: %w", err)
	}

	// For generate command, we support json and yaml only
	if format == output.FormatText {
		format = output.FormatJSON
	}

	// Build template options
	opts := agentcard.TemplateOptions{
		Name:        generateName,
		Description: generateDescription,
		Version:     generateVersion,
		URL:         generateURL,
		Skills:      generateSkills,
		Minimal:     generateMinimal,
	}

	// Generate the template
	card, err := agentcard.GenerateTemplate(opts)
	if err != nil {
		return fmt.Errorf("failed to generate template: %w", err)
	}

	// Determine output destination
	var outputFile string
	if len(args) > 0 {
		outputFile = args[0]
	}

	// Serialize the card
	var data []byte
	switch format {
	case output.FormatYAML:
		data, err = card.ToYAML()
	default:
		data, err = card.ToJSON(true)
	}
	if err != nil {
		return fmt.Errorf("failed to serialize: %w", err)
	}

	// Write output
	if outputFile != "" {
		if err := os.WriteFile(outputFile, data, 0644); err != nil {
			return fmt.Errorf("failed to write file: %w", err)
		}
		if verbose {
			fmt.Fprintf(os.Stderr, "Agent Card template written to %s\n", outputFile)
		}
	} else {
		fmt.Print(string(data))
	}

	return nil
}

func init() {
	AddCommand(NewGenerateCmd())
}
