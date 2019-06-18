from abc import ABC, abstractmethod
from typing import Tuple, Dict


class AbstractSettingsStorage(ABC):
    @abstractmethod
    async def save_customer_headers(self, headers: Dict):
        pass

    @abstractmethod
    async def get_custom_headers(self) -> Dict:
        pass

    @abstractmethod
    async def get_email_from(self) -> Dict[str, str]:
        pass

    @abstractmethod
    async def save_email_from(self, name: str, email: str):
        pass

    @abstractmethod
    async def save_gateway_credentials(self, username: str, password: str):
        pass

    @abstractmethod
    async def get_gateway_credentials(self) -> Tuple[str, str]:
        pass

    @abstractmethod
    async def get_gateway_credentials_headers_and_from(
        self
    ) -> Tuple[Tuple[str, str], Dict, Dict[str, str]]:
        pass
