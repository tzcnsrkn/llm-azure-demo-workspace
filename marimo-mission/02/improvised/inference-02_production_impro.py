import marimo

__generated_with = "0.19.9"
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
    import seaborn as sns
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
    from sklearn.metrics import classification_report, confusion_matrix

    def show_plots():
        """Helper to automatically show fastai/matplotlib plots in Marimo"""
        return mo.mpl.interactive(plt.gcf())

    return (
        Path,
        classification_report,
        confusion_matrix,
        get_image_files,
        io,
        load_learner,
        mo,
        os,
        pd,
        plt,
        requests,
        sns,
        verify_images,
    )


@app.cell
def _():
    # Replace with your actual VM Public IP
    BASE_URL = "http://74.248.24.66"
    API_BASE_URL = f'{BASE_URL}:8080/images'
    print(f"Targeting Cache API at: {API_BASE_URL}")
    return (API_BASE_URL,)


@app.cell
def _():
    import sys
    print(sys.version)
    return


@app.cell
def _(API_BASE_URL, requests):
    class CacheClient:
        def __init__(self, base_url):
            self.base_url = base_url

        def ping(self):
            """Checks if the API is reachable."""
            target_url = f"{self.base_url}/1"
            print(f"DEBUG: Pinging {target_url} ...")

            try:
                response = requests.get(target_url, timeout=2)

                if response.status_code in [200, 404]:
                    print("Successfully connected to Cache API.")
                    return True
                else:
                    print(f"Connected, but received unexpected status: {response.status_code}")
                    return False

            # Catch RequestException (covers Connection, Timeout, and Redirect errors)
            except requests.exceptions.RequestException as e:            
                print("Error: Could not connect to Cache API.")
                print(f"DEBUG INFO: {e}")
                return False
            # Catch everything else (like missing http:// schema)
            except Exception as e:
                print(f"CRITICAL ERROR: {type(e).__name__}: {e}")
                return False

        def get(self, key):
            """Retrieves image bytes for a key."""
            try:
                response = requests.get(f"{self.base_url}/{key}")
                if response.status_code == 200:
                    return response.content # Returns bytes
                return None
            except Exception as e:
                print(f"Error getting key {key}: {e}")
                return None

        def set(self, key, data):
            """Stores image bytes."""
            try:
                # Send raw bytes in the body
                response = requests.post(f"{self.base_url}/{key}", data=data)
                return response.status_code == 200
            except Exception as e:
                print(f"Error setting key {key}: {e}")
                return False

    def connect_cache():
        client = CacheClient(API_BASE_URL)
        client.ping()
        return client

    return (connect_cache,)


@app.cell
def _(connect_cache):
    # Initialize connection
    cache = connect_cache()

    # Example Usage:
    # image_data = cache.get("my_image.png")
    # if image_data:
    #     print(f"Got image: {len(image_data)} bytes")
    return


