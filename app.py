from fastapi import FastAPI
from src.routes import setup_routes
from config import get_config
from src.utils.logger import get_logger
from alembic.config import Config
from alembic import command

import multiprocessing

logger = get_logger(__name__)

config = get_config()
app = FastAPI()


def run_migrations():
    """Run database migrations on application startup."""
    try:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to run migrations: {e}")


run_migrations()

setup_routes(app, config)

if __name__ == "__main__":
    import uvicorn

    workers = multiprocessing.cpu_count()
    workers = workers * 2

    logger.info(f"Starting server with {workers} workers")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, workers=workers)
