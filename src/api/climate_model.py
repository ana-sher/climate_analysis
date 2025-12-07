from fastapi import Depends, Request
from fastapi.routing import APIRouter

from api.limiter import limiter
from api.models.climate_model_dtos import PredictTemp
from api.services.ml_service import MlService

router = APIRouter(prefix="/climate_model", tags=["climate_model"])


def get_ml_service() -> MlService:
    return MlService()


@router.post("/predict-temp", response_model=list[dict])
@limiter.limit("2/minute")
async def predict_temp(request: Request, predict_request: PredictTemp,
                       ml_service: MlService = Depends(get_ml_service)) -> list[dict]:
    return ml_service.predict(
        predict_request.date_from,
        predict_request.date_to,
        predict_request.bbox)
