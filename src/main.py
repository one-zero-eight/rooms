import os
import time

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.openapi.utils import get_openapi
from starlette.responses import RedirectResponse

from src.api.routes.bot import bot_router
from src.api.exception_handlers import error_printing

app = FastAPI()

app.add_exception_handler(HTTPException, error_printing)

app.include_router(bot_router)


@app.get("/")
def docs_redirect():
    return RedirectResponse("/docs")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="InNoHassle-Rooms API",
        version="0.1.0",
        routes=app.routes,
    )
    for route in openapi_schema["paths"].values():
        for v in route.values():
            v["operationId"] = v["summary"].lower().replace(" ", "_")
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


os.environ["TZ"] = "Europe/Moscow"
time.tzset()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
