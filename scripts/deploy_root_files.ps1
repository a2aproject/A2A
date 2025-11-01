#!/usr/bin/env pwsh
#Requires -Version 5.1

<#
.SYNOPSIS
    Deploy specified files to the root of the gh-pages branch.

.DESCRIPTION
    This script deploys a list of specified files (e.g., 404.html, robots.txt)
    to the root of the gh-pages branch. It's designed to be called from a
    GitHub Actions workflow.

.PARAMETER RepositoryName
    The GitHub repository name in format "owner/repo" (e.g., "a2aproject/A2A")

.PARAMETER GitHubToken
    The GITHUB_TOKEN for authentication

.EXAMPLE
    .\deploy_root_files.ps1 -RepositoryName "a2aproject/A2A" -GitHubToken $env:GITHUB_TOKEN
#>

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$RepositoryName,

    [Parameter(Mandatory = $true, Position = 1)]
    [string]$GitHubToken
)

# Set strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Configuration
# List of files to copy from the source directory to the root of the gh-pages branch
$FILES_TO_DEPLOY = @("404.html", "robots.txt", "llms.txt", "llms-full.txt")
# The source directory in the main branch where these files are located
$SOURCE_DIR = "docs"

# Validate Input
if (-not $RepositoryName -or -not $GitHubToken) {
    Write-Error "Missing required arguments. Usage: deploy_root_files.ps1 <owner/repo> <github_token>"
}

Write-Host "Deploying root-level site files for repository: $RepositoryName" -ForegroundColor Cyan
Write-Host "Files to deploy: $($FILES_TO_DEPLOY -join ', ')" -ForegroundColor Yellow

$deployDir = "gh-pages-deploy"

try {
    # Clone the gh-pages branch using the provided token for authentication
    Write-Host "Cloning gh-pages branch..." -ForegroundColor Green
    $cloneUrl = "https://x-access-token:$GitHubToken@github.com/$RepositoryName.git"
    & git clone --branch=gh-pages --single-branch --depth=1 $cloneUrl $deployDir

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone gh-pages branch"
    }

    # Navigate into the cloned directory
    Push-Location $deployDir

    try {
        $filesChanged = $false

        # Loop through the files, copy them from the source checkout, and add them to git
        foreach ($file in $FILES_TO_DEPLOY) {
            $sourceFile = Join-Path ".." (Join-Path $SOURCE_DIR $file)

            if (Test-Path $sourceFile) {
                Write-Host "Copying $file..." -ForegroundColor Yellow
                Copy-Item $sourceFile ".\$file" -Force
                & git add $file

                if ($LASTEXITCODE -eq 0) {
                    $filesChanged = $true
                }
            }
            else {
                Write-Warning "Source file not found, skipping: $sourceFile"
            }
        }

        # Commit and push only if any of the files have actually changed
        $gitStatus = & git diff --staged --quiet
        if ($LASTEXITCODE -ne 0) {
            # Files have changed (git diff --quiet returns non-zero when there are differences)
            Write-Host "Committing and pushing updated root files..." -ForegroundColor Green

            # Configure git user for commit
            & git config user.name "GitHub Actions"
            & git config user.email "github-actions@github.com"

            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to configure git user"
            }

            & git commit -m "docs: Deploy root-level site files"
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to commit changes"
            }

            & git push
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to push changes"
            }

            Write-Host "✅ Root files deployed successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "Root files are up-to-date. No new commit needed." -ForegroundColor Yellow
        }
    }
    finally {
        # Go back to the original directory
        Pop-Location
    }
}
catch {
    Write-Error "Failed to deploy root files: $($_.Exception.Message)"
}
finally {
    # Clean up
    if (Test-Path $deployDir) {
        Remove-Item $deployDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Root file deployment complete." -ForegroundColor Cyan
