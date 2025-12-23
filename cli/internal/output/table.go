package output

import (
	"io"

	"github.com/olekukonko/tablewriter"
)

// TableConfig configures table rendering.
type TableConfig struct {
	Headers    []string
	Alignment  []int
	Border     bool
	HeaderLine bool
	CenterSep  string
	ColumnSep  string
	RowSep     string
	AutoWrap   bool
	WrapWidth  int
}

// DefaultTableConfig returns default table configuration.
func DefaultTableConfig() TableConfig {
	return TableConfig{
		Border:     true,
		HeaderLine: true,
		AutoWrap:   true,
		WrapWidth:  40,
	}
}

// NewTable creates a new table writer with the given configuration.
func NewTable(w io.Writer, config TableConfig) *tablewriter.Table {
	table := tablewriter.NewWriter(w)

	if len(config.Headers) > 0 {
		table.SetHeader(config.Headers)
	}

	if len(config.Alignment) > 0 {
		table.SetColumnAlignment(config.Alignment)
	}

	table.SetBorder(config.Border)
	table.SetHeaderLine(config.HeaderLine)

	if config.CenterSep != "" {
		table.SetCenterSeparator(config.CenterSep)
	}
	if config.ColumnSep != "" {
		table.SetColumnSeparator(config.ColumnSep)
	}
	if config.RowSep != "" {
		table.SetRowSeparator(config.RowSep)
	}

	table.SetAutoWrapText(config.AutoWrap)
	if config.WrapWidth > 0 {
		table.SetColWidth(config.WrapWidth)
	}

	return table
}

// SimpleTable creates a simple table with default styling.
func SimpleTable(w io.Writer, headers []string) *tablewriter.Table {
	config := DefaultTableConfig()
	config.Headers = headers
	return NewTable(w, config)
}

// RenderTable renders a table with the given headers and data.
func RenderTable(w io.Writer, headers []string, data [][]string) {
	table := SimpleTable(w, headers)
	table.AppendBulk(data)
	table.Render()
}

// RenderSkillsTable renders a table specifically for skills.
func RenderSkillsTable(w io.Writer, data [][]string) {
	headers := []string{"ID", "Name", "Description"}
	config := DefaultTableConfig()
	config.Headers = headers
	config.Alignment = []int{
		tablewriter.ALIGN_LEFT,
		tablewriter.ALIGN_LEFT,
		tablewriter.ALIGN_LEFT,
	}

	table := NewTable(w, config)
	table.AppendBulk(data)
	table.Render()
}
