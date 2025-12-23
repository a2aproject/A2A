package cmd

// Exit codes for the CLI.
const (
	ExitSuccess             = 0
	ExitGeneralError        = 1
	ExitInvalidArguments    = 2
	ExitFileNotFound        = 3
	ExitValidationFailed    = 4
	ExitNetworkError        = 5
	ExitAuthenticationError = 6
)

// ExitCodeMessage returns a human-readable message for an exit code.
func ExitCodeMessage(code int) string {
	switch code {
	case ExitSuccess:
		return "Success"
	case ExitGeneralError:
		return "General error"
	case ExitInvalidArguments:
		return "Invalid arguments"
	case ExitFileNotFound:
		return "File not found"
	case ExitValidationFailed:
		return "Validation failed"
	case ExitNetworkError:
		return "Network error"
	case ExitAuthenticationError:
		return "Authentication error"
	default:
		return "Unknown error"
	}
}
