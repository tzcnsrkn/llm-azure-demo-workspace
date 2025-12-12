import marimo

__generated_with = "0.18.3"
app = marimo.App(width="full")


@app.cell
def _(mo):
    mo.md("""
    # Bear Classifier - Data Collection

    This notebook searches for images of bears (Grizzly, Black, Teddy), downloads them, and prepares them for training.
    """)
    return


@app.cell
def _():
    import io
    import os
    import shutil
    import time
    from pathlib import Path
    from types import SimpleNamespace

    import marimo as mo
    import requests
    from fastai.vision.all import error_rate, resnet18
    from fastai.vision.widgets import ImageClassifierCleaner
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
        resize_images,
        verify_images,
        vision_learner,
    )
    from fastdownload import download_url
    from PIL import Image
    return (
        CategoryBlock,
        DataBlock,
        Image,
        ImageBlock,
        L,
        Path,
        RandomSplitter,
        Resize,
        download_images,
        download_url,
        get_image_files,
        io,
        mo,
        parent_label,
        requests,
        time,
        verify_images,
    )


@app.cell
def _():
    api_key = "BSAlRPIUZCDPc3TIQEbB10Jih3r9M9W"
    return (api_key,)


@app.cell
def _(L, requests):
    # Brave Search API function
    def search_images_brave(api_key, term, max_images=200):
        """Search for images using Brave Search API

        Args:
            api_key: Your Brave Search API key
            term: Search term
            max_images: Maximum number of images to return (default: 200)

        Returns:
            L: fastcore L list of image URLs
        """
        params = {"q": term, "source": "web", "search_lang": "en", "count": max_images}
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        }
        # Brave Search API endpoint
        url = "https://api.search.brave.com/res/v1/images/search"

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            results = response.json()
            # Extract image URLs from the 'results' list inside the response
            # The structure depends on API version but usually:
            # response['results'] -> list of dicts -> 'properties' -> 'url'
            # Or sometimes directly 'url'.
            if "results" in results:
                return L([img["properties"]["url"] for img in results["results"]])
            else:
                return L([])
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return L([])
    return (search_images_brave,)


@app.cell(hide_code=True)
def _(api_key, search_images_brave):
    results = search_images_brave(api_key, "grizzly bear")
    ims = results  # URLs already extracted, no .attrgot needed
    len(ims)  # will always be printed, no need to call print()
    return (ims,)


@app.cell
def _(Image, download_url, ims, io, mo):
    import random

    # 1. Pick random image URL
    random_url = random.choice(ims)

    # 2. Define destination
    _dest = "images/grizzly.jpg"

    # 3. Download the URL
    download_url(random_url, _dest)

    # 4. Open with PIL
    _im = Image.open(_dest)

    # 5. Create Thumbnail
    _im.thumbnail((128, 128))

    # 6. Display in Marimo
    # Convert to bytes
    _img_byte_arr = io.BytesIO()
    _im.save(_img_byte_arr, format=_im.format)

    test_image_display = mo.vstack(
        [
            mo.md(f"✅ **API Connection Successful.** Found {ims[0]}"),
            # width to specific pixels or percentage (e.g. "50%")
            mo.image(_img_byte_arr.getvalue(), width=300),
        ]
    )

    test_image_display
    return


@app.cell
def _(Path, api_key, download_images, search_images_brave, time):
    bear_types = "grizzly", "black", "teddy"
    path = Path("bears")

    log_output = []

    if not path.exists():
        path.mkdir()
        for o in bear_types:
            dest = path / o
            dest.mkdir(exist_ok=True)

            log_output.append(f"Searching for {o} bear...")
            urls = search_images_brave(api_key, f"{o} bear")

            log_output.append(f"Downloading {o} images to {dest}...")
            download_images(dest, urls=urls[:50])  # Only download first 50 images

            # Respect rate limits
            time.sleep(1)
    return (path,)


@app.cell
def _(get_image_files, path):
    fns = get_image_files(path)
    fns
    return (fns,)


@app.cell
def _(fns, verify_images):
    failed = verify_images(fns)
    failed
    return (failed,)


@app.cell
def _(Path, failed):
    failed.map(Path.unlink)
    return


@app.cell
def _(
    CategoryBlock,
    DataBlock,
    ImageBlock,
    RandomSplitter,
    Resize,
    get_image_files,
    parent_label,
):
    bears = DataBlock(
        blocks=(ImageBlock, CategoryBlock), 
        get_items=get_image_files, 
        splitter=RandomSplitter(valid_pct=0.3, seed=42),
        get_y=parent_label,
        item_tfms=Resize(128))
    return


if __name__ == "__main__":
    app.run()
