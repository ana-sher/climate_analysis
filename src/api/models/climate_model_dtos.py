from pydantic import BaseModel

from api.models.bounding_box import BoundingBox


class PredictTemp(BaseModel):
    date_from: str
    date_to: str
    bbox: BoundingBox