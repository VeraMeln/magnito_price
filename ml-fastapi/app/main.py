from fastapi import FastAPI
from pydantic import BaseModel
from app.model.model import pipeline, model
from app.model.model import __version__ as model_version

app = FastAPI()


class ItemIn(BaseModel):
	district:str
	adress: district
	floor: str
	total_square: float
	living_square:float
	kitchen_square: float


class PredictionOut(BaseModel):
    price: int


@app.get("/")
def home():
    return {"health_check": "OK", "model_version": model_version}


@app.post("/predict", response_model=PredictionOut)
def predict(payload: ItemIn):
    price = predict_pipeline(payload)
    return {"price": price}