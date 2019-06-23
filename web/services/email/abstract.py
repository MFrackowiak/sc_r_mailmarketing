from abc import ABC, abstractmethod
from typing import Dict


class AbstractEmailService(ABC):
    @abstractmethod
    async def send_emails(self, segment_id: int, template_id: int, subject: str):
        pass

    @abstractmethod
    async def get_email_requests(self):
        pass

    @abstractmethod
    async def get_email_request_details(self, job_id: int):
        pass

    @abstractmethod
    async def update_jobs_statuses(self, statuses: Dict):
        pass
