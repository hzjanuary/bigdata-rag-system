class RagError(Exception):
    """Public errors contain a fixed code, never exception strings or input data."""

    def __init__(self, code: str, status: int = 400):
        self.code = code
        self.status = status
        super().__init__(code)
