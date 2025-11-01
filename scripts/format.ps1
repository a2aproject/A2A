#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Format markdown files using markdownlint.

.DESCRIPTION
    This script formats markdown files using markdownlint-cli. It first sorts
    the spelling allow list, then installs markdownlint-cli if needed, and
    finally runs markdownlint to format all markdown files in the docs directory.

.EXAMPLE
    .\format.ps1
#>

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Determine the repository root directory based on the script's location
$SCRIPT_DIR = $PSScriptRoot
$REPO_ROOT = Split-Path -Parent $SCRIPT_DIR

# Run the spelling sort script first
$sortSpellingScript = Join-Path $SCRIPT_DIR "sort_spelling.ps1"
if (Test-Path $sortSpellingScript) {
    Write-Host "Running sort_spelling.ps1..." -ForegroundColor Cyan
    & $sortSpellingScript
    if ($LASTEXITCODE -ne 0) {
        Write-Error "sort_spelling.ps1 failed with exit code $LASTEXITCODE"
    }
}
else {
    Write-Warning "sort_spelling.ps1 not found at: $sortSpellingScript"
}

# Define file and directory paths
$MARKDOWN_DIR = Join-Path $REPO_ROOT "docs"
$MARKDOWNLINT_CONFIG = Join-Path $REPO_ROOT ".github\linters\.markdownlint.json"

# Check for the existence of the directory and config file
if (-not (Test-Path $MARKDOWN_DIR)) {
    Write-Error "ERROR: Markdown directory not found: $MARKDOWN_DIR"
}

if (-not (Test-Path $MARKDOWNLINT_CONFIG)) {
    Write-Error "ERROR: Markdownlint config not found: $MARKDOWNLINT_CONFIG"
}

# Install markdownlint-cli if the command doesn't already exist
$markdownlintAvailable = Get-Command "markdownlint" -ErrorAction SilentlyContinue
if (-not $markdownlintAvailable) {
    Write-Host "Installing markdownlint-cli..." -ForegroundColor Yellow
    try {
        & npm install -g markdownlint-cli
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install markdownlint-cli"
        }
    }
    catch {
        Write-Error "Failed to install markdownlint-cli: $($_.Exception.Message)"
    }
}

# Run markdownlint to format files
Write-Host "Formatting markdown files..." -ForegroundColor Cyan

try {
    & markdownlint $MARKDOWN_DIR --config $MARKDOWNLINT_CONFIG --fix
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "markdownlint completed with warnings or errors (exit code: $LASTEXITCODE)"
    }
    else {
        Write-Host "✅ Script finished successfully." -ForegroundColor Green
    }
}
catch {
    Write-Error "Failed to run markdownlint: $($_.Exception.Message)"
}
