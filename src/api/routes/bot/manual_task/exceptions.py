from fastapi import status

from src.api.exceptions import MyException


class ManualTaskIsInactiveException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 121, "The manual task is inactive")
