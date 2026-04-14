class ProviderError(Exception):
    pass


class ProviderNotSupportedError(ProviderError):
    pass


class ProviderTimeoutError(ProviderError):
    pass


class ProviderHTTPError(ProviderError):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
