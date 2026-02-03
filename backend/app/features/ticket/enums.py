from enum import StrEnum


class PdfStatus(StrEnum):
    PENDING = 'PENDING'
    GENERATING = 'GENERATING'
    READY = 'READY'
    FAILED = 'FAILED'
