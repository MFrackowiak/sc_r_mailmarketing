from abc import abstractmethod, ABC
from typing import Dict, List


class AbstractEmailClient(ABC):
    @abstractmethod
    async def get_custom_headers_and_email_from(self) -> Dict:
        pass

    @abstractmethod
    async def update_email_client_settings(self, settings: Dict):
        pass

    @abstractmethod
    async def schedule_mailing_jobs(
        self, jobs: List[Dict], template: str, subject: str
    ):
        pass