@app.cell
def _(io, mo, os, re, requests):
    import hashlib
    import zipfile
    from urllib.parse import urljoin, quote
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def download_all_images_cache_api(
        api_url: str = "http://74.248.24.95:8080/images",
        download_path: str = "downloaded_images",
        workers: int = 16,
        timeout: int = 300, # Increased timeout for large zip downloads
        headers: dict | None = None,
    ):
        """
        Fetches images from the API. 
        Handles both 'application/zip' (bulk download) and 'application/json' (list of links).
        """
        if not api_url:
            return mo.callout("API URL is empty", kind="danger")

        session = requests.Session()
        if headers: session.headers.update(headers)

        # --- 1. Request the Endpoint ---
        print(f"Connecting to {api_url}...")
        try:
            response = session.get(api_url, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            return mo.callout(
                f"Connection Refused to {api_url}.\n"
                "1. Check if you are connected to the required VPN.\n"
                "2. Verify the server IP and Port (8080) are correct.", 
                kind="danger"
            )
        except Exception as e:
            return mo.callout(f"Error fetching data: {e}", kind="danger")

        # --- 2. Check Content Type ---
        content_type = response.headers.get("Content-Type", "")
        print(f"Content-Type received: {content_type}")

        # --- CASE A: Handle ZIP File (New API Behavior) ---
        if "application/zip" in content_type:
            print("Detected ZIP response. Extracting...")
            try:
                os.makedirs(download_path, exist_ok=True)

                # Load bytes into memory and unzip
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall(download_path)
                    file_list = z.namelist()

                print(f"Successfully extracted {len(file_list)} files to '{download_path}'.")

                # Show a sample of extracted files
                samples = file_list[:5]

                return mo.md(
                    f"**Download Report (ZIP Mode)**\n"
                    f"- **Endpoint:** `{api_url}`\n"
                    f"- **Status:** Success\n"
                    f"- **Files Extracted:** {len(file_list)}\n"
                    f"- **Target Folder:** `{download_path}`\n\n"
                    f"**Sample Files:**\n" + "\n".join([f"- `{s}`" for s in samples])
                )
            except Exception as e:
                return mo.callout(f"Failed to extract ZIP file: {e}", kind="danger")

        # --- CASE B: Handle JSON List (Old API Behavior / Fallback) ---
        try:
            data = response.json()
        except ValueError:
            return mo.callout(f"Endpoint returned non-JSON and non-ZIP data. (Type: {content_type})", kind="danger")

        # Parse the list
        image_items = []
        if isinstance(data, list):
            image_items = data
        elif isinstance(data, dict):
            for key in ["images", "files", "data", "items", "results"]:
                if key in data and isinstance(data[key], list):
                    image_items = data[key]
                    break

        if not image_items:
            return mo.callout("Connected, but found no list of images in the JSON response.", kind="warning")

        print(f"Found {len(image_items)} items in JSON list. Starting individual downloads...")
        os.makedirs(download_path, exist_ok=True)

        # Helper to parse item
        def _get_download_url_and_name(item):
            if isinstance(item, str):
                full_url = f"{api_url.rstrip('/')}/{quote(item)}"
                name = item
            elif isinstance(item, dict):
                raw_url = item.get("url") or item.get("src") or item.get("link") or item.get("path")
                name = item.get("name") or item.get("filename") or item.get("key")
                if not raw_url and name: raw_url = name

                if raw_url:
                    full_url = raw_url if raw_url.startswith("http") else f"{api_url.rstrip('/')}/{quote(raw_url)}"
                    if not name: name = raw_url.split("/")[-1]
                else:
                    return None, None
            else:
                return None, None
            name = re.sub(r"[^A-Za-z0-9._-]+", "_", str(name))
            return full_url, name

        # Worker function
        def _download_worker(item):
            url, name = _get_download_url_and_name(item)
            if not url: return False, "skipped", 0
            try:
                r = session.get(url, timeout=timeout)
                if r.status_code == 200:
                    if "." not in name:
                        ct = r.headers.get("Content-Type", "")
                        if "png" in ct: name += ".png"
                        elif "jpeg" in ct or "jpg" in ct: name += ".jpg"
                    with open(os.path.join(download_path, name), "wb") as f:
                        f.write(r.content)
                    return True, name, len(r.content)
            except:
                pass
            return False, name, 0

        # Execute ThreadPool
        success_cnt = 0
        fail_cnt = 0
        samples = []
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(_download_worker, item) for item in image_items]
            for fut in as_completed(futures):
                ok, name, size = fut.result()
                if ok:
                    success_cnt += 1
                    if len(samples) < 5: samples.append(f"{name} ({size}b)")
                else:
                    fail_cnt += 1

        return mo.md(
            f"**Download Report (JSON Mode)**\n"
            f"- **Endpoint:** `{api_url}`\n"
            f"- **Items Found:** {len(image_items)}\n"
            f"- **Downloaded:** {success_cnt}\n"
            f"- **Failed:** {fail_cnt}\n\n"
            f"**Sample Files:**\n" + "\n".join([f"- `{s}`" for s in samples])
        )

    # Run the function
    download_all_images_cache_api()
    return


