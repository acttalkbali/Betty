from abc import ABC, abstractmethod

class Storable(ABC):

    def __init__(self, store_mgr):
        super().__init__()
        self._id = None
        self.store_mgr = store_mgr

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value:int|None):
        self._id = value

    @abstractmethod
    def save(self, connection) -> int|None:
        ...

    @abstractmethod
    def load(cls, connection):
        ...



