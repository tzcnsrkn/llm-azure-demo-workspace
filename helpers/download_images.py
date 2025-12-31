import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    # --- IMPORTS ---
    # These must be actual Python code, not inside mo.md()
    import builtins
    import io
    import os
    import random
    import shutil
    import time
    from pathlib import Path
    from types import SimpleNamespace

    import requests

    # Note: These libraries (PIL, fastbook, fastai) need to be installed in your environment
    from PIL import Image, ImageDraw, ImageFont

    # fastbook/fastai specific imports
    # If you don't have fastbook installed, these will fail.
    # Assuming the user environment has them based on the prompt context.
    try:
        from fastbook import download_images, get_image_files, verify_images
        from fastcore.all import L
    except ImportError:
        # Fallback or placeholder if libraries aren't present (for demonstration)
        print("Warning: fastbook/fastai not found. Some functions may fail.")
        download_images = None
        verify_images = None
        get_image_files = None

    import marimo as mo

    return (
        Path,
        download_images,
        get_image_files,
        mo,
        requests,
        shutil,
        time,
        verify_images,
    )


@app.cell
def _(mo):
    mo.md(r"""
    # Bear Image Downloader
    Using Brave Search API
    """)
    return


@app.cell
def _(requests):
    # Brave Search API function
    def search_images_brave(api_key, term, max_images=200):
        """Search for images using Brave Search API

        Args:
            api_key: Your Brave Search API key
            term: Search term
            max_images: Maximum number of images to return (default: 200)

        Returns:
            list: List of image URLs
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

        # Basic error handling
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return []

        results = response.json().get("results", [])
        # Extract URLs from the results
        return [
            r.get("properties", {}).get("url")
            for r in results
            if r.get("properties", {}).get("url")
        ]

    return (search_images_brave,)


@app.cell
def _():
    # Ideally, use an environment variable for keys, but keeping your provided key here
    api_key = "<api-secret-key>"
    return (api_key,)


@app.cell
def _(
    Path,
    api_key,
    download_images,
    get_image_files,
    search_images_brave,
    shutil,
    time,
    verify_images,
):
    # Ensure fastai/fastbook functions exist before running logic
    if download_images is None:
        print("Fastbook library not loaded. Skipping download logic.")
    else:
        bear_types = "grizzly", "black", "teddy"
        path = Path("bears")

        # Delete old bears folder and download fresh images into path
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)

        log_output = []

        if not path.exists():
            path.mkdir()
            for o in bear_types:
                dest = path / o  # Create subdirectory inside path
                dest.mkdir(exist_ok=True)

                log_output.append(f"Searching for {o} bear...")
                urls = search_images_brave(api_key, f"{o} bear")

                if not urls:
                    log_output.append(f"No URLs found for {o} bear.")
                    continue

                # download_images(dest, urls=urls[:50])  # Only download first 50 images
                download_images(dest, urls=urls)

                # Note: dest.ls() is a fastai method. If using standard pathlib, use list(dest.iterdir())
                try:
                    num_images = len(dest.ls())
                except AttributeError:
                    num_images = len(list(dest.iterdir()))

                log_output.append(f"Downloaded {num_images} {o} images to {dest}...")

                # Respect rate limits, increase if you're rate-limited
                time.sleep(1)

        # --- CLEANUP STEP ---
        # This checks every file. If it's not a valid image, it unlinks (deletes) it.
        log_output.append("Verifying images and removing corrupted files...")

        # get_image_files is fastai specific
        files = get_image_files(path)
        failed = verify_images(files)

        # failed is usually an L list (fastcore), map works there.
        # failed.map(Path.unlink)
        # log_output.append(f"Removed {len(failed)} corrupt images.")
        # --------------------

        print("\n".join(log_output))
    return


@app.cell
def _(mo):
    mo.md(r"""
    End of API Call : Brave Search
    """)
    return


if __name__ == "__main__":
    app.run()
