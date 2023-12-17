import uvicorn
from fastapi import FastAPI

from src.api.routes.bot import bot_router

app = FastAPI()

app.include_router(bot_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
