import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.middleware import setup_middleware
from api.router import register_routes
from db.indexes import create_indexes
from utils.tracer import configure_logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

setup_middleware(app)
register_routes(app)
create_indexes()
configure_logging()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} → {response.status_code}")
        return response
    except Exception as e:
        logger.exception(f"{request.method} {request.url.path} → 500: {e}")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/health")
def health():
    try:
        from db.mongo import client
        client.admin.command("ping")
        return {"status": "ok", "mongodb": "connected"}
    except Exception as e:
        logger.error(f"MongoDB ping failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "error", "mongodb": str(e)},
        )