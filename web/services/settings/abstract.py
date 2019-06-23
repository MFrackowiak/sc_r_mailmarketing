from abc import ABC, abstractmethod
from typing import Dict


class AbstractSettingsService(ABC):
    @abstractmethod
    async def get_current_settings(self) -> Dict:
        pass

    @abstractmethod
    async def update_settings(self, settings: Dict):
        pass
