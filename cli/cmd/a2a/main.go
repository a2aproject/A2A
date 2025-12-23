// Package main is the entry point for the A2A CLI.
package main

import (
	"github.com/a2aproject/a2a/cli/internal/cmd"
)

// Build-time variables set via ldflags.
var (
	version   = "dev"
	buildTime = "unknown"
)

func main() {
	cmd.SetVersion(version, buildTime)
	cmd.Execute()
}
