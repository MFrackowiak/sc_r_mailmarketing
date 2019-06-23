from abc import ABC, abstractmethod
from typing import Dict, List


class AbstractJobRepository(ABC):
    @abstractmethod
    async def create_email_request(self, segment_id: int, template_id: int, name: str):
        pass

    @abstractmethod
    async def get_email_requests(self) -> List[Dict]:
        pass

    @abstractmethod
    async def get_email_request(self, request_id: int) -> Dict:
        pass

    @abstractmethod
    async def get_email_requests_job_statuses(
        self, email_request_id: int
    ) -> List[Dict]:
        pass

    @abstractmethod
    async def update_job_statuses(self, statuses: Dict):
        pass
