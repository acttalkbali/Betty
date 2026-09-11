from .bteam import Bteam
from .storable import Storable, CharField, Many2OneField
from .team import Team


class Bettor(Storable):
    _table_ = "bettor"

    name = CharField(unique=True)
    nickname = CharField(unique=True)
    email = CharField(unique=True)
    pwd = CharField(unique=False) # todo Should not be stored in the DB
    bteam = Many2OneField(target_field=Bteam.id)

    def __init__(self, name=None, pwd=None, email=None, nickname=None, bteam:Bteam|int|None=None, id:int|None=None):
        super().__init__()
        self.name = name
        self.nickname = nickname
        self.email = email
        self.pwd = pwd
        self.bteam = bteam

    def __str__(self):
        return f"Bettor {self.name} alias '{self.nickname}'"

    def __repr__(self):
        return super().__repr__()