@app.cell
def _(mo):
    # Create UI inputs for paths
    model_path_input = mo.ui.text(
        label="Path to export.pkl", 
        value="export.pkl",
        placeholder="e.g., ./export.pkl"
    )

    images_path_input = mo.ui.text(
        label="Folder containing images", 
        value="downloaded_images/",
        placeholder="e.g., /data/test_images"
    )

    # Display the inputs
    mo.md(
        f"""
        ### Configuration
        Please enter your paths below:

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
            # --- LOAD MODEL ---
            learn_inf = load_learner(p)
            load_message = f"✅ Model loaded successfully from `{p}`"
            vocab_msg = f"**Classes:** {learn_inf.dls.vocab}"
            mo.md(vocab_msg)  # Debug print

            # --- GET FILES ---
            files = get_image_files(image_source)

            if len(files) > 0:
                # --- VERIFY IMAGES (Optional but recommended) ---
                # This checks if files can be opened. If not, it unlinks (deletes) them.
                # We wrap this in a try/except to avoid stopping the whole script
                try:
                    failed = verify_images(files)
                    if len(failed) > 0:
                        print(f"Removing {len(failed)} corrupt images...")
                        failed.map(Path.unlink)
                        # Re-fetch files after deletion
                        files = get_image_files(image_source)
                except Exception as e:
                    print(f"Skipping verification step due to error: {e}")

                # --- PREDICT ---
                if len(files) > 0:
                    # num_workers=0 is safer for debugging and prevents some multiprocessing errors
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
def _(files, learn_inf, pd, preds):
    # --- PROCESS PREDICTIONS INTO DATAFRAME ---

    # Use the vocab from the learner
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
                "Confidence": pred_scores[i].item(),
            }
        )

    df = pd.DataFrame(results)

    # --- EXTRACT TRUE LABELS ---
    # Assuming filename format from Redis download: "image_<category>_..."
    # We split by "_" and take the second element (index 1)
    try:
        df["True_Label"] = df["Filename"].apply(lambda x: x.split("_")[1])
    except Exception as e:
        print(f"Warning: Could not extract True_Label from filenames. {e}")
        df["True_Label"] = "Unknown"

    # Display the first few rows
    print("Preview of processed data:")
    print(df.head())
    return (df,)


@app.cell
def _(confusion_matrix, df, learn_inf, pd):
    # --- CALCULATE CONFUSION MATRIX ---

    cm_df = pd.DataFrame()
    labels = []

    if not df.empty and learn_inf is not None:
        # We use the learner's vocab as the official list of labels
        labels = list(learn_inf.dls.vocab)

        # Filter out any rows where True_Label might not be in our model's vocab
        # (Optional, but prevents errors if random files are in the folder)
        valid_df = df[df["True_Label"].isin(labels)]

        if not valid_df.empty:
            cm = confusion_matrix(
                valid_df["True_Label"], valid_df["Prediction"], labels=labels
            )
            cm_df = pd.DataFrame(cm, index=labels, columns=labels)
        else:
            print("⚠️ No valid data found matching model labels.")
    return cm_df, labels


@app.cell
def _(cm_df, plt, sns):
    # --- VISUALIZE CONFUSION MATRIX ---

    if not cm_df.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues", ax=ax)
        ax.set_title("Confusion Matrix (Calculated from Predictions)")
        ax.set_ylabel("True Label")
        ax.set_xlabel("Predicted Label")
        plot_output = fig
    else:
        plot_output = "No data available for Confusion Matrix."

    plot_output
    return


@app.cell
def _(classification_report, df, labels):
    # --- CLASSIFICATION REPORT ---

    if not df.empty and labels:
        print("=== Classification Report ===")
        # We filter again to ensure we only report on known classes
        valid_df_report = df[df["True_Label"].isin(labels)]

        if not valid_df_report.empty:
            print(
                classification_report(
                    valid_df_report["True_Label"],
                    valid_df_report["Prediction"],
                    target_names=labels,
                    zero_division=0,
                )
            )
        else:
            print("No valid labels found for report.")
    return


@app.cell
def _(df):
    # --- SHOW MISCLASSIFIED IMAGES ---

    errors_view = None
    if not df.empty:
        # Filter where Prediction does not match True Label
        errors = df[df["True_Label"] != df["Prediction"]]

        print(f"=== Found {len(errors)} Misclassified Images ===")

        if not errors.empty:
            # Create a view for the UI
            errors_view = errors[["Filename", "True_Label", "Prediction", "Confidence"]]

    errors_view
    return


if __name__ == "__main__":
    app.run()
