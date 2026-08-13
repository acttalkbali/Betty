from model.storable import Storable, Field, UniqueField, Referenceable, DbText
from model.tournament import Tournament


class Phase(Storable):
    _table_ = "phase"
    """
    id SERIAL PRIMARY KEY,
    {cls.references_by_id(Tournament)},
    name TEXT,
    state TEXT NOT NULL,
    scoring TEXT
    """
    def __init__(self, store, name:str, tournament:Tournament, state:str='', scoring:str=''):
        super().__init__(store)
        self._name = Field(name, DbText)
        self._tournament = Referenceable(Tournament, tournament)
        #self._tournament_id = tournament._id
        self._state = Field(state, DbText)
        self._scoring = Field(scoring, DbText)

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

    def tournament_id(self):
        return self._tournament.id
