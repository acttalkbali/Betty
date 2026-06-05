from abc import ABC, abstractmethod

class Storable(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def save(self, connection):
        ...

    @abstractmethod
    def load(cls, connection):
        ...



