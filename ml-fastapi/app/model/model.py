import pickle
import re
from pathlib import Path
import pandas as pd

__version__ = "1.0"

BASE_DIR = Path(__file__).resolve(strict=True).parent


with open(f"{BASE_DIR}/pipeline-{__version__}.pkl", "rb") as f:
    pipeline = pickle.load(f)


with open(f"{BASE_DIR}/model-{__version__}.pkl", "rb") as f:
    model = pickle.load(f)


def predict_pipeline(item):
    item.to_frame().T
    pipeline.transform(item)
    pred = model.predict([pipeline.transform(item)])
    return pred