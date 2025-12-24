package cmd

import (
	"fmt"
	"os"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
	"github.com/a2aproject/a2a/cli/internal/output"
	"github.com/a2aproject/a2a/cli/internal/validator"
	"github.com/spf13/cobra"
)

var (
	validateStrict bool
	validateQuiet  bool
)

// NewValidateCmd creates the validate command.
func NewValidateCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "validate <file>",
		Short: "Validate an Agent Card file",
		Long: `Validate an Agent Card file against the A2A protocol specification.

The validation checks:
  - Required fields are present
  - Field types are correct
  - Values match expected formats
  - Nested structures are valid

Examples:
  # Validate a JSON file
  a2a validate agent-card.json

  # Validate with strict mode (fail on warnings)
  a2a validate --strict agent-card.yaml

  # Check validity using exit code
  a2a validate -q agent-card.json && echo "Valid"`,
		Args: cobra.ExactArgs(1),
		RunE: runValidate,
	}

	cmd.Flags().BoolVar(&validateStrict, "strict", false,
		"Fail on warnings")
	cmd.Flags().BoolVarP(&validateQuiet, "quiet", "q", false,
		"Suppress output, use exit code only")

	return cmd
}

func runValidate(cmd *cobra.Command, args []string) error {
	filePath := args[0]

	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		return fmt.Errorf("file not found: %s", filePath)
	}

	// Read and parse the file
	data, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read file: %w", err)
	}

	// Detect format
	format := agentcard.DetectFormat(filePath, data)

	// Validate
	result, err := validator.Validate(data, format)
	if err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}

	// Determine output format
	outputFmt, _ := output.ParseFormat(outputFormat)

	// Check for strict mode failures
	if validateStrict && len(result.Warnings) > 0 {
		result.Valid = false
		result.Errors = append(result.Errors, result.Warnings...)
		result.Warnings = nil
	}

	// Output results
	if !validateQuiet {
		switch outputFmt {
		case output.FormatJSON:
			output.WriteJSON(os.Stdout, result, true)
		case output.FormatYAML:
			output.WriteYAML(os.Stdout, result)
		default:
			printValidationResultText(filePath, data, result)
		}
	}

	// Exit with appropriate code
	if !result.Valid {
		os.Exit(ExitValidationFailed)
	}

	return nil
}

func printValidationResultText(filePath string, data []byte, result *agentcard.ValidationResult) {
	if result.Valid {
		output.PrintSuccess(os.Stdout, "Agent Card is valid")
		fmt.Println()

		// Parse the card to show summary
		format := agentcard.DetectFormat(filePath, data)
		card, err := agentcard.Parse(data, format)
		if err == nil {
			fmt.Printf("Validated: %s\n", filePath)
			fmt.Printf("Protocol Version: %s\n", card.ProtocolVersion)
			fmt.Printf("Agent: %s v%s\n", card.Name, card.Version)
			fmt.Printf("Skills: %d\n", len(card.Skills))
		}

		// Show warnings if any
		if len(result.Warnings) > 0 {
			fmt.Println()
			fmt.Println("Warnings:")
			for _, w := range result.Warnings {
				fmt.Printf("  - %s: %s\n", w.Path, w.Message)
			}
		}
	} else {
		output.PrintError(os.Stdout, "Agent Card validation failed")
		fmt.Println()
		fmt.Println("Errors:")
		for _, e := range result.Errors {
			if e.Line > 0 {
				fmt.Printf("  - %s (line %d): %s\n", e.Path, e.Line, e.Message)
			} else {
				fmt.Printf("  - %s: %s\n", e.Path, e.Message)
			}
		}
	}
}

func init() {
	AddCommand(NewValidateCmd())
}
