from datetime import datetime, timedelta
from .storable import Storable, Many2OneField, FloatField, IntegerField, Referenceable
from .betty import *

#from SqlStore import SqlStore

TOURNAMENT_STATE_OPEN = "OPEN"
TOURNAMENT_STATE_RUNNING = "RUNNING"
TOURNAMENT_STATE_CLOSED = "CLOSED"

class Participation(Storable):

    bettor = Many2OneField(Bettor.id)
    tournament = Many2OneField(Tournament.id)
    score = FloatField()
    credit = IntegerField()

    def __init__(self, bettor:Bettor=None, tournament:Tournament=None, score=0, credit=0, id=None):
        super().__init__(id)
        self.bettor = bettor
        self.tournament = tournament
        self.score = score
        self.credit = credit or tournament.sheep_credit if tournament else None

    def __str__(self):
        return f'Participation {self.bettor} {self.tournament}'

    def __repr__(self):
        return super().__repr__()

    @property
    def bettor_id(self):
        return self.bettor.id

    @property
    def tournament_id(self):
        return self.tournament.id
