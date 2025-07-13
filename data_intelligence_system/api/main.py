import uvicorn
import os

from data_intelligence_system.utils.logger import get_logger

logger = get_logger(name="API_Main")

def main():
    """
    Entry point for running the FastAPI application using Uvicorn.
    Supports dynamic configuration via environment variables.
    """
    try:
        config = {
            "host": os.getenv("API_HOST", "127.0.0.1"),
            "port": int(os.getenv("API_PORT", 8000)),
            "reload": os.getenv("API_RELOAD", "true").lower() == "true",
            "log_level": os.getenv("API_LOG_LEVEL", "info"),
            "workers": int(os.getenv("API_WORKERS", 1))
        }

        logger.info(f"Starting API with config: {config}")

        uvicorn.run(
            "data_intelligence_system.api.app:app",
            host=config["host"],
            port=config["port"],
            reload=config["reload"],
            log_level=config["log_level"],
            workers=config["workers"]
        )
    except Exception as e:
        logger.exception(f"Error while running the application: {e}")

if __name__ == "__main__":
    main()
