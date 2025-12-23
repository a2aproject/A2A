package output

import (
	"encoding/json"
	"io"
)

// MarshalJSON marshals data to JSON with optional indentation.
func MarshalJSON(data interface{}, indent bool) ([]byte, error) {
	if indent {
		return json.MarshalIndent(data, "", "  ")
	}
	return json.Marshal(data)
}

// WriteJSONTo writes JSON-formatted data to a writer.
func WriteJSONTo(w io.Writer, data interface{}, indent bool) error {
	bytes, err := MarshalJSON(data, indent)
	if err != nil {
		return err
	}
	_, err = w.Write(bytes)
	if err != nil {
		return err
	}
	_, err = w.Write([]byte("\n"))
	return err
}
