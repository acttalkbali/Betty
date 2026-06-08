from model.storable import Storable

class Phase(Storable):
    def __init__(self, store, name:str, tournament:Tournament):
        super().__init__(store)
        self._name = name
        self._tournament = tournament
        self._tournament_id = tournament._id

    def __str__(self):
        return f'Phase {self._name}'

    def __repr__(self):
        return super().__repr__()

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, v):
        self._name = v or "unnamed" + str(id(self))

    #property
    def tournament_id(self):
        return self._tournament._id

    def load(self, condition = ''):
        self.store_mgr.load(self)

    def save(self):
        self.store_mgr.save(self)
        if self._tournament:
            self.store_mgr.save(self)