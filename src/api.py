from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from titiler.core.factory import TilerFactory
from src.api import climate_model
from api.core.logging import setup_logging

from src.utils.location import get_location

setup_logging()
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

cog = TilerFactory()

app.include_router(cog.router, tags=["Cloud Optimized GeoTIFF"])
app.include_router(climate_model.router, tags=["Climate Model API"])
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def root():
    return {"message": "Service is up and running."}


@app.get("/health")
async def health():
    return Response(status_code=200)

# handler = Mangum(
#     app
# )
