from abc import ABC, abstractmethod
from typing import Dict, List, Tuple


class AbstractTemplateRepository(ABC):
    @abstractmethod
    async def create_email_template(
        self, name: str, template: str
    ) -> Tuple[int, List[Dict]]:
        pass

    @abstractmethod
    async def get_email_template(self, template_id: int) -> Dict:
        pass

    @abstractmethod
    async def list_email_templates(self) -> List[Dict]:
        pass
