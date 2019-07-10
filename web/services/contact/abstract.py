from abc import abstractmethod, ABC
from typing import List, Dict, Optional


class AbstractContactService(ABC):
    @abstractmethod
    async def create_contact(self, contact: Dict):
        pass

    @abstractmethod
    async def get_contact(self, contact_id: int) -> Dict:
        pass

    @abstractmethod
    async def read_contacts(self, page: int, per_page: int) -> List[Dict]:
        pass

    @abstractmethod
    async def update_contact(self, contact: Dict):
        pass

    @abstractmethod
    async def delete_contact(self, contact_id: int):
        pass

    @abstractmethod
    async def create_segment(self, segment: Dict):
        pass

    @abstractmethod
    async def get_segment(self, segment_id: int) -> Dict:
        pass

    @abstractmethod
    async def read_segments(self, page: int, per_page: Optional[int]) -> List[Dict]:
        pass

    @abstractmethod
    async def update_segment(self, segment: Dict):
        pass

    @abstractmethod
    async def delete_segment(self, segment_id: int):
        pass

    @abstractmethod
    async def list_contacts_in_segment(self, segment_id: int):
        pass

    @abstractmethod
    async def add_contact_to_segment(self, segment_id: int, contact_id: int):
        pass

    @abstractmethod
    async def remove_contact_from_segment(self, segment_id: int, contact_id: int):
        pass

    @abstractmethod
    async def get_contacts_pages_count(self, per_page: int) -> int:
        pass

    @abstractmethod
    async def get_segments_pages_count(self, per_page: int) -> int:
        pass
