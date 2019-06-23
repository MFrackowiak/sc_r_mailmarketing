from abc import ABC, abstractmethod
from typing import List, Dict

from common.enums import EmailResult


class AbstractWebClient(ABC):
    @abstractmethod
    async def report_job_status(self, statuses: Dict[EmailResult, List[int]]):
        pass
