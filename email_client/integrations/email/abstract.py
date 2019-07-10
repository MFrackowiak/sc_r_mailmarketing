from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional


class AbstractEmailGatewayClient(ABC):
    @abstractmethod
    async def send_emails(
        self,
        jobs: List[Dict],
        template: str,
        subject: str,
        auth: Tuple[str, str],
        email_from: Dict[str, str],
        headers: Optional[Dict] = None,
    ) -> Tuple[Dict, List[Dict]]:
        pass
