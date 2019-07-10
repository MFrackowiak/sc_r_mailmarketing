from enum import Enum


class EmailResult(Enum):
    SUCCESS = "success"
    AUTH_FAILURE = "auth_failure"
    FAILURE = "failure"
    RECOVERABLE_FAILURE = "retry"
    PENDING = "pending"
