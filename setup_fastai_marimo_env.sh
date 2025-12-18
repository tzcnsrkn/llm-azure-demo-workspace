#!/bin/bash

# Exit on error
set -e

# Create and enter dev directory
mkdir -p dev
cd dev

# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip and install main packages
pip install --upgrade pip
pip install fastai marimo

# Configure marimo with custom GUI settings
mkdir -p ~/.marimo && echo -e "[display]\ntheme = \"dark\"\ncode_editor_font_size = 16\n\n[runtime]\nauto_instantiate = true" > ~/.marimo/state.toml

# Install jupyter
pip install jupyter

# Create requirements.txt
# marimo convert 01_intro.ipynb > 01_intro.py
cat > ~/dev/venv/requirements.txt << 'EOF'
fastai>=2.0.0
graphviz
ipywidgets
matplotlib
nbdev>=0.2.12
pandas
scikit_learn
azure-cognitiveservices-search-imagesearch
sentencepiece
EOF

# Install requirements
pip install -r ~/dev/venv/requirements.txt

# Start marimo editor
# Add --headless --no-token at the end if using LightningAI
marimo edit 01_intro.py --host 0.0.0.0 --port 2718 --no-token
