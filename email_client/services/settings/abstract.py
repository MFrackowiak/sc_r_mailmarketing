from abc import abstractmethod, ABC
from typing import Dict


class AbstractSettingsService(ABC):
    @abstractmethod
    async def get_custom_headers_and_email_from(self) -> Dict:
        pass

    @abstractmethod
    async def update_email_credentials(self, user: str, password: str):
        pass

    @abstractmethod
    async def update_custom_headers(self, headers: Dict):
        pass

    @abstractmethod
    async def update_email_from(self, name: str, email: str):
        pass
