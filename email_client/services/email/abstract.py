from abc import ABC, abstractmethod
from typing import Dict, List, Generator, Tuple, Optional


class AbstractSendEmailService(ABC):
    @abstractmethod
    def dispatch_sending_emails(self, jobs: List[Dict], template: str):
        pass

    @abstractmethod
    def send_emails(self, jobs: List[Dict], template: str, retry_attempt: int = 0):
        pass

    @abstractmethod
    def send_email_batch(
        self,
        jobs_batch: List[Dict],
        template: str,
        auth: Tuple[str, str],
        headers: Optional[Dict],
        email_from: Dict[str, str],
    ) -> List[Dict]:
        pass

    @abstractmethod
    def _split_to_batches(
        self, to_split: List, batch_size: int
    ) -> Generator[List, None, None]:
        pass

    @abstractmethod
    async def manage_retry(self, jobs: List[Dict], template: str, retry_attempt: int):
        pass
