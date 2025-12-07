import model.train
from model.predict import predict_for_region
from datetime import datetime
from api.models.bounding_box import BoundingBox


class MlService:
    def __init__(self):
        self.model = model.train.load_latest_model()

    def predict(self, date_from: str, date_to: str, bbox: BoundingBox) -> list[dict]:
        lat_min = bbox.lower_left_lat if bbox.lower_left_lat < bbox.upper_right_lat else bbox.upper_right_lat
        lat_max = bbox.upper_right_lat if bbox.upper_right_lat > bbox.lower_left_lat else bbox.lower_left_lat
        lon_min = bbox.lower_left_lon if bbox.lower_left_lon < bbox.upper_right_lon else bbox.upper_right_lon
        lon_max = bbox.upper_right_lon if bbox.upper_right_lon > bbox.lower_left_lon else bbox.lower_left_lon

        prediction_df = predict_for_region(self.model, lat_min, lat_max, lon_min, lon_max,
                                           datetime.fromisoformat(date_from),
                                           datetime.fromisoformat(date_to))
        return prediction_df.to_dict(orient="records")
