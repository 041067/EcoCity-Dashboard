class ExternalApiException(Exception):
    def __init__(self, service: str, message: str, status_code: int | None = None):
        self.service = service
        self.status_code = status_code
        super().__init__(f"{service} API error: {message} (status={status_code})")
