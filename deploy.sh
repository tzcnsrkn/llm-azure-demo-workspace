#!/bin/bash

#########################################################
######## RUN below two once copied manually #############
#########################################################
# chmod +x deploy.sh
# ./deploy.sh

# Exit on error
set -e

# Azure Extension environment does not always provide it by default.
# NOTE: This implies the script runs as root via Custom Script Extension.
export HOME=/root

# Update apt (non-interactive to prevent debconf errors)
export DEBIAN_FRONTEND=noninteractive
sudo apt update

# Azure extension runs as root
cd $HOME 

# Ensure empty workspace to avoid git clone errors
rm -rf workspace

# 1. Clone the repository
git clone https://github.com/tzcnsrkn/llm-azure-demo-workspace.git workspace
cd workspace

# -----------------------------------------------------------------------------
# ADJUSTMENT: Merge Terraform Uploaded Datasets
# -----------------------------------------------------------------------------
# Terraform uploaded your local datasets to /home/azuser/datasets_upload
# We must move them into the cloned workspace/datasets folder.
# We assume the admin user is 'azuser' based on standard Azure defaults.
UPLOAD_DIR="/home/azuser/datasets_upload"

if [ -d "$UPLOAD_DIR" ]; then
    echo "Found uploaded datasets at $UPLOAD_DIR. Merging into workspace..."
    
    # Ensure the destination directory exists
    mkdir -p datasets
    
    # Copy the contents of the uploaded folder into the repo datasets folder
    # -r: recursive, -v: verbose, -f: force overwrite
    cp -rvf "$UPLOAD_DIR/"* datasets/
else
    echo "Warning: No uploaded datasets found at $UPLOAD_DIR. Using repository defaults."
fi
# -----------------------------------------------------------------------------

# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip and install main packages
pip install --upgrade pip
pip install fastai jupyter marimo

# Install requirements from the repository root
pip install -r requirements.txt

# Configure marimo
mkdir -p ~/.marimo && echo -e "[display]\ntheme = \"dark\"\ncode_editor_font_size = 16" > ~/.marimo/marimo.toml

# Start marimo editor [[4]](https://docs.marimo.io/guides/configuration/runtime_configuration/)[[5]](https://github.com/marimo-team/marimo/issues/7174)
# Using nohup to ensure it keeps running if the session disconnects
nohup marimo edit marimo-mission/02/improvised/02_production_impro.py --host 0.0.0.0 --port 2718 --no-token > marimo.log 2>&1 &
