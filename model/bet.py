from .storable import Storable
from .bettor import Bettor
from .bettable import Bettable

from datetime import datetime, timezone


class Bet(Storable):

    def __init__(self, store, bettor: Bettor, bettable: Bettable, prediction: int|None=None, score:int|None=None):
        super().__init__(store)
        self._name = f"{bettor}:{bettable}={prediction}"
        self._bettor = bettor
        self._bettable = bettable
        self._prediction = prediction # eg. 10=Team_a victory, 01=Team b Victory, 00=Nul, 11=Team_a or Team_b victory, 10=Team_a or nul, 02=Team_b or nul
        self._score = score

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
        conditions = []
        if self.id:
            conditions.append(self.store.wrap_condition('id', '=', self.id))
        else:
            if self._bettor:
                conditions.append(self.store.wrap_condition('bettor_id', '=', self.bettor_id))
            if self._bettable:
                conditions.append(self.store.wrap_condition('bettable_id', '=', self.bettable_id))
        result = self.store_mgr.load(type(self), ' AND '.join(conditions))
        if len(result)==1:
            self._prediction = result[0]['prediction']
            self._score = result[0]['score']
            self._id = result[0]['id']
        return result

    def save(self):
        if self._bettable._start_dt < datetime.now().replace(tzinfo=timezone.utc):
            self.store_mgr.save(self)
