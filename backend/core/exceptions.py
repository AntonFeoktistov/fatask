from fastapi import HTTPException, status


class UserAlreadyExistsException(HTTPException):
    def __init__(
        self,
        detail: str = "User with this email/username already exists",
        status_code: int = status.HTTP_409_CONFLICT,
    ):
        super().__init__(status_code=status_code, detail=detail)


class TaskAlreadyExistsException(HTTPException):
    def __init__(
        self,
        detail: str = "Such task is already exists in users task-list",
        status_code: int = status.HTTP_409_CONFLICT,
    ):
        super().__init__(status_code=status_code, detail=detail)
