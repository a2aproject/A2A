#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Generate OpenAPI (Swagger v2) using protoc + protoc-gen-openapiv2.

.DESCRIPTION
    This script generates OpenAPI documentation from Protocol Buffer definitions
    using protoc and protoc-gen-openapiv2. The output is a temporary swagger.json
    file used primarily for JSON Schema extraction.

.PARAMETER GoogleApisDir
    Optional path to the googleapis directory containing google/api/*.proto files.
    If not specified, the script will try common locations.

.PARAMETER OutputTempDir
    Optional temporary directory for output. If not specified, a temporary directory will be created.

.EXAMPLE
    .\generate_openapi.ps1
    .\generate_openapi.ps1 -GoogleApisDir "C:\path\to\googleapis"

.NOTES
    Requirements: protoc and protoc-gen-openapiv2 must be available in PATH.
    Uses the OPENAPI_OUTPUT environment variable if set to copy the generated swagger file.
#>

param(
    [string]$GoogleApisDir = $env:GOOGLEAPIS_DIR,
    [string]$OutputTempDir = $env:OPENAPI_TMP_DIR
)

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Get the root directory (parent of scripts directory)
$ROOT_DIR = Split-Path -Parent $PSScriptRoot
$PROTO_DIR = Join-Path $ROOT_DIR "specification\grpc"
$PROTO_FILE = Join-Path $PROTO_DIR "a2a.proto"

# Set up output directory
if (-not $OutputTempDir) {
    $OutputTempDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
    New-Item -ItemType Directory -Path $OutputTempDir -Force | Out-Null
    $cleanupTempDir = $true
}
else {
    $cleanupTempDir = $false
}

try {
    # Check for required tools
    $protocAvailable = Get-Command "protoc" -ErrorAction SilentlyContinue
    if (-not $protocAvailable) {
        Write-Error "[generate_openapi] protoc not found on PATH"
    }

    $protocGenAvailable = Get-Command "protoc-gen-openapiv2" -ErrorAction SilentlyContinue
    if (-not $protocGenAvailable) {
        Write-Error "[generate_openapi] protoc-gen-openapiv2 not found on PATH"
    }

    # Ensure output directory exists
    if (-not (Test-Path $OutputTempDir)) {
        New-Item -ItemType Directory -Path $OutputTempDir -Force | Out-Null
    }

    # Build include flags for protoc
    $includeFlags = @("-I$PROTO_DIR")

    # Find standard protobuf includes (google/protobuf/*.proto)
    $protobufIncludePaths = @()

    # Check if protoc is from WinGet installation
    $protocPath = (Get-Command "protoc" -ErrorAction SilentlyContinue).Source
    if ($protocPath -and $protocPath -like "*WinGet*") {
        # WinGet uses Links directory with symlinks, need to find the actual package
        $wingetBaseDir = Split-Path (Split-Path $protocPath)
        $packagesDir = Join-Path $wingetBaseDir "Packages"

        if (Test-Path $packagesDir) {
            $protobufPackages = Get-ChildItem $packagesDir -Directory | Where-Object { $_.Name -like "*Protobuf*" }

            foreach ($package in $protobufPackages) {
                $includeDir = Join-Path $package.FullName "include"
                $descriptorPath = Join-Path $includeDir "google\protobuf\descriptor.proto"
                if (Test-Path $descriptorPath) {
                    $protobufIncludePaths += $includeDir
                    break
                }
            }
        }
    }    # Common locations for protobuf includes
    $protobufIncludePaths += @(
        "C:\Program Files\protobuf\include",
        "C:\usr\local\include",
        "/usr/local/include",
        "/usr/include"
    )

    # Add the first valid protobuf include path
    foreach ($path in $protobufIncludePaths) {
        if (Test-Path (Join-Path $path "google\protobuf\descriptor.proto")) {
            $includeFlags += "-I$path"
            break
        }
    }

    # Priority order for googleapis protos providing google/api/*.proto
    $googleApisPaths = @()
    if ($GoogleApisDir) {
        $googleApisPaths += $GoogleApisDir
    }
    $googleApisPaths += Join-Path $ROOT_DIR "third_party\googleapis"
    $googleApisPaths += "C:\usr\local\include"  # Common Windows location might be different

    $annotationsFound = $false
    foreach ($path in $googleApisPaths) {
        if (Test-Path (Join-Path $path "google\api\annotations.proto")) {
            $includeFlags += "-I$path"
            $annotationsFound = $true
            break
        }
    }

    if (-not $annotationsFound) {
        Write-Error @"
[generate_openapi] google/api/annotations.proto not found in include paths ($($includeFlags -join ', ')).
[generate_openapi] Set GOOGLEAPIS_DIR env var to your cloned googleapis repo, e.g.:
  `$env:GOOGLEAPIS_DIR = "C:\path\to\googleapis"
  git clone https://github.com/googleapis/googleapis.git C:\path\to\googleapis
"@
    }

    # Generate swagger json
    Write-Host "[generate_openapi] Running protoc to emit swagger..." -ForegroundColor Cyan

    $protocArgs = $includeFlags + @(
        "--openapiv2_out=$OutputTempDir",
        "--openapiv2_opt=logtostderr=true",
        $PROTO_FILE
    )

    & protoc @protocArgs

    if ($LASTEXITCODE -ne 0) {
        Write-Error "[generate_openapi] protoc command failed with exit code $LASTEXITCODE"
    }

    # Find the generated swagger file
    $swaggerFiles = Get-ChildItem -Path $OutputTempDir -Filter "*.swagger.json" -ErrorAction SilentlyContinue
    if (-not $swaggerFiles -or @($swaggerFiles).Count -eq 0) {
        Write-Error "[generate_openapi] No .swagger.json produced"
    }

    $swaggerJson = $swaggerFiles[0].FullName
    Write-Host "[generate_openapi] Generated OpenAPI (ephemeral): $swaggerJson" -ForegroundColor Green

    # If caller exported OPENAPI_OUTPUT, copy swagger there (used by build_docs for extraction)
    if ($env:OPENAPI_OUTPUT) {
        Copy-Item $swaggerJson $env:OPENAPI_OUTPUT -Force
        Write-Host "[generate_openapi] Copied swagger to $($env:OPENAPI_OUTPUT)" -ForegroundColor Green
    }
}
catch {
    Write-Error "Failed to generate OpenAPI: $($_.Exception.Message)"
}
finally {
    # Cleanup temporary directory if we created it
    if ($cleanupTempDir -and (Test-Path $OutputTempDir)) {
        Remove-Item $OutputTempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
