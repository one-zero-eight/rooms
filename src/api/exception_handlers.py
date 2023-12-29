from fastapi.responses import JSONResponse

from src.api.exceptions import MyException


# noinspection PyUnusedLocal
async def error_printing(request, exception: MyException):
    print(exception)
    return JSONResponse(exception.detail, exception.status_code, exception.headers)
