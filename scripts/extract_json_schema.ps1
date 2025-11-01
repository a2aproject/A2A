#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Extract pure JSON Schema components from an OpenAPI (v2 or v3) document.

.DESCRIPTION
    This script extracts JSON Schema components from OpenAPI documents and creates
    a JSON Schema bundle with top-level $schema and $id hints. It supports both
    OpenAPI v2 (definitions) and v3 (components.schemas) formats.

.PARAMETER InputFile
    The input OpenAPI file (JSON or YAML format)

.PARAMETER OutputFile
    The output JSON Schema file

.EXAMPLE
    .\extract_json_schema.ps1 -InputFile "openapi.json" -OutputFile "schema.json"
    .\extract_json_schema.ps1 -InputFile "openapi.yaml" -OutputFile "schema.json"

.NOTES
    Requires jq to be installed and available in PATH.
    For YAML files, requires yq to be installed and available in PATH.
#>

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$InputFile,

    [Parameter(Mandatory = $true, Position = 1)]
    [string]$OutputFile
)

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Validate input parameters
if (-not $InputFile -or -not $OutputFile) {
    Write-Error "Usage: extract_json_schema.ps1 <openapi.(json|yaml)> <output.json>"
}

if (-not (Test-Path $InputFile)) {
    Write-Error "Input file not found: $InputFile"
}

# Check for required tools
$jqAvailable = Get-Command "jq" -ErrorAction SilentlyContinue
if (-not $jqAvailable) {
    Write-Error "jq is required to extract schemas."
}

# Determine file type and convert to JSON if needed
$extension = [System.IO.Path]::GetExtension($InputFile).ToLower()
$tempJson = [System.IO.Path]::GetTempFileName()

try {
    if ($extension -eq ".yaml" -or $extension -eq ".yml") {
        $yqAvailable = Get-Command "yq" -ErrorAction SilentlyContinue
        if (-not $yqAvailable) {
            Write-Error "yq is required to process YAML OpenAPI documents."
        }

        # Convert YAML to JSON using yq
        & yq -o=json '.' $InputFile | Out-File $tempJson -Encoding UTF8
    }
    else {
        # Copy JSON file directly
        Copy-Item $InputFile $tempJson
    }

    # Extract schema content using jq
    # Try v3 (components.schemas) then fallback to v2 (definitions)
    $jqQuery = 'if .components and .components.schemas then .components.schemas elif .definitions then .definitions else {} end'
    $schemaContentJson = & jq $jqQuery $tempJson

    if (-not $schemaContentJson -or $schemaContentJson -eq "null" -or $schemaContentJson -eq "{}") {
        Write-Warning "[extract_json_schema] Warning: No schemas found in OpenAPI document."
        $schemaContentJson = "{}"
    }

    # Construct final JSON Schema bundle
    $finalSchemaQuery = @'
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "A2A Protocol Schemas",
  "description": "Non-normative JSON Schema bundle extracted from generated OpenAPI document (proto-derived).",
  "version": "v1",
  "definitions": $defs
}
'@

    # Use temporary files to avoid command line length limits
    $tempSchemaFile = [System.IO.Path]::GetTempFileName()
    $tempQueryFile = [System.IO.Path]::GetTempFileName()

    try {
        # Write schema content to temp file
        $schemaContentJson | Out-File $tempSchemaFile -Encoding UTF8

        # Write query to temp file
        $finalSchemaQuery | Out-File $tempQueryFile -Encoding UTF8

        # Use jq with file inputs instead of command line args
        & jq --slurpfile defs $tempSchemaFile -f $tempQueryFile -n | & jq . | Out-File $OutputFile -Encoding UTF8
    }
    finally {
        # Clean up temp files
        if (Test-Path $tempSchemaFile) { Remove-Item $tempSchemaFile -Force -ErrorAction SilentlyContinue }
        if (Test-Path $tempQueryFile) { Remove-Item $tempQueryFile -Force -ErrorAction SilentlyContinue }
    }

    Write-Host "[extract_json_schema] Wrote schemas to $OutputFile" -ForegroundColor Green
}
catch {
    Write-Error "Failed to extract JSON schema: $($_.Exception.Message)"
}
finally {
    # Cleanup temporary file
    if (Test-Path $tempJson) {
        Remove-Item $tempJson -Force -ErrorAction SilentlyContinue
    }
}
