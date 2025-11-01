#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Unified docs build script that ensures the non-normative JSON artifact is
    regenerated (if stale) before invoking MkDocs. Uses PowerShell + npm.

.DESCRIPTION
    This script checks if the schema JSON needs to be regenerated based on file
    modification times, regenerates it if needed, ensures it's available in the
    docs directory, and then builds the MkDocs site.

.PARAMETER Arguments
    Additional arguments to pass to mkdocs build command

.EXAMPLE
    .\build_docs.ps1
    .\build_docs.ps1 --clean
#>

param(
    [Parameter(ValueFromRemainingArguments)]
    [string[]]$Arguments
)

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Get the root directory (parent of scripts directory)
$ROOT_DIR = Split-Path -Parent $PSScriptRoot

$SCHEMA_JSON = Join-Path $ROOT_DIR "specification\json\a2a.json"
$SCHEMA_JSON_SITE_DIR = Join-Path $ROOT_DIR "docs\spec-json"
$SCHEMA_JSON_SITE_FILE = Join-Path $SCHEMA_JSON_SITE_DIR "a2a.json"
$PROTO_SRC = Join-Path $ROOT_DIR "specification\grpc\a2a.proto"
$TS_SRC = Join-Path $ROOT_DIR "types\src\types.ts"
$OPENAPI_TMP = [System.IO.Path]::GetTempFileName()
$OPENAPI_FILE_V2 = $OPENAPI_TMP
$EXTRACT_SCRIPT = Join-Path $ROOT_DIR "scripts\extract_json_schema.ps1"

# Cleanup function for temporary files
function Cleanup {
    if (Test-Path $OPENAPI_TMP) {
        Remove-Item $OPENAPI_TMP -Force -ErrorAction SilentlyContinue
    }
}

# Register cleanup for script exit
try {
    # Function to check if regeneration is needed
    function Test-RegenerationNeeded {
        if (-not (Test-Path $SCHEMA_JSON)) {
            return $true
        }

        $protoMtime = (Get-Item $PROTO_SRC).LastWriteTime
        $schemaMtime = (Get-Item $SCHEMA_JSON).LastWriteTime

        return $protoMtime -gt $schemaMtime
    }

    Write-Host "[build_docs] Checking schema freshness..." -ForegroundColor Cyan

    if (Test-RegenerationNeeded) {
        Write-Host "[build_docs] Regenerating a2a.json from proto (OpenAPI -> definitions)" -ForegroundColor Yellow

        $generateOpenApiScript = Join-Path $ROOT_DIR "scripts\generate_openapi.ps1"

        if (Test-Path $generateOpenApiScript) {
            try {
                # Set environment variable for OpenAPI output
                $env:OPENAPI_OUTPUT = $OPENAPI_FILE_V2

                # Run the generate_openapi.ps1 script
                & $generateOpenApiScript

                if ((Test-Path $OPENAPI_FILE_V2) -and ((Get-Item $OPENAPI_FILE_V2).Length -gt 0)) {
                    if (Test-Path $EXTRACT_SCRIPT) {
                        try {
                            & $EXTRACT_SCRIPT -InputFile $OPENAPI_FILE_V2 -OutputFile $SCHEMA_JSON
                        }
                        catch {
                            Write-Warning "[build_docs] Warning: schema extraction failed - $($_.Exception.Message)"
                        }
                    }
                    else {
                        Write-Warning "[build_docs] Extraction script not found: $EXTRACT_SCRIPT"
                    }
                }
                else {
                    Write-Warning "[build_docs] OpenAPI swagger not produced (expected at $OPENAPI_FILE_V2)"
                }
            }
            catch {
                Write-Warning "[build_docs] Warning: OpenAPI generation failed - $($_.Exception.Message)"
            }
        }
        else {
            Write-Warning "[build_docs] generate_openapi.ps1 missing; skipping proto-derived schema generation."
        }
    }
    else {
        Write-Host "[build_docs] Schema is up-to-date, skipping regeneration" -ForegroundColor Green
    }

    # Always ensure schema is available in docs directory for MkDocs
    if (Test-Path $SCHEMA_JSON) {
        # Create directory if it doesn't exist
        if (-not (Test-Path $SCHEMA_JSON_SITE_DIR)) {
            New-Item -ItemType Directory -Path $SCHEMA_JSON_SITE_DIR -Force | Out-Null
        }

        Copy-Item $SCHEMA_JSON $SCHEMA_JSON_SITE_FILE -Force
        Write-Host "[build_docs] Published schema to $SCHEMA_JSON_SITE_FILE" -ForegroundColor Green
    }
    else {
        Write-Warning "[build_docs] Warning: Schema file not found at $SCHEMA_JSON - MkDocs may fail"
    }

    Write-Host "" # Empty line for readability
    Write-Host "[build_docs] Building MkDocs site..." -ForegroundColor Cyan

    # Run mkdocs build with any additional arguments
    if ($Arguments) {
        & mkdocs build @Arguments
    }
    else {
        & mkdocs build
    }

    Write-Host "[build_docs] Done." -ForegroundColor Green
}
finally {
    # Always cleanup temporary files
    Cleanup
}
