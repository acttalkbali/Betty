from .storable import Storable
from .bettor import Bettor
from .bettable import Bettable

from datetime import datetime

class Bet(Storable):

    def __init__(self, store, bettor: Bettor, bettable: Bettable, prediction: int):
        super().__init__(store)
        self._name = f"{bettor}:{bettable}={prediction}"
        self._bettor = bettor
        self._bettable = bettable
        self._prediction = prediction # eg. 10=Team_a victory, 01=Team b Victory, 00=Nul, 11=Team_a or Team_b victory, 10=Team_a or nul, 02=Team_b or nul

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f'Bettable {self._team_a.name} - {self._team_b.name} [{start}]'

    def __repr__(self):
        return super().__repr__()

    # properties -----------------------------------------------------------------

    @property
    def bettor_id(self):
        return self._bettor._id

    @property
    def bettable_id(self):
        return self._bettable._id

    # storable -----------------------------------------------------------------

    def load(self, condition=''):
        return self.store_mgr.load(self, f"bettor_id={self.bettor_id} AND bettable_id={self.bettable_id}" + (f" AND {condition}" if condition else ''))

    def save(self):
        if self.bettable._start_dt < datetime.now():
            self.store_mgr.save(self)
