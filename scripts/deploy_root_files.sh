#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# This script deploys a list of specified files (e.g., 404.html, robots.txt)
# to the root of the gh-pages branch.
# It's designed to be called from a GitHub Actions workflow.
#
# Arguments:
# $1: The GitHub repository name (e.g., "a2aproject/A2A").
# $2: The GITHUB_TOKEN for authentication.

# --- Configuration ---
# List of files to copy from the source directory to the root of the gh-pages branch.
FILES_TO_DEPLOY=("404.html" "robots.txt" "llms.txt", "llms-full.txt")
# The source directory in the main branch where these files are located.
SOURCE_DIR="docs"

# --- Validate Input ---
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Error: Missing required arguments."
  echo "Usage: $0 <owner/repo> <github_token>"
  exit 1
fi

REPO_NAME=$1
GH_TOKEN=$2

echo "Deploying root-level site files for repository: $REPO_NAME"
echo "Files to deploy: ${FILES_TO_DEPLOY[*]}"

# --- Deployment Logic ---
# Clone the gh-pages branch using the provided token for authentication.
# This ensures we have push access.
git clone --branch=gh-pages --single-branch --depth=1 "https://x-access-token:${GH_TOKEN}@github.com/${REPO_NAME}.git" gh-pages-deploy

# Navigate into the cloned directory
cd gh-pages-deploy

# Loop through the files, copy them from the source checkout, and add them to git.
# The source checkout is in the parent directory (`../`).
for file in "${FILES_TO_DEPLOY[@]}"; do
  SOURCE_FILE="../${SOURCE_DIR}/${file}"
  if [ -f "$SOURCE_FILE" ]; then
    echo "Copying $file..."
    cp "$SOURCE_FILE" "./$file"
    git add "$file"
  else
    echo "Warning: Source file not found, skipping: $SOURCE_FILE"
  fi
done

# Commit and push only if any of the files have actually changed
if git diff --staged --quiet; then
  echo "Root files are up-to-date. No new commit needed."
else
  echo "Committing and pushing updated root files..."
  # Configure git user for commit
  git config user.name "GitHub Actions"
  git config user.email "github-actions@github.com"

  git commit -m "docs: Deploy root-level site files"
  git push
fi

# Go back to the original directory and clean up
cd ..
rm -rf gh-pages-deploy

echo "Root file deployment complete."
