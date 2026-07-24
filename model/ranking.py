from .storable import Storable
from .bettor import Bettor
from .tournament import Tournament

from datetime import datetime

class Ranking(Storable):
    _table_ = "ranking"
    def __init__(self, store, tournament: Tournament, bettor: Bettor, rank:int, score:int|None=None):
        super().__init__(store)
        self._rank = rank
        self._bettor = bettor
        self._tournament = tournament
        self._score = score

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

    def load(self, condition=''):
        return self.store_mgr.load(self, f"bettor_id={self.bettor_id} AND tournament_id={self.tournament_id}" + (f" AND {condition}" if condition else ''))

    def save(self):
        self.store_mgr.save(self)
