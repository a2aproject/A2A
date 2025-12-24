package output

import (
	"fmt"
	"io"
	"strings"

	"github.com/a2aproject/a2a/cli/internal/agentcard"
)

// ViewOptions configures what to display.
type ViewOptions struct {
	ShowSkills       bool
	ShowCapabilities bool
	ShowSecurity     bool
}

// WriteAgentCardOverview writes a complete overview of an agent card.
func WriteAgentCardOverview(w io.Writer, card *agentcard.AgentCard) {
	// Basic info
	fmt.Fprintf(w, "Agent: %s\n", card.Name)
	fmt.Fprintf(w, "Version: %s\n", card.Version)
	fmt.Fprintf(w, "Description: %s\n", card.Description)
	fmt.Fprintln(w)

	// Provider
	if card.Provider != nil {
		fmt.Fprintf(w, "Provider: %s (%s)\n", card.Provider.Organization, card.Provider.URL)
	}
	if card.DocumentationURL != "" {
		fmt.Fprintf(w, "Documentation: %s\n", card.DocumentationURL)
	}
	if card.Provider != nil || card.DocumentationURL != "" {
		fmt.Fprintln(w)
	}

	// Capabilities
	WriteCapabilities(w, &card.Capabilities)

	// Input/Output modes
	fmt.Fprintf(w, "Input Modes:  %s\n", strings.Join(card.DefaultInputModes, ", "))
	fmt.Fprintf(w, "Output Modes: %s\n", strings.Join(card.DefaultOutputModes, ", "))
	fmt.Fprintln(w)

	// Skills summary
	WriteSkillsSummary(w, card.Skills)
}

// WriteCapabilities writes capabilities with checkmarks.
func WriteCapabilities(w io.Writer, caps *agentcard.AgentCapabilities) {
	fmt.Fprintln(w, "Capabilities:")
	PrintCheckmark(w, "Streaming", caps.Streaming, 25)
	PrintCheckmark(w, "Push Notifications", caps.PushNotifications, 25)
	PrintCheckmark(w, "State Transition History", caps.StateTransitionHistory, 25)

	if len(caps.Extensions) > 0 {
		fmt.Fprintf(w, "  Extensions: %d\n", len(caps.Extensions))
		for _, ext := range caps.Extensions {
			req := ""
			if ext.Required {
				req = " (required)"
			}
			fmt.Fprintf(w, "    - %s%s\n", ext.URI, req)
		}
	}
	fmt.Fprintln(w)
}

// WriteSkillsSummary writes a brief list of skills.
func WriteSkillsSummary(w io.Writer, skills []agentcard.AgentSkill) {
	fmt.Fprintf(w, "Skills (%d):\n", len(skills))
	for _, skill := range skills {
		fmt.Fprintf(w, "  \u2022 %-12s - %s\n", skill.ID, skill.Description)
	}
}

// WriteSkillsTable writes a detailed table of skills.
func WriteSkillsTable(w io.Writer, skills []agentcard.AgentSkill) {
	fmt.Fprintln(w, "Skills:")
	fmt.Fprintln(w)

	var data [][]string
	for _, skill := range skills {
		data = append(data, []string{
			skill.ID,
			skill.Name,
			truncateString(skill.Description, 40),
		})
	}

	RenderSkillsTable(w, data)
}

// WriteSkillsDetailed writes detailed skill information.
func WriteSkillsDetailed(w io.Writer, skills []agentcard.AgentSkill) {
	for i, skill := range skills {
		if i > 0 {
			fmt.Fprintln(w)
			fmt.Fprintln(w, "---")
			fmt.Fprintln(w)
		}

		fmt.Fprintf(w, "Skill: %s\n", skill.Name)
		fmt.Fprintf(w, "ID: %s\n", skill.ID)
		fmt.Fprintf(w, "Description: %s\n", skill.Description)

		if len(skill.Tags) > 0 {
			fmt.Fprintf(w, "Tags: %s\n", strings.Join(skill.Tags, ", "))
		}

		if len(skill.InputModes) > 0 {
			fmt.Fprintf(w, "Input Modes: %s\n", strings.Join(skill.InputModes, ", "))
		}

		if len(skill.OutputModes) > 0 {
			fmt.Fprintf(w, "Output Modes: %s\n", strings.Join(skill.OutputModes, ", "))
		}

		if len(skill.Examples) > 0 {
			fmt.Fprintln(w, "Examples:")
			for _, ex := range skill.Examples {
				fmt.Fprintf(w, "  - %s\n", ex)
			}
		}
	}
}

// WriteSecurityConfig writes security configuration.
func WriteSecurityConfig(w io.Writer, card *agentcard.AgentCard) {
	fmt.Fprintln(w, "Security Configuration:")
	fmt.Fprintln(w)

	if len(card.SecuritySchemes) == 0 {
		fmt.Fprintln(w, "  No security schemes defined")
		return
	}

	fmt.Fprintln(w, "Security Schemes:")
	for name, scheme := range card.SecuritySchemes {
		fmt.Fprintf(w, "  %s:\n", name)
		if scheme.APIKey != nil {
			fmt.Fprintf(w, "    Type: API Key\n")
			fmt.Fprintf(w, "    Location: %s\n", scheme.APIKey.Location)
			fmt.Fprintf(w, "    Name: %s\n", scheme.APIKey.Name)
		} else if scheme.HTTP != nil {
			fmt.Fprintf(w, "    Type: HTTP\n")
			fmt.Fprintf(w, "    Scheme: %s\n", scheme.HTTP.Scheme)
			if scheme.HTTP.BearerFormat != "" {
				fmt.Fprintf(w, "    Bearer Format: %s\n", scheme.HTTP.BearerFormat)
			}
		} else if scheme.OAuth2 != nil {
			fmt.Fprintf(w, "    Type: OAuth2\n")
			if scheme.OAuth2.OAuth2MetadataURL != "" {
				fmt.Fprintf(w, "    Metadata URL: %s\n", scheme.OAuth2.OAuth2MetadataURL)
			}
		} else if scheme.OpenIDConnect != nil {
			fmt.Fprintf(w, "    Type: OpenID Connect\n")
			fmt.Fprintf(w, "    Discovery URL: %s\n", scheme.OpenIDConnect.OpenIDConnectURL)
		} else if scheme.MutualTLS != nil {
			fmt.Fprintf(w, "    Type: Mutual TLS\n")
		}
	}

	if len(card.Security) > 0 {
		fmt.Fprintln(w)
		fmt.Fprintln(w, "Security Requirements:")
		for i, req := range card.Security {
			fmt.Fprintf(w, "  Option %d:\n", i+1)
			for scheme, scopes := range req.Schemes {
				if len(scopes) > 0 {
					fmt.Fprintf(w, "    %s: %s\n", scheme, strings.Join(scopes, ", "))
				} else {
					fmt.Fprintf(w, "    %s\n", scheme)
				}
			}
		}
	}
}

func truncateString(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen-3] + "..."
}
