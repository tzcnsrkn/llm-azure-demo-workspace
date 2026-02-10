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
    export DEBIAN_FRONTEND=noninteractive
    export NEEDRESTART_MODE=a
    
    # wait for first-boot tasks that often hold dpkg/apt locks
    if command -v cloud-init >/dev/null 2>&1; then
      cloud-init status --wait || true
    fi
    
    while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || fuser /var/lib/apt/lists/lock >/dev/null 2>&1; do
      echo "Waiting for apt/dpkg lock..."
      sleep 5
    done
    
    # retry update (transient 404/hash-mismatch happens on mirrors)
    for i in 1 2 3 4 5; do
      echo "apt-get update attempt $i/5"
      if apt-get -o Acquire::Retries=5 -o Dpkg::Use-Pty=0 -y update; then
        break
      fi
      rm -rf /var/lib/apt/lists/*
      sleep 10
    done
    
    dpkg --configure -a || true
    
    apt-get -o Dpkg::Use-Pty=0 -y install --no-install-recommends python3-venv

    apt-get update
    apt-get install -y --no-install-recommends python3.10-venv
    
    # Create and activate virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Upgrade pip and install main packages
    pip install --upgrade pip
    pip install fastai jupyter marimo

    # Install requirements from the repository root
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    fi

    # Configure marimo
    mkdir -p ~/.marimo 
    echo -e "[display]\ntheme = \"dark\"\ncode_editor_font_size = 16" > ~/.marimo/marimo.toml

    # Start marimo editor 
    # Using nohup to ensure it keeps running if the session disconnects
    nohup marimo edit marimo-mission/02/improvised/02_production_impro.py --host 0.0.0.0 --port 2718 --no-token > marimo.log 2>&1 &

    echo "Deployment script finished successfully."




