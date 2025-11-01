#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Concatenates all documentation and specification files into a single file for LLM consumption.

.DESCRIPTION
    This script consolidates all documentation (markdown and rst files), specification files,
    and type definitions into a single text file that can be easily consumed by LLMs.

.EXAMPLE
    .\build_llms_full.ps1
#>

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Configuration
$OUTPUT_FILE = "docs\llms-full.txt"
$DOCS_DIR = "docs"
$SPEC_DIR = "specification"
$TYPES_DIR = "types"

Write-Host "--- Generating consolidated LLM file: $OUTPUT_FILE ---" -ForegroundColor Cyan

# Clear the output file to start fresh
if (Test-Path $OUTPUT_FILE) {
    Remove-Item $OUTPUT_FILE -Force
}
New-Item $OUTPUT_FILE -ItemType File -Force | Out-Null

# Helper function to append file content with a header
function Add-FileContent {
    param(
        [string]$FilePath
    )

    if (Test-Path $FilePath) {
        Write-Host "Appending: $FilePath" -ForegroundColor Yellow

        # Create header and content block
        $header = "--- START OF FILE $FilePath ---"
        $separator = "=" * 49

        # Append to output file
        Add-Content -Path $OUTPUT_FILE -Value $header -Encoding UTF8
        Add-Content -Path $OUTPUT_FILE -Value "" -Encoding UTF8
        Get-Content -Path $FilePath -Encoding UTF8 | Add-Content -Path $OUTPUT_FILE -Encoding UTF8
        Add-Content -Path $OUTPUT_FILE -Value "" -Encoding UTF8
        Add-Content -Path $OUTPUT_FILE -Value $separator -Encoding UTF8
        Add-Content -Path $OUTPUT_FILE -Value "" -Encoding UTF8
    }
    else {
        Write-Warning "File not found, skipping: $FilePath"
    }
}

try {
    # Process Documentation Files
    # Find all markdown and rst files in the docs directory, sort them for consistent output
    Write-Host "Processing documentation files..." -ForegroundColor Green

    $docFiles = Get-ChildItem -Path $DOCS_DIR -Recurse -Include "*.md", "*.rst" -File |
    Sort-Object FullName

    foreach ($docFile in $docFiles) {
        Add-FileContent -FilePath $docFile.FullName
    }

    # Process Specification Files
    Write-Host "Processing specification files..." -ForegroundColor Green

    $specFiles = @(
        (Join-Path $SPEC_DIR "grpc\a2a.proto"),
        (Join-Path $SPEC_DIR "json\a2a.json"),
        (Join-Path $TYPES_DIR "src\types.ts")
    )

    foreach ($specFile in $specFiles) {
        Add-FileContent -FilePath $specFile
    }

    Write-Host "✅ Consolidated LLM file generated successfully at $OUTPUT_FILE" -ForegroundColor Green
}
catch {
    Write-Error "Failed to generate consolidated LLM file: $($_.Exception.Message)"
}
