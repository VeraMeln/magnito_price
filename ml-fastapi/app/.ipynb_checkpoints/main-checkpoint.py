from fastapi import FastAPI
from pydantic import BaseModel
from model.model import pipeline, model
from model.model import __version__ as model_version
import model.magnito_price
import uvicon

app = FastAPI()


class ItemIn(BaseModel):
	district:str
	adress: str
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
def predict(features: ItemIn):
	features = features.dict()
	print(features)
	district = features['district']
	adress = features['adress']
	floor = features['floor']
	total_square = features['total_square']
	living_square = features['living_square']
	kitchen_square = features['kitchen_square']
	price = predict_pipeline([[district, adress, floor, total_square, living_square, kitchen_square]])
	return {"price": price}

if __name__ == '__main__':
	uvicorn.run(app, host='127.0.0.1', port=8000)