from .storable import Storable, Field, DbText, UniqueField


class Bettor(Storable):
    _table_ = "bettor"

    def __init__(self, store, name, pwd=None, email=None, nickname=None, id=None):
        super().__init__(store, id)
        self._name = Field(name, DbText)
        self._nickname = UniqueField(nickname, DbText)
        self._email = UniqueField(email, DbText)
        self._pwd = Field(pwd, DbText)

    def __str__(self):
        return f"Bettor {self._name} alias '{self._nickname}'"

    def __repr__(self):
        return super().__repr__()

    #@classmethod
    #def load(cls, condition = ''):
    #    self.store_mgr.load(cls, condition)

    def load(self, condition = ''):
        return super().load(condition)
        """
        # todo use the mini model mapping to hide the attribute names
        if self.id:
            condition += self.store.wrap_condition('id', '=', self.id)
        elif self._name:
            condition += self.store.wrap_condition('name', '=', self._name)
        results = self.store_mgr.load(type(self), condition)
        if len(results)==1:
            self._name = results[0]['name']
            self._id = results[0]['id']
            self._email = results[0]['email']
            self._pwd = results[0]['pwd']
            self._nickname = results[0]['nickname']
            print(f"Filled {self}")
        """

    def save(self):
        super().save()
        #self.store_mgr.save(self)


