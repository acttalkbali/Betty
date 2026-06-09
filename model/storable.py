from abc import ABC, abstractmethod

class Storable(ABC):

    def __init__(self, store_mgr, id=None):
        super().__init__()
        self._id = id or None
        self.store_mgr = store_mgr

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value:int|None):
        self._id = value

    @property
    def store(self):
        return self.store_mgr.get_store()

    def load(self, condition = ''):
        self.store_mgr.load(self)

    def save(self):
        self.store_mgr.save(self)


