from .storable import Storable, IntegerField, Many2OneField, FloatField, UniqueConstraint
from .bettor import Bettor
from .tournament import Tournament

from datetime import datetime

class Ranking(Storable):
    # Model -----------------------------------------------------------------
    _table_ = "ranking"

    rank = IntegerField()
    bettor = Many2OneField(Bettor.id)
    tournament = Many2OneField(Tournament.id)
    score = FloatField()

    constraint = UniqueConstraint([bettor, tournament])

    # -----------------------------------------------------------------------

    def __init__(self, tournament: Tournament|int=None, bettor: Bettor|int=None, rank:int|None=None, score:int|None=None):
        super().__init__()
        self.rank = rank
        self.bettor = bettor
        self.tournament = tournament
        self.score = score
        #self._unique_constraint = UniqueConstraint(['_bettor', '_tournament'])

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f'Rank({self.tournament.name} {self.rank({self.score})} {self.bettor.name} [{start}]'

    def __repr__(self):
        return super().__repr__()

    # properties -----------------------------------------------------------------

    @property
    def bettor_id(self):
        return self.bettor._id

    @property
    def tournament_id(self):
        return self.tournament._id

    # storable -----------------------------------------------------------------
