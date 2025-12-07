from pydantic import BaseModel


class BoundingBox(BaseModel):
    lower_left_lon: float
    lower_left_lat: float
    upper_right_lon: float
    upper_right_lat: float
