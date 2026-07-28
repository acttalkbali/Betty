from .storable import Storable, Field, DbText, UniqueField


class Bettor(Storable):
    _table_ = "bettor"

    def __init__(self, store, name, pwd=None, email=None, nickname=None, id:int|None=None):
        super().__init__(store)
        self._name = UniqueField(name, DbText)
        self._nickname = UniqueField(nickname, DbText)
        self._email = UniqueField(email, DbText)
        self._pwd = Field(pwd, DbText)

    def __str__(self):
        return f"Bettor {self._name} alias '{self._nickname}'"

    def __repr__(self):
        return super().__repr__()

    def load(self, condition = ''):
        return super().load(condition)




