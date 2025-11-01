#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Sorts the spelling allow list file.

.DESCRIPTION
    This script sorts the spelling allow list file used by the spelling checker
    to ensure consistent ordering and removes duplicates.

.EXAMPLE
    .\sort_spelling.ps1
#>

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Determine the repository root directory based on the script's location
$SCRIPT_DIR = $PSScriptRoot
$REPO_ROOT = Split-Path -Parent $SCRIPT_DIR

$ALLOW_FILE = Join-Path $REPO_ROOT ".github\actions\spelling\allow.txt"

Write-Host "Sorting spelling allow list..." -ForegroundColor Cyan

if (-not (Test-Path $ALLOW_FILE)) {
    Write-Error "ERROR: Allow list not found: $ALLOW_FILE"
}

try {
    # Read the file, sort uniquely, and write back
    $content = Get-Content $ALLOW_FILE -ErrorAction Stop
    $sortedContent = $content | Sort-Object -Unique
    $sortedContent | Set-Content $ALLOW_FILE -Encoding UTF8

    Write-Host "✅ Spelling allow list sorted successfully" -ForegroundColor Green
}
catch {
    Write-Error "Failed to sort spelling allow list: $($_.Exception.Message)"
}
