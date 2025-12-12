import marimo

__generated_with = "0.18.3"
app = marimo.App()


@app.cell
def imports():
    import marimo as mo
    # Explicit imports replacing 'from fastai2.vision.all import *'
    from fastai.vision.all import (
        untar_data, URLs, ImageDataLoaders, get_image_files, Resize,
        cnn_learner, resnet34, error_rate, PILImage,
        SegmentationDataLoaders, unet_learner, vision_learner,
        defaults, ProgressCallback
    )
    # Explicit imports replacing 'from fastai2.text.all import *'
    from fastai.text.all import (
        TextDataLoaders, text_classifier_learner, AWD_LSTM, accuracy
    )
    # Explicit imports replacing 'from fastai2.tabular.all import *'
    from fastai.tabular.all import (
        TabularDataLoaders, Categorify, FillMissing, Normalize, tabular_learner
    )
    # Explicit imports replacing 'from fastai2.collab import *'
    from fastai.collab import CollabDataLoaders, collab_learner

    import numpy as np
    from types import SimpleNamespace

    # 'from utils import *' is not supported. 
    # If you have a utils.py, import specific functions here.
    # We define a mock 'gv' function here since it is used in the notebook
    try:
        import graphviz
        def gv(s): return graphviz.Source(s)
    except ImportError:
        def gv(s): return "Graphviz not installed"
    return (
        AWD_LSTM,
        Categorify,
        CollabDataLoaders,
        FillMissing,
        ImageDataLoaders,
        Normalize,
        PILImage,
        ProgressCallback,
        Resize,
        SegmentationDataLoaders,
        SimpleNamespace,
        TabularDataLoaders,
        TextDataLoaders,
        URLs,
        accuracy,
        collab_learner,
        defaults,
        error_rate,
        get_image_files,
        gv,
        mo,
        np,
        resnet34,
        tabular_learner,
        text_classifier_learner,
        unet_learner,
        untar_data,
        vision_learner,
    )


@app.cell
def intro_markdown(mo):
    mo.md("""
    # Your deep learning journey
    ## Deep learning is for everyone
    ## Neural networks: a brief history
    ## What you will learn
    ## Who we are
    ## How to learn deep learning
    ## Your projects and your mindset
    ## The software: PyTorch, fastai, and Jupyter (and why it doesn't matter)
    ## Your first model
    ### Getting a GPU deep learning server
    ### Running your first notebook
    """)
    return


@app.cell
def train_cat_model(
    ImageDataLoaders,
    ProgressCallback,
    Resize,
    URLs,
    defaults,
    error_rate,
    get_image_files,
    resnet34,
    untar_data,
    vision_learner,
):
    # Explicit imports instead of wildcard (*)
    # from fastai.vision.all import (
    #     untar_data, 
    #     URLs, 
    #     ImageDataLoaders, 
    #     get_image_files, 
    #     Resize, 
    #     vision_learner, 
    #     resnet34, 
    #     error_rate,
    #     defaults,
    #     ProgressCallback
    # )

    # 1. Disable the progress bar globally for this session
    # We filter out the ProgressCallback from defaults
    defaults.callbacks = [c for c in defaults.callbacks if not isinstance(c, ProgressCallback)]

    path = untar_data(URLs.PETS)/'images'

    def is_cat(x): return x[0].isupper()

    files = get_image_files(path)
    subset_files = files[:500]

    dls = ImageDataLoaders.from_name_func(
        path, subset_files, valid_pct=0.2, seed=42,
        label_func=is_cat, item_tfms=Resize(224), bs=128)

    # 2. Use vision_learner (modern replacement for cnn_learner)
    learn = vision_learner(dls, resnet34, metrics=error_rate)

    learn.fine_tune(1)
    return (learn,)


@app.cell
def sidebar_math(mo):
    mo.md("### Sidebar: This book was written in Jupyter Notebooks")
    1+1
    return


@app.cell
def show_thumb(PILImage):
    # Note: Ensure 'images/chapter1_cat_example.jpg' exists locally
    try:
        img = PILImage.create('images/chapter1_cat_example.jpg')
        thumb = img.to_thumb(192)
    except FileNotFoundError:
        thumb = "Image not found"
    return


@app.cell
def fake_upload(SimpleNamespace):
    #hide
    # For the book, we can't actually click an upload button, so we fake it
    uploader = SimpleNamespace(data = ['images/chapter1_cat_example.jpg'])
    return (uploader,)


