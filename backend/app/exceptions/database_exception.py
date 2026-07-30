class DatabaseException(Exception):
    def __init__(self, message: str, original: Exception | None = None):
        self.original = original
        super().__init__(f"Database error: {message}")


class InvalidDataException(DatabaseException):
    def __init__(self, message: str):
        super().__init__(f"Invalid data: {message}")
