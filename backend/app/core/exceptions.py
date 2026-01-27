class DatabaseError(Exception):
    """Raised when database operations fail."""

    def __init__(self, message: str = 'Database operation failed'):
        self.message = message
        super().__init__(self.message)


class StorageError(Exception):
    """Raised when S3/storage operations fail."""

    def __init__(self, message: str = 'Storage operation failed'):
        self.message = message
        super().__init__(self.message)
