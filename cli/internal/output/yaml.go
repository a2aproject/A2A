package output

import (
	"io"

	"gopkg.in/yaml.v3"
)

// MarshalYAML marshals data to YAML.
func MarshalYAML(data interface{}) ([]byte, error) {
	return yaml.Marshal(data)
}

// WriteYAMLTo writes YAML-formatted data to a writer.
func WriteYAMLTo(w io.Writer, data interface{}) error {
	bytes, err := MarshalYAML(data)
	if err != nil {
		return err
	}
	_, err = w.Write(bytes)
	return err
}
