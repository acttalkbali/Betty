from .storable import Storable, Field, Many2OneField, CharField, FloatField, UniqueConstraint
from .bettor import Bettor
from .bettable import Bettable

from datetime import datetime, timezone


class Bet(Storable):
    _table_ = 'bet'

    bettor = Many2OneField(Bettor.id, required=True)
    bettable = Many2OneField(Bettable.id, required=True)
    prediction = CharField(required=True)
    score = FloatField(required=False)

    bettor_bettable_unicity = UniqueConstraint([bettor, bettable])

    def __init__(self, bettor: Bettor|int=None, bettable: Bettable|int=None, prediction: int|None=None, score:int|None=None):
        super().__init__()
        self.name = f"{bettor}:{bettable}={prediction}"
        self.bettor = bettor
        self.bettable = bettable
        self.prediction = prediction # eg. 10=Team_a victory, 01=Team b Victory, 00=Nul, 11=Team_a or Team_b victory, 10=Team_a or nul, 02=Team_b or nul
        self.score = score
        #self._bettor_bettable_unicity = UniqueConstraint(['_bettor', '_bettable'])

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f"Bet  {self.name}"

    def __repr__(self):
        return super().__repr__()

    # properties -----------------------------------------------------------------

    @property
    def bettor_id(self):
        return self.bettor._id

    @property
    def bettable_id(self):
        return self.bettable._id

    # storable -----------------------------------------------------------------

    def save(self):
        if self.bettable.start_dt > datetime.now().replace(tzinfo=timezone.utc):
            super().save()
        else:
            print(f"{__file__} Bet rejected: Bettable has already started ({self.bettable.start_dt})")
