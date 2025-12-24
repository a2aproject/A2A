# A2A CLI Makefile

# Variables
BINARY_NAME := a2a
VERSION := 1.0.0
BUILD_DIR := ./build
MAIN_PACKAGE := ./cmd/a2a
GIT_COMMIT := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_TIME := $(shell date -u '+%Y-%m-%dT%H:%M:%SZ')
LDFLAGS := -ldflags "-X github.com/a2aproject/a2a/cli/internal/cmd.version=$(VERSION) \
	-X github.com/a2aproject/a2a/cli/internal/cmd.buildTime=$(BUILD_TIME) \
	-X github.com/a2aproject/a2a/cli/internal/cmd.gitCommit=$(GIT_COMMIT)"

# Go commands
GOCMD := go
GOBUILD := $(GOCMD) build
GOTEST := $(GOCMD) test
GOFMT := $(GOCMD) fmt
GOVET := $(GOCMD) vet
GOMOD := $(GOCMD) mod

# Default target
.PHONY: all
all: build

# Sync schema to validator package (go:embed cannot use .. paths)
.PHONY: sync-schema
sync-schema:
	cp schemas/agentcard.json internal/validator/schema_data.json

# Build the binary
.PHONY: build
build: sync-schema
	$(GOBUILD) $(LDFLAGS) -o $(BINARY_NAME) $(MAIN_PACKAGE)

# Install to GOPATH/bin
.PHONY: install
install:
	$(GOCMD) install $(LDFLAGS) $(MAIN_PACKAGE)

# Run tests
.PHONY: test
test:
	$(GOTEST) -v -race -cover ./...

# Run tests with coverage report
.PHONY: coverage
coverage:
	$(GOTEST) -v -race -coverprofile=coverage.out ./...
	$(GOCMD) tool cover -html=coverage.out -o coverage.html

# Format code
.PHONY: fmt
fmt:
	$(GOFMT) ./...

# Run linter (requires golangci-lint)
.PHONY: lint
lint:
	golangci-lint run ./...

# Vet code
.PHONY: vet
vet:
	$(GOVET) ./...

# Clean build artifacts
.PHONY: clean
clean:
	rm -f $(BINARY_NAME) coverage.out coverage.html
	rm -rf $(BUILD_DIR)

# Download dependencies
.PHONY: deps
deps:
	$(GOMOD) download
	$(GOMOD) tidy

# Verify dependencies
.PHONY: verify
verify:
	$(GOMOD) verify

# Cross-compilation targets
.PHONY: build-all
build-all: build-linux build-darwin build-windows

.PHONY: build-linux
build-linux:
	mkdir -p $(BUILD_DIR)
	GOOS=linux GOARCH=amd64 $(GOBUILD) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-linux-amd64 $(MAIN_PACKAGE)
	GOOS=linux GOARCH=arm64 $(GOBUILD) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-linux-arm64 $(MAIN_PACKAGE)

.PHONY: build-darwin
build-darwin:
	mkdir -p $(BUILD_DIR)
	GOOS=darwin GOARCH=amd64 $(GOBUILD) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-amd64 $(MAIN_PACKAGE)
	GOOS=darwin GOARCH=arm64 $(GOBUILD) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-darwin-arm64 $(MAIN_PACKAGE)

.PHONY: build-windows
build-windows:
	mkdir -p $(BUILD_DIR)
	GOOS=windows GOARCH=amd64 $(GOBUILD) $(LDFLAGS) -o $(BUILD_DIR)/$(BINARY_NAME)-windows-amd64.exe $(MAIN_PACKAGE)

# Generate shell completions
.PHONY: completions
completions: build
	mkdir -p $(BUILD_DIR)/completions
	./$(BINARY_NAME) completion bash > $(BUILD_DIR)/completions/$(BINARY_NAME).bash
	./$(BINARY_NAME) completion zsh > $(BUILD_DIR)/completions/_$(BINARY_NAME)
	./$(BINARY_NAME) completion fish > $(BUILD_DIR)/completions/$(BINARY_NAME).fish
	./$(BINARY_NAME) completion powershell > $(BUILD_DIR)/completions/$(BINARY_NAME).ps1

# Help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build       - Build the binary"
	@echo "  install     - Install to GOPATH/bin"
	@echo "  test        - Run tests"
	@echo "  coverage    - Run tests with coverage report"
	@echo "  fmt         - Format code"
	@echo "  lint        - Run linter"
	@echo "  vet         - Vet code"
	@echo "  clean       - Clean build artifacts"
	@echo "  deps        - Download dependencies"
	@echo "  verify      - Verify dependencies"
	@echo "  sync-schema - Sync schema to validator package"
	@echo "  build-all   - Cross-compile for all platforms"
	@echo "  completions - Generate shell completions"
	@echo "  help        - Show this help"
