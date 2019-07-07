from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class AbstractEmailService(ABC):
    @abstractmethod
    async def send_emails(
        self, segment_id: int, template_id: int, subject: str
    ) -> Tuple[Dict, str]:
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

    @abstractmethod
    async def list_email_templates(self) -> List[Dict]:
        pass

    @abstractmethod
    async def get_email_template(self, template_id: int) -> Dict:
        pass

    @abstractmethod
    async def update_email_template(self, template: Dict):
        pass

    @abstractmethod
    async def create_email_template(self, template: Dict) -> Dict:
        pass
