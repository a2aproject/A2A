package cmd

import (
	"fmt"
	"runtime"

	"github.com/spf13/cobra"
)

// Version information (set via ldflags during build).
var (
	version   = "dev"
	buildTime = "unknown"
	gitCommit = "unknown"
)

// SetVersionInfo sets version information (for testing or programmatic use).
func SetVersionInfo(v, bt, gc string) {
	version = v
	buildTime = bt
	gitCommit = gc
}

// GetVersion returns the current version.
func GetVersion() string {
	return version
}

// NewVersionCmd creates the version command.
func NewVersionCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "version",
		Short: "Display version information",
		Long:  `Display version information including build time and runtime details.`,
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("a2a version %s\n", version)
			fmt.Printf("Protocol version: 1.0\n")
			fmt.Printf("Go version: %s\n", runtime.Version())
			fmt.Printf("OS/Arch: %s/%s\n", runtime.GOOS, runtime.GOARCH)
			fmt.Printf("Built: %s\n", buildTime)
			if gitCommit != "unknown" {
				fmt.Printf("Commit: %s\n", gitCommit)
			}
		},
	}
}
