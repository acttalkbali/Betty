from .storable import Storable, CharField

class Bteam(Storable):
    _table_ = "bteam"

    name = CharField(unique=True)

    def _init_(self, name:str|None=None, id:int|None=None):
        super().__init__(id)
        self.name = name
        self.description = description
