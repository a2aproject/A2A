package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

var (
	// Global flags
	outputFormat string
	verbose      bool
)

// rootCmd represents the base command.
var rootCmd = &cobra.Command{
	Use:   "a2a",
	Short: "A2A Protocol CLI Tool",
	Long: `A2A CLI is a command-line tool for working with the A2A Protocol.

It provides commands to:
  - Generate Agent Card templates
  - Validate Agent Cards against the protocol specification
  - Test connectivity to agent endpoints
  - View agent capabilities and skills
  - Simulate client-server interactions

For more information, visit: https://a2a-protocol.org`,
	SilenceUsage:  true,
	SilenceErrors: true,
}

// Execute runs the root command.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(ExitGeneralError)
	}
}

// GetRootCmd returns the root command (for testing).
func GetRootCmd() *cobra.Command {
	return rootCmd
}

// GetOutputFormat returns the global output format.
func GetOutputFormat() string {
	return outputFormat
}

// IsVerbose returns whether verbose mode is enabled.
func IsVerbose() bool {
	return verbose
}

func init() {
	// Global flags
	rootCmd.PersistentFlags().StringVarP(&outputFormat, "output", "o", "text",
		"Output format: text, json, yaml")
	rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false,
		"Enable verbose output")

	// Add subcommands
	rootCmd.AddCommand(NewVersionCmd())
}

// AddCommand adds a command to the root command.
func AddCommand(cmd *cobra.Command) {
	rootCmd.AddCommand(cmd)
}
