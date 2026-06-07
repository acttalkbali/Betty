from .storable import Storable

class Bettor(Storable):

    def model():
        return {'entity': 'BETTOR',
                'attribute_mapping': [('name', '_name'),
                                      ('nickname', '_nickname'),
                                      ('email', '_email'),
                                      ()]}

    def __init__(self, name, email, nickname, pwd, datastore):
        self._name = name
        self._nickname = nickname
        self._email = email
        self._pwd = pwd
        self._datastore = datastore

    def __str__(self):
        return f'Bettor {self.name} alias {self.nickname}]'

    def __repr__(self):
        return super().__repr__(self)

    def save(self):
        self._datastore.save(cls, self)

    def load(cls, *args, **kwargs):
        return Bettor(self._datastore.load(*args, **kwargs))
