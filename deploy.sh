#########################################################
######## RUN below two once copied manually #############
#########################################################
# chmod +x deploy.sh
# ./deploy.sh

#!/bin/bash

# Exit on error
set -e

# Create and enter workspace directory
mkdir -p workspace
cd workspace

sudo apt update
sudo apt install -y python3.10-venv

# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip and install main packages
pip install --upgrade pip
pip install fastai jupyter marimo    # run duration: ~5.5 min

# Create requirements.txt
mkdir -p ~/venv && echo -e "fastai>=2.0.0\ngraphviz\nipywidgets\nmatplotlib\nnbdev>=0.2.12\npandas\nscikit_learn\nazure-cognitiveservices-search-imagesearch\nsentencepiece\nfastbook" > ~/workspace/venv/requirements.txt

# Configure marimo with custom GUI settings
mkdir -p ~/venv/.marimo && echo -e "[display]\ntheme = \"dark\"\ncode_editor_font_size = 16\n\n[runtime]\nauto_instantiate = true" > ~/.marimo/marimo.toml

# marimo convert 01_intro.ipynb > 01_intro.py

# Install requirements
pip install -r ~/venv/requirements.txt

# Start marimo editor
# Add --headless --no-token at the end if using LightningAI

marimo edit 02_production_impro.py --host 0.0.0.0 --port 2718 --no-token
