from abc import abstractmethod, ABC
from typing import List

from web.models.contact import Contact
from web.models.segment import Segment


class AbstractContactService(ABC):
    @abstractmethod
    def create_contact(self, contact: Contact):
        pass

    @abstractmethod
    def get_contact(self, contact_id: int) -> Contact:
        pass

    @abstractmethod
    def read_contacts(self, page: int, per_page: int) -> List[Contact]:
        pass

    @abstractmethod
    def update_contact(self, contact: Contact):
        pass

    @abstractmethod
    def delete_contact(self, contact_id: int):
        pass

    @abstractmethod
    def create_segment(self, segment: Segment):
        pass

    @abstractmethod
    def get_segment(self, segment_id: int) -> Segment:
        pass

    @abstractmethod
    def read_segments(self, page: int, per_page: int) -> List[Contact]:
        pass

    @abstractmethod
    def update_segment(self, segment: Segment):
        pass

    @abstractmethod
    def delete_segment(self, segment_id: int):
        pass

    @abstractmethod
    def list_contacts_in_segment(self, segment_id: int):
        pass

    @abstractmethod
    def add_contact_to_segment(self, segment_id: int, contact_id: int):
        pass

    @abstractmethod
    def remove_contact_from_segment(self, segment_id: int, contact_id: int):
        pass
