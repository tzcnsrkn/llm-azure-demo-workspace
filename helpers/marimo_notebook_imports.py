# ============================================================================
# MARIMO IMPORTS - SECTION-BASED
# ============================================================================
marimo_imports = {
    "fastai_01_intro": [
        "import marimo as mo",
        "from fastai.vision.all import untar_data, URLs, ImageDataLoaders, get_image_files, Resize, cnn_learner, resnet34, error_rate, PILImage, SegmentationDataLoaders, unet_learner, vision_learner, defaults, ProgressCallback",
        "from fastai.text.all import TextDataLoaders, text_classifier_learner, AWD_LSTM, accuracy",
        "from fastai.tabular.all import TabularDataLoaders, Categorify, FillMissing, Normalize, tabular_learner",
        "from fastai.collab import CollabDataLoaders, collab_learner",
        "import numpy as np",
        "from types import SimpleNamespace",
        "import graphviz",
        "import matplotlib.pyplot as plt"
    ],
    "fastai_02_production": [
        "import marimo as mo",
        "import os",
        "import shutil",
        "from types import SimpleNamespace",
        "from pathlib import Path",
        "from PIL import Image",
        "from fastbook import DataBlock, ImageBlock, CategoryBlock, get_image_files, RandomSplitter, parent_label, Resize, ResizeMethod, RandomResizedCrop, aug_transforms, vision_learner, ClassificationInterpretation, load_learner, PILImage, Path, Image, download_url, download_images, verify_images, resize_images, L",
        "from fastai.vision.widgets import ImageClassifierCleaner",
        "from fastai.vision.all import resnet18, error_rate",
        "from fastdownload import download_url",
        "import requests",
        "import io",
        "import time"
    ]
}
