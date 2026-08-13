from datetime import datetime, timedelta
from .storable import Storable, Referenceable
from .betty import *

#from SqlStore import SqlStore

TOURNAMENT_STATE_OPEN = "OPEN"
TOURNAMENT_STATE_RUNNING = "RUNNING"
TOURNAMENT_STATE_CLOSED = "CLOSED"

class Participation(Storable):

    def __init__(self, store, bettor:Bettor=None, tournament:Tournament=None, score=0, credit=0, id=None):
        super().__init__(store, id)
        self._bettor = Referenceable(Bettor, bettor)
        self._tournament = Referenceable(Tournament, tournament)
        self._score = Field(score)
        self._credit = Field(credit or tournament.sheep_credit if tournament else None)

    def __str__(self):
        return f'Participation {self._bettor} {self._tournament}'

    def __repr__(self):
        return super().__repr__()

    @property
    def bettor_id(self):
        return self._bettor.id

    @property
    def tournament_id(self):
        return self._tournament.id
