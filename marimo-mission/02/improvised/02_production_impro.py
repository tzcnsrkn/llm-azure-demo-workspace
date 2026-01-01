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
    import requests
    import torch
    from fastai.vision.all import error_rate, resnet18
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
    from fastcore.basics import Inf

    # from fastdownload import download_u
    from PIL import Image, ImageDraw, ImageFont

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
        vision_learner,
    )


@app.cell
def _(Path):
    # Setup path (Assuming the 'datasets/bears' folder exists)
    path = Path('datasets/bears')
    return (path,)


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
        item_tfms=Resize(128),
    )

    # Augmentations
    bears = bears.new(
        item_tfms=RandomResizedCrop(224, min_scale=0.5), batch_tfms=aug_transforms()
    )

    # Load Data
    dls = bears.dataloaders(path)
    return (dls,)


@app.cell
def _(dls, error_rate, resnet18, vision_learner):
    # should_stop = True
    # mo.stop(should_stop, mo.md("Execution stopped. Testing the previous cells only."))

    # Train Model
    # https://docs.fast.ai/vision.learner.html#cnn_learner
    learn = vision_learner(dls, resnet18, metrics=error_rate)
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
    ## Image Classifier Cleaner
    """)
    return


@app.cell
def _(mo):
    # Create Dropdowns for filtering
    # Reference: https://docs.marimo.io/api/inputs/dropdown/

    select_split = mo.ui.dropdown(
        options=["Train", "Valid"], value="Valid", label="Dataset Split"
    )

    select_category = mo.ui.dropdown(
        options=["black", "grizzly", "teddy"], value="teddy", label="Category"
    )

    mo.hstack([select_split, select_category])
    return select_category, select_split


@app.cell
def _(dls, learn, select_split, torch):
    ds_idx = 0 if select_split.value == "Train" else 1
    dl = dls[ds_idx]

    # Get predictions and losses
    probs, targs, losses = learn.get_preds(dl=dl, with_loss=True)

    # Ensure losses is a Tensor. 
    if isinstance(losses, list):
        losses = torch.tensor(losses)

    # Ensure targs is a Tensor
    if isinstance(targs, list):
        targs = torch.tensor(targs)
    return ds_idx, losses, probs, targs


@app.cell
def _(
    Path,
    dls,
    ds_idx,
    losses,
    mo,
    probs,
    select_category,
    select_split,
    targs,
):
    # Logic to extract top losses based on dropdown selection

    # Create Loss & Probability Maps for better visual traceability ---
    current_items = dls.train.items if ds_idx == 0 else dls.valid.items

    # Convert the tensor of losses into a simple list of floats
    # .view(-1) ensures it's flat, .tolist() converts to Python floats
    loss_values = losses.view(-1).tolist()

    # File paths with their loss values into a dictionary
    loss_map = dict(zip(current_items, loss_values))

    # Probability Map
    max_probs, _ = probs.max(dim=1)
    prob_values = max_probs.tolist()

    # Map file paths to their probability index
    prob_map = dict(zip(current_items, prob_values))
    # ---

    # Sort by top losses
    idxs = losses.argsort(descending=True)

    # Filter by the selected category
    vocab = dls.vocab
    wanted_idx = vocab.o2i[select_category.value]

    # Create a mask for the specific category
    mask = targs[idxs] == wanted_idx
    top_idxs = idxs[mask]
    top_idxs_list = top_idxs.tolist()

    # Get file paths
    all_items = dls.train.items if ds_idx == 0 else dls.valid.items
    model_high_loss_items = [all_items[i] for i in top_idxs_list]

    # --- Append Dummy Images (if any provided) ---
    dummy_path = Path(f"data/{select_category.value}")
    dummy_items = []

    if dummy_path.exists():    
        dummy_items = list(dummy_path.ls())

    # Combine lists
    # WARNING: Swap the operands below in a production-like 
    # scenario where no need to prioritize dummy items.
    top_items = dummy_items + model_high_loss_items
    # ---------------------------
    # --- VISUALIZATION ---
    # 1. Create a header
    header = mo.md(
        f"**Showing top high-loss images + dummy images for: {select_category.value} ({select_split.value})**"
    )

    # Create a gallery of the first 5 images found
    if top_items:
        # Create a list of vertical stacks. 
        # Each item is a vstack containing [Image, Text].
        gallery_items = []

        for x in top_items[:5]:
            # how marimo handles image
            img = mo.image(src=str(x), width="100px", rounded=True)
            loss_val = loss_map.get(x, None)
            prob_val = prob_map.get(x, None)

            if loss_val is not None:  # real image from the model
                loss_html = f"<span style='color:red; font-weight:bold;'>Loss: {loss_val:.2f}</span>"
                # Shows how confident the model was
                prob_html = f"<span style='color:orange; font-size:9px;'>Probability: {prob_val:.2f}</span>"
            else:  # dummy image
                loss_html = (
                    "<span style='color:blue; font-weight:bold;'>Dummy (No Loss)</span>"
                )
                prob_html = (
                    "<span style='color:#999; font-size:9px;'>(No Probability)</span>"
                )

            # The Text (Filename)
            # small font size and word-wrap to ensure paths don't break the layout
            txt = mo.md(
                f"<div style='font-size: 10px; width: 100px; overflow-wrap: break-word; line-height: 1.1;'>"
                f"{loss_html}<br/>"
                f"{prob_html}<br/>"
                f"{x.name}"
                f"</div>"
            )
            # Combine vertically
            item_stack = mo.vstack([img, txt], align="center")
            gallery_items.append(item_stack)

        # Display the list of stacks horizontally
        image_gallery = mo.hstack(
            gallery_items, 
            gap=1, 
            wrap=True,
            align="start"     # Aligns items to the top
        )
        status_msg = mo.md(f"_Found {len(model_high_loss_items)} model errors and {len(dummy_items)} dummy images._")
    else:
        image_gallery = mo.md("🚫 No images found.")
        status_msg = mo.md("")

    # Stack together for display
    display_output = mo.vstack([header, status_msg, image_gallery])

    # Render the output explicitly
    # Using mo.output.replace to force display to return variables implicitly
    mo.output.replace(display_output)
    return (top_items,)


@app.cell
def _(mo, top_items):
    # Display the images using Marimo api
    # Limit: 5 for display performance

    images_to_show = []

    # Iterate the list of Path objects
    for item in top_items[:5]:
        # Convert Path object to string for mo.image
        images_to_show.append(mo.image(src=str(item), width=200))
    return


@app.cell
def _(mo):
    # Create the "trigger" variable
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
    # Get the current selection from the widget
    selected_files = cleaner_selector.value

    # Logic: If nothing is selected, show a placeholder. 
    # Otherwise, show them in a grid.
    if not selected_files:
        preview_section = mo.md("_Select images from the list above to preview them here._")
    else:
        # Create a list of image elements
        # Use a smaller width (150px) to fit nicely side-by-side
        img_elements = [
            mo.image(src=f, width="150px", rounded=True, caption=f.split('/')[-1]) 
            for f in selected_files
        ]

        # Stack them horizontally (hstack) with wrapping enabled
        preview_section = mo.vstack([
            mo.md(f"### ⚠️ Previewing {len(selected_files)} image(s) marked for deletion:"),
            mo.hstack(img_elements, wrap=True, gap=1)
        ])

    # Display the section
    preview_section
    return


@app.cell
def _(mo):
    delete_button = mo.ui.run_button(label="🗑️ Delete Selected Images", kind="danger")
    delete_button
    return (delete_button,)


@app.cell
def _(cleaner_selector, delete_button, mo, os, set_file_list_version):
    # STOP if the button wasn't actually clicked.
    mo.stop(not delete_button.value, output=mo.md(""))

    # Perform the deletion using the cleaner_selector
    files_to_delete = cleaner_selector.value
    deleted_count = 0

    if not files_to_delete:
        result_message = mo.md("ℹ️ No images selected.")
    else:
        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

        # Update the state to refresh the selector cell
        set_file_list_version(lambda v: v + 1)
        result_message = mo.md(f"✅ **Deleted {deleted_count} images.**")

    result_message
    return


@app.cell
def _(mo):
    # Dropdown to select where to move the images
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
    # STOP if the move button wasn't clicked
    mo.stop(not move_button.value, output=mo.md(""))

    # Get files and target
    files_to_move = cleaner_selector.value
    target_cat = target_category_selector.value

    moved_count = 0

    if not files_to_move:
        result_msg = mo.md("ℹ️ No images selected to move.")
    elif not target_cat:
        result_msg = mo.md("⚠️ Please select a target category.")
    else:
        for file_path_m in files_to_move:
            try:
                # Convert string path to Path object
                src_path = Path(file_path_m)

                # destination: parent_dir / new_category / filename
                dest_path = src_path.parent.parent / target_cat / src_path.name

                # Ensure destination exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Move the file
                shutil.move(str(src_path), str(dest_path))
                moved_count += 1
            except Exception as e:
                print(f"Error moving {file_path_m}: {e}")

        # Update state to refresh the list (remove moved items from current view)
        set_file_list_version(lambda v: v + 1)
        result_msg = mo.md(f"✅ **Moved {moved_count} images to '{target_cat}'.**")

    result_msg
    return


if __name__ == "__main__":
    app.run()
