#!/bin/bash

#########################################################
######## RUN below two once copied manually #############
#########################################################
# chmod +x deploy.sh
# ./deploy.sh

# Exit on error
set -e
# Azure Extension environment does not always provide it by default.
export HOME=/root

# Update apt (non-interactive to prevent debconf errors)
export DEBIAN_FRONTEND=noninteractive
sudo apt update

# Azure extension runs as root
cd $HOME 

# Ensure empty workspace to avoid git clone errors
rm -rf workspace

git clone https://github.com/tzcnsrkn/llm-azure-demo-workspace.git workspace
cd workspace

sudo apt install -y python3.10-venv
# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip and install main packages
pip install --upgrade pip
pip install fastai jupyter marimo

# Install requirements from the repository root
# This matches the file structure shown in your image
pip install -r requirements.txt

# Configure marimo
mkdir -p ~/.marimo && echo -e "[display]\ntheme = \"dark\"\ncode_editor_font_size = 16\n\n[runtime]\nauto_instantiate = true" > ~/.marimo/marimo.toml

# Start marimo editor
nohup marimo edit "marimo-mission/02/improvised" 02_production_impro.py --host 0.0.0.0 --port 2718 --no-token > marimo.log 2>&1 &



