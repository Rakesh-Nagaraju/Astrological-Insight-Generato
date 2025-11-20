"""
Main entry point for the Astrological Insight Generator.
Run this file to start the FastAPI server.
"""
import uvicorn
from app.config import Config

if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    )
