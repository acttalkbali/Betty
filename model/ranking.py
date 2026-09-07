from .storable import Storable, Referenceable, Field, UniqueConstraint
from .bettor import Bettor
from .tournament import Tournament

from datetime import datetime

class Ranking(Storable):
    _table_ = "ranking"
    def __init__(self, store=None, tournament: Tournament|int|None=None, bettor: Bettor|int|None=None, rank:int|None=None, score:int|None=None):
        super().__init__(store)
        self._rank = Field(rank)
        self._bettor = Referenceable(Bettor, bettor)
        self._tournament = Referenceable(Tournament, tournament)
        self._score = Field(score)
        self._unique_constraint = UniqueConstraint(['_bettor', '_tournament'])

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f'Rank({self._tournament.name} {self._rank({self._score})} {self._bettor.name} [{start}]'

    def __repr__(self):
        return super().__repr__()

    # properties -----------------------------------------------------------------

    @property
    def bettor_id(self):
        return self._bettor._id

    @property
    def tournament_id(self):
        return self._tournament._id

    # storable -----------------------------------------------------------------
