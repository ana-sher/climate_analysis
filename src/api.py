from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.data import read_raw_co2
from src.utils.location import get_location

app = FastAPI(
    title="Climate Analysis API",
    openapi_url="/api",
    docs_url="/api.html",
    description="API for climate data analysis and visualization.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/refresh-data/")
async def refresh_data(year_range: int = 4, loc_range: int = 5):
    utc_now = datetime.now(timezone.utc)
    year_from = utc_now.year - year_range

    lon, lat = get_location()

    lat_min = lat - loc_range
    lat_max = lat + loc_range
    lon_min = lon - loc_range
    lon_max = lon + loc_range
    # For now starting with co2 only
    co2_df = read_raw_co2(year_from, lat_min, lat_max, lon_min, lon_max)
