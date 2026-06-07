from abc import ABC, abstractmethod

class Storable(ABC):

    def __init__(self, store_mgr):
        super().__init__()
        self.store_mgr = store_mgr

    @abstractmethod
    def save(self, connection):
        ...

    @abstractmethod
    def load(cls, connection):
        ...



