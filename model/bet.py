from .storable import Storable, UniqueField, Field, DbText, DbFloat, Referenceable
from .bettor import Bettor
from .bettable import Bettable

from datetime import datetime, timezone


class Bet(Storable):

    def __init__(self, store, bettor: Bettor, bettable: Bettable, prediction: int|None=None, score:int|None=None):
        super().__init__(store)
        self._id = UniqueField(self._id)
        self._name = f"{bettor}:{bettable}={prediction}"
        self._bettor = Referenceable(bettor)
        self._bettable = Referenceable(bettable)
        self._prediction = Field(prediction, DbText) # eg. 10=Team_a victory, 01=Team b Victory, 00=Nul, 11=Team_a or Team_b victory, 10=Team_a or nul, 02=Team_b or nul
        self._score = Field(score, DbFloat, required=False)

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
        if self._bettable._start_dt > datetime.now().replace(tzinfo=timezone.utc):
            super().save()
        else:
            print(f"Bet rejected: Bettable has already started ({self._bettable._start_dt})")
