from typing import Dict, List

from web.repositories.contact.abstract import AbstractContactRepository
from web.services.contact.abstract import AbstractContactService


class ContactService(AbstractContactService):
    def __init__(self, contact_repository: AbstractContactRepository):
        self._contact_repository = contact_repository

    async def create_contact(self, contact: Dict) -> Dict:
        return await self._contact_repository.create_contact(contact)

    async def get_contact(self, contact_id: int) -> Dict:
        return await self._contact_repository.get_contact_with_segments(contact_id)

    async def read_contacts(self, page: int, per_page: int) -> List[Dict]:
        return await self._contact_repository.read_contacts(page, per_page)

    async def update_contact(self, contact: Dict):
        await self._contact_repository.update_contact(contact)

    async def delete_contact(self, contact_id: int):
        await self._contact_repository.delete_contact(contact_id)

    async def create_segment(self, segment: Dict) -> Dict:
        return await self._contact_repository.create_segment(segment)

    async def get_segment(self, segment_id: int) -> Dict:
        return await self._contact_repository.get_segment(segment_id)

    async def read_segments(self, page: int, per_page: int) -> List[Dict]:
        return await self._contact_repository.read_segments(page, per_page)

    async def update_segment(self, segment: Dict):
        await self._contact_repository.update_segment(segment)

    async def delete_segment(self, segment_id: int):
        await self._contact_repository.delete_segment(segment_id)

    async def list_contacts_in_segment(self, segment_id: int):
        return await self._contact_repository.list_contacts_in_segment(segment_id)

    async def add_contact_to_segment(self, segment_id: int, contact_id: int):
        await self._contact_repository.add_contact_to_segment(segment_id, contact_id)

    async def remove_contact_from_segment(self, segment_id: int, contact_id: int):
        await self._contact_repository.remove_contact_from_segment(
            segment_id, contact_id
        )
