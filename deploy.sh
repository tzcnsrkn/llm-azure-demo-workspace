#!/bin/bash
set -e

# Azure Extension environment setup
export HOME=/root
export DEBIAN_FRONTEND=noninteractive

echo "Starting deployment fix..."

# 1. FIX: disable broken scala/sbt repo (scala.jfrog.io)
# This prevents apt-get update from failing due to the broken link in the DSVM image.
echo "Disabling scala.jfrog.io apt sources (if any)..."
for f in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do
  [ -f "$f" ] || continue
  if grep -q 'scala\.jfrog\.io' "$f"; then
    echo " - $f"
    sed -i.bak '/scala\.jfrog\.io/ { /^[[:space:]]*#/! s|^[[:space:]]*|# | }' "$f"
  fi
done

# 2. Update apt and Install python3.10-venv (CRITICAL FIX)
echo "Running apt update and installing venv..."
apt-get update || echo "WARNING: apt-get update had errors, continuing anyway..."
apt-get install -y python3.10-venv

# 3. Setup Workspace
cd $HOME
rm -rf workspace

# Clone the repository
git clone https://github.com/tzcnsrkn/llm-azure-demo-workspace.git workspace
cd workspace

# 4. Merge Terraform Uploaded Datasets
UPLOAD_DIR="/home/azuser/datasets_upload"
if [ -d "$UPLOAD_DIR" ]; then
    echo "Found uploaded datasets at $UPLOAD_DIR. Merging..."
    mkdir -p datasets
    cp -rvf "$UPLOAD_DIR/"* datasets/
else
    echo "No uploaded datasets found. Using defaults."
fi

# 5. Python Setup
python3.10 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install fastai jupyter marimo

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

# 6. Configure and Start Marimo
mkdir -p ~/.marimo 
echo -e "[display]\ntheme = \"dark\"\ncode_editor_font_size = 16" > ~/.marimo/marimo.toml

echo "Starting Marimo..."
nohup marimo edit marimo-mission/02/improvised/02_production_impro.py --host 0.0.0.0 --port 2718 --no-token > marimo.log 2>&1 &

echo "Deployment script finished successfully."
