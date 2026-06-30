import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import uvicorn
from backend.database import init_db
from backend.api import router as api_router
from backend.bot import start_bot, stop_bot, player
from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"

app_settings = AppSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    bot_task = asyncio.create_task(start_bot())
    yield
    await stop_bot()
    bot_task.cancel()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

frontend_dist = Path("frontend/dist")
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

def main():
    uvicorn.run(
        "backend.main:app",
        host=app_settings.host,
        port=app_settings.port,
        reload=True
    )

if __name__ == "__main__":
    main()
