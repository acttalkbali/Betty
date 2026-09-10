from model.storable import Storable, Field, CharField, Many2OneField
from model.tournament import Tournament


class Phase(Storable):
    # Model -----------------------------------------------------------------
    _table_ = "phase"

    name = CharField()
    tournament = Many2OneField(Tournament.id)
    state = CharField(required=True)
    scoring = CharField()

    def __init__(self, name:str='', tournament:Tournament|int=None, state:str='', scoring:str=''):
        super().__init__()
        self.name = name
        self.tournament = tournament
        self.state = state
        self.scoring = scoring

    def __str__(self):
        return f'Phase {self.name}'

    def __repr__(self):
        return super().__repr__()