from datetime import datetime

from fastapi.routing import APIRouter

from dtos import BoundingBox
from model.predict import predict_for_region
from model.train import load_latest_model

router = APIRouter()


@router.get("/climate-model/info")
async def get_climate_model_info():
    return {
        "model": "Climate Analysis Model",
        "version": "1.0",
        "description": "API endpoint for climate model information."
    }


@router.post("/climate-model/predict-temp", response_model=list[dict])
async def predict_temp(date_from: str, date_to: str, bbox: BoundingBox):
    model = load_latest_model()
    lat_min = bbox.lower_left_lat if bbox.lower_left_lat < bbox.upper_right_lat else bbox.upper_right_lat
    lat_max = bbox.upper_right_lat if bbox.upper_right_lat > bbox.lower_left_lat else bbox.lower_left_lat
    lon_min = bbox.lower_left_lon if bbox.lower_left_lon < bbox.upper_right_lon else bbox.upper_right_lon
    lon_max = bbox.upper_right_lon if bbox.upper_right_lon > bbox.lower_left_lon else bbox.lower_left_lon

    prediction_df = predict_for_region(model, lat_min, lat_max, lon_min, lon_max, datetime.fromisoformat(date_from),
                                       datetime.fromisoformat(date_to))
    return prediction_df.to_dict(orient="records")
