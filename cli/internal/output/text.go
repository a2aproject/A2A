package output

import (
	"fmt"
	"io"
	"strings"
)

// PrintSuccess prints a success message with a checkmark.
func PrintSuccess(w io.Writer, message string) {
	fmt.Fprintf(w, "\u2713 %s\n", message)
}

// PrintError prints an error message with an X.
func PrintError(w io.Writer, message string) {
	fmt.Fprintf(w, "\u2717 %s\n", message)
}

// PrintWarning prints a warning message.
func PrintWarning(w io.Writer, message string) {
	fmt.Fprintf(w, "\u26a0 %s\n", message)
}

// PrintInfo prints an informational message.
func PrintInfo(w io.Writer, message string) {
	fmt.Fprintf(w, "\u2139 %s\n", message)
}

// PrintBullet prints a bullet point item.
func PrintBullet(w io.Writer, message string) {
	fmt.Fprintf(w, "  \u2022 %s\n", message)
}

// PrintKeyValue prints a key-value pair with alignment.
func PrintKeyValue(w io.Writer, key, value string, keyWidth int) {
	format := fmt.Sprintf("%%-%ds %%s\n", keyWidth)
	fmt.Fprintf(w, format, key+":", value)
}

// PrintHeader prints a section header.
func PrintHeader(w io.Writer, title string) {
	fmt.Fprintf(w, "\n%s\n", title)
	fmt.Fprintln(w, strings.Repeat("-", len(title)))
}

// PrintSection prints a section with a title and content.
func PrintSection(w io.Writer, title string, content func(io.Writer)) {
	PrintHeader(w, title)
	content(w)
	fmt.Fprintln(w)
}

// PrintCheckmark prints a checkmark or X based on the condition.
func PrintCheckmark(w io.Writer, label string, enabled bool, labelWidth int) {
	mark := "\u2717" // X
	if enabled {
		mark = "\u2713" // checkmark
	}
	format := fmt.Sprintf("  %%s %%-%ds\n", labelWidth)
	fmt.Fprintf(w, format, mark, label)
}

// Pluralize returns the plural form if count != 1.
func Pluralize(count int, singular, plural string) string {
	if count == 1 {
		return singular
	}
	return plural
}

// FormatCount formats a count with proper pluralization.
func FormatCount(count int, singular, plural string) string {
	return fmt.Sprintf("%d %s", count, Pluralize(count, singular, plural))
}
