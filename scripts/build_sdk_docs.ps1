#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Build Python SDK documentation using Sphinx.

.DESCRIPTION
    This script sets up a virtual environment, installs the A2A SDK package and
    documentation dependencies, generates API documentation source files using
    sphinx-apidoc, and builds HTML documentation using Sphinx.

.EXAMPLE
    .\build_sdk_docs.ps1
#>

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Configuration
$PACKAGE_NAME = "a2a"          # The name of the package to import
$PYPI_PACKAGE_NAME = "a2a-sdk" # The name on PyPI
$DOCS_SOURCE_DIR = "docs\sdk\python"
$DOCS_BUILD_DIR = Join-Path $DOCS_SOURCE_DIR "_build"
$VENV_DIR = ".doc-venv"

Write-Host "--- Setting up documentation build environment ---" -ForegroundColor Cyan

try {
    # Create a clean virtual environment
    if (Test-Path $VENV_DIR) {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item $VENV_DIR -Recurse -Force
    }

    Write-Host "Creating virtual environment..." -ForegroundColor Green
    & python -m venv $VENV_DIR
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
    }

    # Activate virtual environment
    $activateScript = if ($IsWindows -or $env:OS -eq "Windows_NT") {
        Join-Path $VENV_DIR "Scripts\Activate.ps1"
    }
    else {
        Join-Path $VENV_DIR "bin\Activate.ps1"
    }

    if (Test-Path $activateScript) {
        Write-Host "Activating virtual environment..." -ForegroundColor Green
        & $activateScript
    }
    else {
        # Fallback for older PowerShell versions or different venv structures
        $env:VIRTUAL_ENV = Resolve-Path $VENV_DIR
        $env:PATH = "$(Join-Path $VENV_DIR 'Scripts');$env:PATH"
    }

    Write-Host "--- Installing package and dependencies ---" -ForegroundColor Cyan

    # Upgrade pip and install documentation requirements
    Write-Host "Upgrading pip..." -ForegroundColor Green
    & python -m pip install -U pip
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to upgrade pip"
    }

    Write-Host "Installing documentation requirements..." -ForegroundColor Green
    & pip install -r "requirements-docs.txt"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install documentation requirements"
    }

    # Install the package itself
    Write-Host "Installing $PYPI_PACKAGE_NAME..." -ForegroundColor Green
    & pip install $PYPI_PACKAGE_NAME
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install $PYPI_PACKAGE_NAME"
    }

    Write-Host "--- Finding installed package path ---" -ForegroundColor Cyan

    # Find the installation path of the package
    $pythonCode = "import $PACKAGE_NAME, os; print(os.path.dirname($PACKAGE_NAME.__file__))"
    $packagePath = & python -c $pythonCode
    if ($LASTEXITCODE -ne 0 -or -not $packagePath) {
        Write-Error "Failed to find package path for '$PACKAGE_NAME'"
    }

    Write-Host "Found '$PACKAGE_NAME' at: $packagePath" -ForegroundColor Green

    Write-Host "--- Generating API documentation source files (.rst) ---" -ForegroundColor Cyan

    # Ensure docs source directory exists
    if (-not (Test-Path $DOCS_SOURCE_DIR)) {
        New-Item -ItemType Directory -Path $DOCS_SOURCE_DIR -Force | Out-Null
    }

    # Run sphinx-apidoc on the installed package directory
    # -f: force overwrite of existing files
    # -e: put each module on its own page
    & sphinx-apidoc -f -e -o $DOCS_SOURCE_DIR $packagePath
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to generate API documentation source files"
    }

    Write-Host "--- Building HTML documentation ---" -ForegroundColor Cyan

    # Build the HTML documentation
    & sphinx-build -b html $DOCS_SOURCE_DIR (Join-Path $DOCS_BUILD_DIR "html")
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to build HTML documentation"
    }

    Write-Host "" # Empty line for readability
    Write-Host "✅ SDK documentation built successfully!" -ForegroundColor Green
    Write-Host "Documentation available at: $(Join-Path $DOCS_BUILD_DIR 'html')" -ForegroundColor Yellow
}
catch {
    Write-Error "Failed to build SDK documentation: $($_.Exception.Message)"
}
finally {
    # Note: We don't deactivate the virtual environment in PowerShell the same way as bash
    # The environment variables will be cleaned up when the PowerShell session ends
    Write-Host "Build process completed." -ForegroundColor Cyan
}
