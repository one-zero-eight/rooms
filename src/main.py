import uvicorn
from fastapi import FastAPI, HTTPException

from src.api.routes.bot import bot_router
from src.api.exception_handlers import error_printing

app = FastAPI()

app.add_exception_handler(HTTPException, error_printing)

app.include_router(bot_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
