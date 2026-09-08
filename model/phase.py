from model.storable import Storable, Field, CharField, Many2OneField
from model.tournament import Tournament


class Phase(Storable):
    # Model -----------------------------------------------------------------
    _table_ = "phase"

    name = CharField()
    tournament = Many2OneField(Tournament.id)
    state = CharField(required=True)
    scoring = CharField()

    """
    id SERIAL PRIMARY KEY,
    {cls.references_by_id(Tournament)},
    name TEXT,
    state TEXT NOT NULL,
    scoring TEXT
    """
    def __init__(self, name:str='', tournament:Tournament|int=None, state:str='', scoring:str=''):
        super().__init__()
        self.name = name
        self.tournament = tournament
        #self._tournament_id = tournament._id
        self.state = state
        self.scoring = scoring

    def __str__(self):
        return f'Phase {self.name}'

    def __repr__(self):
        return super().__repr__()

    # @property
    # def name(self):
    #    return self.name
    # @name.setter
    # def name(self, v):
    #    self.name = v or "unnamed" + str(id(self))

    def tournament_id(self):
        return self.tournament.id
