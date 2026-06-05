from Storable import Storable

class Phase(Storable):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def __str__(self):
        return f'Phase {self._name}'

    def __repr__(self):
        return super().__repr__(self)

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, v):
        self._name = v or "unnamed" + str(id(self))
