from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import sys

from routes.summarize import router as summarize_router
from config import settings

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "logs" / "app.log"),
    ],
)

logger = logging.getLogger(__name__)

# ディレクトリ作成
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.PROCESSING_DIR.mkdir(parents=True, exist_ok=True)

# FastAPIアプリ
app = FastAPI(
    title="YouTube Video Summarizer API",
    description="YouTube動画のサマライザーAPI",
    version="1.0.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーター登録
app.include_router(summarize_router)


@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
