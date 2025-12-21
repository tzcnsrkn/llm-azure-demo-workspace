import marimo

__generated_with = "0.18.4"
app = marimo.App()


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
    from fastai.vision.all import error_rate, resnet18, cnn_learner
    import builtins
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
        # load_learner,
        parent_label,
        # resize_images,
        verify_images,
        vision_learner,
    )
    # from fastdownload import download_u
    from PIL import Image, ImageDraw, ImageFont
    import random
    import matplotlib.pyplot as plt
    from fastcore.basics import Inf
    import torch
    def show_plots():
        """Helper to automatically show fastai/matplotlib plots in Marimo"""
        return mo.mpl.interactive(plt.gcf())
    return (
        CategoryBlock,
        ClassificationInterpretation,
        DataBlock,
        ImageBlock,
        L,
        Path,
        RandomResizedCrop,
        RandomSplitter,
        Resize,
        aug_transforms,
        cnn_learner,
        download_images,
        error_rate,
        get_image_files,
        mo,
        os,
        parent_label,
        requests,
        resnet18,
        show_plots,
        shutil,
        time,
        torch,
        verify_images,
    )


@app.cell
def _():
    # # FAKE DATA generation to the path /data/teddy in order to debug dropdowns

    # # import marimo as mo
    # # import os

    # # 1. SETUP: Define the class name your UI is looking for
    # target_class = "teddy"

    # # 2. GENERATE: Create dummy images in a folder structure that mimics real data
    # # We create a specific folder and filenames including "teddy" so filters pick them up
    # os.makedirs(f"data/{target_class}", exist_ok=True)
    # generated_files = []

    # for i in range(1, 6):
    #     # Naming the file with the class name is often required for these filters
    #     fname = f"data/{target_class}/{target_class}_sample_{i}.jpg"

    #     # Write a minimal valid JPG binary (1x1 pixel) so the browser can actually render it
    #     with open(fname, "wb") as f:
    #         f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x15\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x11\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00\xff\xd9')

    #     generated_files.append(fname)

    # # # 3. UI: Create the selector with the data we just made
    # # # This populates the "Total: X" count
    # # image_selector = mo.ui.multiselect(
    # #     options=generated_files,
    # #     label=f"Select Generated Images to Delete (Total: {len(generated_files)})"
    # # )

    # # # 4. DISPLAY: Show the header, the selector, and the images
    # # mo.vstack([
    # #     mo.md(f"### Showing top high-loss images for: **{target_class}** (Valid)"),
    # #     image_selector,
    # #     mo.md("_Preview of generated dummy images:_"),
    # #     mo.hstack([mo.image(src=f, width="100px", rounded=True) for f in generated_files], gap=1)
    # # ])

    # mo.vstack([    
    #     mo.md("_Preview of generated dummy images:_"),
    #     mo.hstack([mo.image(src=f, width="100px", rounded=True) for f in generated_files], gap=1)
    # ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    API Call : Brave Search
    """)
    return


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


@app.cell
def _():
    api_key = "BSAlRPIUZCDPc3TIQEbB10Jih3r9M9W"
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
    bear_types = "grizzly", "black", "teddy"
    path = Path("bears")

    # Delete old bears folder and download fresh images into path
    shutil.rmtree(path, ignore_errors=True)

    log_output = []

    if not path.exists():
        path.mkdir()
        for o in bear_types:
            dest = path / o      # Create subdirectory inside path
            dest.mkdir(exist_ok=True)

            log_output.append(f"Searching for {o} bear...")
            urls = search_images_brave(api_key, f"{o} bear")

            # download_images(dest, urls=urls[:50])  # Only download first 50 images
            download_images(dest, urls=urls)
            log_output.append(f"Downloaded {o} images to {dest}...")
            num_images = len(dest.ls())    # fastai specific
            log_output.append(f"Downloaded {num_images} {o} images to {dest}...")

            # Respect rate limits, increase if you're rate-limited
            time.sleep(1)

    # --- CLEANUP STEP ---
    # This checks every file. If it's not a valid image, it unlinks (deletes) it.
    log_output.append("Verifying images and removing corrupted files...")
    failed = verify_images(get_image_files(path))
    failed.map(Path.unlink)
    log_output.append(f"Removed {len(failed)} corrupt images.")
    # --------------------

    print("\n".join(log_output))
    return (path,)


@app.cell
def _(mo):
    mo.md(r"""
    End of API Call : Brave Search
    """)
    return


@app.cell
def _(
    CategoryBlock,
    DataBlock,
    ImageBlock,
    RandomResizedCrop,
    RandomSplitter,
    Resize,
    aug_transforms,
    get_image_files,
    parent_label,
    path,
):
    # Define DataBlock
    bears = DataBlock(
        blocks=(ImageBlock, CategoryBlock), 
        get_items=get_image_files, 
        splitter=RandomSplitter(valid_pct=0.2, seed=42),
        get_y=parent_label,
        item_tfms=Resize(128))

    # Augmentations
    bears = bears.new(
        item_tfms=RandomResizedCrop(224, min_scale=0.5),
        batch_tfms=aug_transforms())

    # Load Data
    dls = bears.dataloaders(path)
    return (dls,)


@app.cell
def _(cnn_learner, dls, error_rate, resnet18):
    # should_stop = True
    # mo.stop(should_stop, mo.md("Execution stopped. Testing the previous cells only."))

    # Train Model
    learn = cnn_learner(dls, resnet18, metrics=error_rate)
    learn.fine_tune(4)
    return (learn,)


@app.cell
def _(ClassificationInterpretation, learn, show_plots):
    interp = ClassificationInterpretation.from_learner(learn)
    interp.plot_confusion_matrix()
    show_plots()
    return


@app.cell
def _(mo):
    mo.md("""
    ## Image Classifier Cleaner (Marimo Version)
    """)
    return


@app.cell
def _(mo):
    # Create Dropdowns for filtering
    # Reference: https://docs.marimo.io/api/inputs/dropdown/

    select_split = mo.ui.dropdown(
        options=["Train", "Valid"], 
        value="Valid", 
        label="Dataset Split"
    )

    select_category = mo.ui.dropdown(
        options=["black", "grizzly", "teddy"], 
        value="teddy", 
        label="Category"
    )

    mo.hstack([select_split, select_category])
    return select_category, select_split


@app.cell
def _(dl, learn):
    # Get predictions and losses
    predst, targst, lossest = learn.get_preds(dl=dl, with_loss=True)
    return


@app.cell
def _(Path, dls, learn, mo, select_category, select_split, torch):
    # Logic to extract top losses based on dropdown selection

    ds_idx = 0 if select_split.value == "Train" else 1
    dl = dls[ds_idx]

    # Get predictions and losses
    preds, targs, losses = learn.get_preds(dl=dl, with_loss=True)

    # ERROR FIX: Ensure losses is a Tensor. 
    if isinstance(losses, list):
        losses = torch.tensor(losses)

    # Ensure targs is a Tensor
    if isinstance(targs, list):
        targs = torch.tensor(targs)

    # Sort by top losses
    idxs = losses.argsort(descending=True)

    # Filter by the selected category
    vocab = dls.vocab
    wanted_idx = vocab.o2i[select_category.value]

    # Create a mask for the specific category
    mask = targs[idxs] == wanted_idx

    # Apply mask to get indices sorted by loss
    top_idxs = idxs[mask]
    top_idxs_list = top_idxs.tolist()

    # Get the file paths
    all_items = dls.train.items if ds_idx == 0 else dls.valid.items
    model_high_loss_items = [all_items[i] for i in top_idxs_list]

    # --- APPEND DUMMY IMAGES ---
    dummy_path = Path(f"data/{select_category.value}")
    dummy_items = []

    if dummy_path.exists():    
        dummy_items = list(dummy_path.ls())

    # Combine lists
    # WARNING: You must swap the operands below in a production-like scenario where there is no need to prioritize dummy items.
    top_items = dummy_items + model_high_loss_items
    # ---------------------------

    # --- VISUALIZATION ---
    # 1. Create a header
    header = mo.md(f"**Showing top high-loss images + dummy images for: {select_category.value} ({select_split.value})**")

    # 2. Create a gallery of the first 5 images found
    if top_items:
        # We create a list of vertical stacks. 
        # Each item is a vstack containing [Image, Text].
        gallery_items = []

        for x in top_items[:5]:
            # The Image
            img = mo.image(src=str(x), width="100px", rounded=True)

            # The Text (Filename)
            # We use a small font size and word-wrap so long paths don't break the layout
            txt = mo.md(f"<div style='font-size: 10px; width: 100px; overflow-wrap: break-word; line-height: 1.1;'>{str(x)}</div>")

            # Combine them vertically
            item_stack = mo.vstack([img, txt], align="center")
            gallery_items.append(item_stack)

        # Display the list of stacks horizontally
        image_gallery = mo.hstack(
            gallery_items, 
            gap=1, 
            wrap=True,
            align="start" # Aligns items to the top
        )
        status_msg = mo.md(f"_Found {len(model_high_loss_items)} model errors and {len(dummy_items)} dummy images._")
    else:
        image_gallery = mo.md("🚫 No images found.")
        status_msg = mo.md("")

    # 3. Stack them together for display
    display_output = mo.vstack([header, status_msg, image_gallery])

    # 4. Render the output explicitly
    # (We use mo.output.replace to force display since we also need to return variables)
    mo.output.replace(display_output)

    # 5. CRITICAL: Return the variables so the next cells (selector/delete button) work!
    # (Implicit return of variables in scope)
    return dl, top_items


@app.cell
def _(mo, top_items):
    # Display the images using Marimo
    # We limit to top 5 for display performance

    images_to_show = []

    # Iterate through the list of Path objects directly
    for item in top_items[:5]:
        # Convert Path object to string for mo.image
        images_to_show.append(mo.image(src=str(item), width=200))
    return


@app.cell
def _(mo):
    # This creates the "trigger" variable
    get_file_list_version, set_file_list_version = mo.state(0)
    return get_file_list_version, set_file_list_version


@app.cell
def _(get_file_list_version, mo, top_items):
    # This cell creates the selector for the high-loss images.
    # It listens to 'get_file_list_version' so it refreshes after a delete.

    _version = get_file_list_version()

    # Filter the top_items to ensure we only show files that exist on disk
    current_files = [str(p) for p in top_items if p.exists()]

    cleaner_selector = mo.ui.multiselect(
        options=current_files,
        label=f"Select High-Loss Images to Delete (Total: {len(current_files)})"
    )

    cleaner_selector
    return (cleaner_selector,)


@app.cell
def _(cleaner_selector, mo):
    # 1. Get the current selection from the widget
    selected_files = cleaner_selector.value

    # 2. Logic: If nothing is selected, show a placeholder. 
    #    If items are selected, show them in a grid.
    if not selected_files:
        preview_section = mo.md("_Select images from the list above to preview them here._")
    else:
        # Create a list of image elements
        # We use a smaller width (150px) so they fit nicely side-by-side
        img_elements = [
            mo.image(src=f, width="150px", rounded=True, caption=f.split('/')[-1]) 
            for f in selected_files
        ]

        # Stack them horizontally (hstack) with wrapping enabled
        preview_section = mo.vstack([
            mo.md(f"### ⚠️ Previewing {len(selected_files)} image(s) marked for deletion:"),
            mo.hstack(img_elements, wrap=True, gap=1)
        ])

    # 3. Display the section
    preview_section
    return


@app.cell
def _(mo):
    delete_button = mo.ui.run_button(label="🗑️ Delete Selected Images", kind="danger")
    delete_button
    return (delete_button,)


@app.cell
def _(cleaner_selector, delete_button, mo, os, set_file_list_version):
    # 1. STOP if the button wasn't actually clicked.
    mo.stop(not delete_button.value, output=mo.md(""))

    # 2. Perform the deletion using the cleaner_selector
    files_to_delete = cleaner_selector.value
    deleted_count = 0

    if not files_to_delete:
        result_message = mo.md("ℹ️ No images selected.")
    else:
        for file_path_d in files_to_delete:
            try:
                if os.path.exists(file_path_d):
                    os.remove(file_path_d)
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file_path_d}: {e}")

        # 3. Update the state to refresh the selector cell
        set_file_list_version(lambda v: v + 1)
        result_message = mo.md(f"✅ **Deleted {deleted_count} images.**")

    result_message
    return


@app.cell
def _(mo):
    mo.md(r"""
    Checkpoint
    """)
    return


@app.cell
def _(mo):
    # 1. Dropdown to select where to move the images
    # We match the options from the main category selector
    target_category_selector = mo.ui.dropdown(
        options=["black", "grizzly", "teddy"], 
        label="Move to Category"
    )

    # 2. Button to execute the move
    move_button = mo.ui.run_button(label="🚚 Move Selected Images")

    # Display them
    mo.hstack([target_category_selector, move_button], justify="start")
    return move_button, target_category_selector


@app.cell
def _(
    Path,
    cleaner_selector,
    mo,
    move_button,
    set_file_list_version,
    shutil,
    target_category_selector,
):
    # 1. STOP if the move button wasn't clicked
    mo.stop(not move_button.value, output=mo.md(""))

    # 2. Get files and target
    files_to_move = cleaner_selector.value
    target_cat = target_category_selector.value

    moved_count = 0

    # 3. Validation
    if not files_to_move:
        result_msg = mo.md("ℹ️ No images selected to move.")
    elif not target_cat:
        result_msg = mo.md("⚠️ Please select a target category.")
    else:
        # 4. Perform the move
        # Logic: shutil.move(src, dst)
        for file_path_m in files_to_move:
            try:
                # Convert string path to Path object for easier manipulation
                src_path = Path(file_path_m)

                # Construct destination: parent_dir / new_category / filename
                # Assuming structure is: data/category/image.jpg or bears/category/image.jpg
                # We go up two levels to find the root, then down into the new category
                dest_path = src_path.parent.parent / target_cat / src_path.name

                # Ensure destination folder exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Move the file
                shutil.move(str(src_path), str(dest_path))
                moved_count += 1
            except Exception as e:
                print(f"Error moving {file_path_m}: {e}")

        # 5. Update state to refresh the list (remove moved items from current view)
        set_file_list_version(lambda v: v + 1)
        result_msg = mo.md(f"✅ **Moved {moved_count} images to '{target_cat}'.**")

    result_msg
    return


if __name__ == "__main__":
    app.run()
