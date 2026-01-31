import enum


class PdfStatus(enum.StrEnum):
    """Represents the status of a ticket PDF generation."""

    PENDING = 'PENDING'
    GENERATING = 'GENERATING'
    READY = 'READY'
    FAILED = 'FAILED'
