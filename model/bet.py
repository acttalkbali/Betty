from .storable import Storable, UniqueField, Field, DbText, DbFloat, Referenceable, UniqueConstraint
from .bettor import Bettor
from .bettable import Bettable

from datetime import datetime, timezone


class Bet(Storable):

    def __init__(self, store=None, bettor: Bettor|int=None, bettable: Bettable|int=None, prediction: int|None=None, score:int|None=None):
        super().__init__(store)
        self._name = f"{bettor}:{bettable}={prediction}"
        self._bettor = Referenceable(Bettor, bettor)
        self._bettable = Referenceable(Bettable, bettable)
        self._prediction = Field(prediction, DbText) # eg. 10=Team_a victory, 01=Team b Victory, 00=Nul, 11=Team_a or Team_b victory, 10=Team_a or nul, 02=Team_b or nul
        self._score = Field(score, DbFloat, required=False)
        self._bettor_bettable_unicity = UniqueConstraint(['_bettor', '_bettable'])

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f"Bet  {self._name}"

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

    def save(self):
        if self._bettable._referred._start_dt._value > datetime.now().replace(tzinfo=timezone.utc):
            super().save()
        else:
            print(f"{__file__} Bet rejected: Bettable has already started ({self._bettable._referred._start_dt._value})")
