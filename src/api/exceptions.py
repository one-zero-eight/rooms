from fastapi import HTTPException, status


class MyException(HTTPException):
    def __init__(self, http_code: int, code: int, details: str):
        super().__init__(http_code, {"code": code, "detail": details})


"""
Token errors
"""


class NoTokenException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, 1, "No access token provided")


class InvalidTokenException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, 2, "Invalid access token")


class TokenExpiredException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_401_UNAUTHORIZED, 3, "Access token has expired")


"""
Access errors
"""


class TelegramBotAccessException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_403_FORBIDDEN, 11, "Invalid token for bot's access")


"""
API errors
"""


class UserExistsException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 101, "The user already exists")


class UserNotExistException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 102, "The user does not exist")


class RoomExistsException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 103, "The room already exists")


class RoomNotExistException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 104, "The room does not exist")


class UserWithoutRoomException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 105, "The user does not have a room")


class UserHasRoomException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 106, "The user already has a room")


class OrderNotExistException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 107, "The order does not exist")


class TaskNotExistException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 108, "The task does not exist")


class TooManyInvitationsException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 109, "Maximum number of invitations is reached for the user")


class InvitationAlreadySentException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 110, "Such an invitation is already sent")


class InvitationNotExistException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 111, "The invitation is not found")


class NotYoursInvitationException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 112, "The invitation is not addressed to this user")


class TooManyOrdersException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 113, "Maximum number of orders is reached for the room")


class TooManyTasksException(MyException):
    def __init__(self):
        super().__init__(status.HTTP_400_BAD_REQUEST, 114, "Maximum number of tasks is reached for the room")


class SpecifiedUserNotInRoomException(MyException):
    def __init__(self, user_id: int):
        super().__init__(status.HTTP_400_BAD_REQUEST, 115, f"The user {user_id} does not belong to the room")


class SpecifiedUserNotExistException(MyException):
    def __init__(self, user_id: int):
        super().__init__(status.HTTP_400_BAD_REQUEST, 116, f"The user {user_id} does not exist")


class WrongRoomException(MyException):
    def __init__(self, obj: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, 117, f"The {obj} does not belong to the room")
