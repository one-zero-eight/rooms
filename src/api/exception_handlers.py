from fastapi import HTTPException
from fastapi.responses import JSONResponse


# noinspection PyUnusedLocal
async def error_printing(request, exception: HTTPException):
    print(exception)
    return JSONResponse({"detail": exception.detail}, exception.status_code, exception.headers)
