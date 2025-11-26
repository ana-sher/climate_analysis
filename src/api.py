from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/refresh-data")
async def refresh_data():
    # For now starting with co2 only
    co2_df = read_raw_co2(year_from, lat_min, lat_max, lon_min, lon_max)
