from fastapi import FastAPI

from api.middleware import (
    setup_middleware
)

from api.router import (
    register_routes
)

from db.indexes import (
    create_indexes
)

from utils.tracer import configure_logging


app = FastAPI()


setup_middleware(app)

register_routes(app)

create_indexes()

configure_logging()