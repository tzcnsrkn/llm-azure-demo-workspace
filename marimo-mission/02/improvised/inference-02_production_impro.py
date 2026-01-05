import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    import builtins
    import io
    import os
    import random
    import shutil
    import time
    from pathlib import Path
    from types import SimpleNamespace

    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import redis
    import requests
    import torch
    from fastai.callback.tracker import SaveModelCallback
    from fastai.vision.all import error_rate, resnet18, set_seed
    from fastai.vision.widgets import I
    from fastbook import (
        CategoryBlock,
        ClassificationInterpretation,
        DataBlock,
        Image,
        ImageBlock,
        L,
        Path,
        PILImage,
        RandomResizedCrop,
        RandomSplitter,
        Resize,
        ResizeMethod,
        aug_transforms,
        download_images,
        download_url,
        get_image_files,
        load_learner,
        parent_label,
        # resize_images,
        verify_images,
        vision_learner,
    )
    from fastcore.basics import Inf

    # from fastdownload import download_u
    from PIL import Image, ImageDraw, ImageFont

    def show_plots():
        """Helper to automatically show fastai/matplotlib plots in Marimo"""
        return mo.mpl.interactive(plt.gcf())

    return Path, get_image_files, load_learner, mo, os, redis, verify_images


@app.cell
def _(redis):
    def connect_redis(host="localhost", port=6379, db=0):
        """Establishes a connection to the Redis server."""
        try:
            r = redis.Redis(
                host="redis-11744.c53156.eu-central-1-mz.ec2.cloud.rlrcp.com",
                port=11744,
                password="8NhfcLwBJZvoM6yEBfyMozGn5TgPK5kN",
                decode_responses=False,
            )

            # WARNING: This deletes EVERYTHING in Redis
            # r.flushall()
            # print("Database flushed/cleared.")

            # Check connection
            r.ping()
            print("Successfully connected to Redis.")
            return r
        except redis.ConnectionError:
            print("Error: Could not connect to Redis.")
            return None

    return (connect_redis,)


@app.cell
def _():
    import sys

    print(sys.version)
    return


@app.cell
def _(connect_redis):
    r = connect_redis()
    return (r,)


@app.cell
def _(mo, os):
    def download_all_images(
        redis_conn, pattern="image:*", download_path="downloaded_images"
    ):
        if not redis_conn:
            return mo.callout("❌ Not connected to Redis", kind="danger")

        # Find all keys matching the pattern
        # keys() returns a list of bytes that can be decoded
        keys = [k.decode("utf-8") for k in redis_conn.keys(pattern)]

        if not keys:
            return mo.callout(
                f"⚠️ No keys found matching pattern: `{pattern}`", kind="warn"
            )

        os.makedirs(download_path, exist_ok=True)

        results = []

        for key in keys:
            try:
                # Getting raw bytes
                data = redis_conn.get(key)

                if not data:
                    continue

                # Saving to file
                safe_filename = key.replace("/", "_").replace(":", "_")
                # Add extension if missing
                if not safe_filename.endswith((".png", ".jpg", ".jpeg")):
                    safe_filename += ".png"

                file_path = os.path.join(download_path, safe_filename)

                with open(file_path, "wb") as f:
                    f.write(data)

                results.append(f"✅ Saved `{key}` -> `{file_path}`")

            except Exception as e:
                results.append(f"❌ Error on `{key}`: {e}")

        # Summary info
        return mo.vstack(
            [mo.md(f"**Found {len(keys)} keys.**"), mo.md("\n".join(results))]
        )

    return (download_all_images,)


@app.cell
def _(download_all_images, r):
    download_all_images(r, pattern="image:*")
    return


@app.cell
def _(mo):
    # Create UI inputs for paths
    model_path_input = mo.ui.text(
        label="Path to your language model, export.pkl",
        value="export.pkl",
        placeholder="e.g., ./export.pkl",
    )

    images_path_input = mo.ui.text(
        label="Folder containing images",
        value="downloaded_images/",
        placeholder="e.g., /data/test_images",
    )

    # Display the inputs
    mo.md(
        f"""
        ### Configuration
        Please enter the paths below:

        {model_path_input}

        {images_path_input}
        """
    )
    return (model_path_input,)


@app.cell
def _(
    Path,
    get_image_files,
    load_learner,
    mo,
    model_path_input,
    verify_images,
):
    from PIL import ImageFile

    ImageFile.LOAD_TRUNCATED_IMAGES = True

    learn_inf = None
    load_message = ""
    results_msg = ""
    vocab_msg = ""

    # Define your image source
    image_source = Path("downloaded_images")

    try:
        p = Path(model_path_input.value)

        if p.exists() and p.is_file():
            # --- Loading model ---
            learn_inf = load_learner(p)
            load_message = f"✅ Model loaded successfully from `{p}`"
            vocab_msg = f"**Classes:** {learn_inf.dls.vocab}"
            # ---

            # Getting files
            files = get_image_files(image_source)

            if len(files) > 0:
                # --- Verifying Images (Optional) ---
                # Check if files can be opened. If not, unlink (delete) them.
                # Avoid stopping the whole script
                try:
                    failed = verify_images(files)
                    if len(failed) > 0:
                        print(f"Removing {len(failed)} corrupt images...")
                        failed.map(Path.unlink)
                        # Re-fetch files to get the current
                        # state of the path after removal.
                        files = get_image_files(image_source)
                except Exception as e:
                    print(f"Skipping verification step due to error: {e}")

                # Predict
                if len(files) > 0:
                    # Safer to use num_workers=0 for debugging and prevents multiprocessing errors
                    test_dl = learn_inf.dls.test_dl(files, num_workers=0)
                    preds, _ = learn_inf.get_preds(dl=test_dl)
                    results_msg = f"✅ Generated predictions for {len(files)} images."
                else:
                    results_msg = "⚠️ All images were corrupt and removed."
            else:
                results_msg = f"⚠️ No images found in `{image_source}`."

        else:
            load_message = f"⚠️ File not found at `{p}`."

    except Exception as e:
        load_message = f"❌ Error: {e}"

    mo.md(f"""
    {load_message}

    {vocab_msg}

    {results_msg}
    """)
    return files, learn_inf, preds


@app.cell
def _(files, learn_inf, preds):
    vocab = learn_inf.dls.vocab

    # Get indices and scores
    pred_indices = preds.argmax(dim=1)
    pred_scores = preds.max(dim=1).values

    results = []
    for i, file_path in enumerate(files):
        results.append(
            {
                "Filename": file_path.name,
                "Prediction": vocab[pred_indices[i]],
                "Confidence": f"{pred_scores[i].item():.4f}",
            }
        )

    # Display
    pd.DataFrame(results)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
