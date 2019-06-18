from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Tuple, Optional


class EmailResult(Enum):
    SUCCESS = "success"
    AUTH_FAILURE = "auth_failure"
    FAILURE = "failure"
    RECOVERABLE_FAILURE = "retry"


class AbstractEmailGatewayClient(ABC):
    @abstractmethod
    async def send_emails(
        self,
        jobs: List[Dict],
        template: str,
        auth: Tuple[str, str],
        email_from: Dict[str, str],
        headers: Optional[Dict] = None,
    ) -> Tuple[Dict, List[Dict]]:
        pass