@app.cell
def predict_cat(PILImage, learn, uploader):
    try:
        img_pred = PILImage.create(uploader.data[0])
        is_cat_pred,_,probs = learn.predict(img_pred)
        print(f"Is this a cat?: {is_cat_pred}; Probability it's a cat: {probs[1].item():.6f}")
    except Exception as e:
        print(f"Could not predict: {e}")
    return


@app.cell
def ml_diagrams(gv, mo):
    mo.md("### What is machine learning?")
    d1 = gv('''program[shape=box3d width=1 height=0.7]
    inputs->program->results''')

    d2 = gv('''model[shape=box3d width=1 height=0.7]
    inputs->model->results; weights->model''')

    d3 = gv('''ordering=in
    model[shape=box3d width=1 height=0.7]
    inputs->model->results; weights->model; results->performance
    performance->weights[constraint=false label=update]''')

    d4 = gv('''model[shape=box3d width=1 height=0.7]
    inputs->model->results''')
    return


@app.cell
def dl_jargon(gv, mo):
    mo.md(
        """
        ### What is a neural network?
        ### A bit of deep learning jargon
        """
    )
    d5 = gv('''ordering=in
    model[shape=box3d width=1 height=0.7 label=architecture]
    inputs->model->predictions; parameters->model; labels->loss; predictions->loss
    loss->parameters[constraint=false label=update]''')
    return


@app.cell
def segmentation_model(
    SegmentationDataLoaders,
    URLs,
    get_image_files,
    np,
    resnet34,
    unet_learner,
    untar_data,
):
    def _():
        # Deep learning is not just for image classification
        path_cam = untar_data(URLs.CAMVID_TINY)
        files = get_image_files(path_cam/"images")[:30]  # Subset
        # files = get_image_files(path_cam/"images")

        dls_cam = SegmentationDataLoaders.from_label_func(
            path_cam, bs=16,  # Larger batch
            fnames=files,
            label_func = lambda o: path_cam/'labels'/f'{o.stem}_P{o.suffix}',
            codes = np.loadtxt(path_cam/'codes.txt', dtype=str),
            num_workers=4  # Parallel loading
        )
        learn_cam = unet_learner(dls_cam, resnet34)
        learn_cam.fine_tune(6)  # Train it (no return here)
        return learn_cam  # Return the learner object


    learn_cam = _()
    return (learn_cam,)


@app.cell
def show_seg_results(learn_cam):
    import matplotlib.pyplot as plt

    # Turn off interactive plotting to prevent automatic display
    plt.ioff()

    # Generate the results
    learn_cam.show_results(max_n=6, figsize=(7, 8))

    # Capture the figure
    results_fig = plt.gcf()

    # Turn interactive mode back on (optional, but good practice)
    plt.ion()

    # Display in Marimo
    results_fig
    return


@app.cell
def text_model(
    AWD_LSTM,
    TextDataLoaders,
    URLs,
    accuracy,
    text_classifier_learner,
    untar_data,
):
    dls_text = TextDataLoaders.from_folder(untar_data(URLs.IMDB), valid='test')
    learn_text = text_classifier_learner(dls_text, AWD_LSTM, drop_mult=0.5, metrics=accuracy)
    learn_text.fine_tune(4, 1e-2)
    return (learn_text,)


@app.cell
def predict_text(learn_text):
    learn_text.predict("I really liked that movie!")
    return


@app.cell
def tabular_model(
    Categorify,
    FillMissing,
    Normalize,
    TabularDataLoaders,
    URLs,
    accuracy,
    tabular_learner,
    untar_data,
):
    path_tab = untar_data(URLs.ADULT_SAMPLE)

    dls_tab = TabularDataLoaders.from_csv(path_tab/'adult.csv', path_tab, y_names="salary",
        cat_names = ['workclass', 'education', 'marital-status', 'occupation',
                     'relationship', 'race'],
        cont_names = ['age', 'fnlwgt', 'education-num'],
        procs = [Categorify, FillMissing, Normalize])

    learn_tab = tabular_learner(dls_tab, metrics=accuracy)
    learn_tab.fit_one_cycle(3)
    return


@app.cell
def collab_model(CollabDataLoaders, URLs, collab_learner, untar_data):
    path_collab = untar_data(URLs.ML_SAMPLE)
    dls_collab = CollabDataLoaders.from_csv(path_collab/'ratings.csv')
    learn_collab = collab_learner(dls_collab, y_range=(0.5,5.5))
    learn_collab.fine_tune(10)
    return (learn_collab,)


@app.cell
def show_collab_results(learn_collab):
    learn_collab.show_results()
    return


if __name__ == "__main__":
    app.run()
