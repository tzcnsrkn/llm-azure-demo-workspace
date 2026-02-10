#!/bin/bash

# Exit on error
set -e

# Azure Extension environment setup
# The extension runs as root, so we ensure HOME is set correctly
export HOME=/root
export DEBIAN_FRONTEND=noninteractive

echo "Starting deployment script..."

# -----------------------------------------------------------------------------
# FIX 1: Disable broken Scala/sbt repo (scala.jfrog.io)
# -----------------------------------------------------------------------------
# The DSVM image often has a broken link here, causing 'apt-get update' to fail.
echo "Checking for broken scala.jfrog.io apt sources..."
for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do
  [ -f "$f" ] || continue
  if grep -q 'scala\.jfrog\.io' "$f"; then
    echo " - Disabling broken source in $f"
    sed -i.bak '/scala\.jfrog\.io/ { /^[[:space:]]*#/! s|^[[:space:]]*|# | }' "$f"
  fi
done

# -----------------------------------------------------------------------------
# FIX 2: Update apt and Install python3.10-venv
# -----------------------------------------------------------------------------
# This was the cause of the "ensurepip is not available" error.
echo "Running apt update..."
# We allow update to fail (|| true) in case of minor transient network issues, 
# but usually, the fix above ensures it works.
apt-get update || echo "WARNING: apt-get update had errors, attempting to continue..."

echo "Installing python3.10-venv..."
apt-get install -y python3.10-venv

# -----------------------------------------------------------------------------
# Workspace Setup
# -----------------------------------------------------------------------------
cd $HOME 

# Ensure empty workspace to avoid git clone errors
rm -rf workspace

# Clone the repository
git clone https://github.com/tzcnsrkn/llm-azure-demo-workspace.git workspace
cd workspace

# -----------------------------------------------------------------------------
# Merge Terraform Uploaded Datasets
# -----------------------------------------------------------------------------
UPLOAD_DIR="/home/azuser/datasets_upload"

if [ -d "$UPLOAD_DIR" ]; then
    echo "Found uploaded datasets at $UPLOAD_DIR. Merging into workspace..."
    mkdir -p datasets
    cp -rvf "$UPLOAD_DIR/"* datasets/
else
    echo "Warning: No uploaded datasets found. Using repository defaults."
fi

# -----------------------------------------------------------------------------
# Python Environment Setup
# -----------------------------------------------------------------------------
# Create and activate virtual environment
# This will now succeed because python3.10-venv is installed
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip and install main packages
pip install --upgrade pip
pip install fastai jupyter marimo

# Install requirements from the repository root
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# -----------------------------------------------------------------------------
# Marimo Configuration and Start
# -----------------------------------------------------------------------------
mkdir -p ~/.marimo && echo -e "[display]\ntheme = \"dark\"\ncode_editor_font_size = 16" > ~/.marimo/marimo.toml

echo "Starting Marimo..."
# Using nohup to ensure it keeps running
nohup marimo edit marimo-mission/02/improvised/02_production_impro.py --host 0.0.0.0 --port 2718 --no-token > marimo.log 2>&1 &

echo "Deployment script finished successfully."
