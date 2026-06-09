from datetime import datetime, timedelta
from .storable import Storable
from .betty import *

#from SqlStore import SqlStore

TOURNAMENT_STATE_OPEN = "OPEN"
TOURNAMENT_STATE_RUNNING = "RUNNING"
TOURNAMENT_STATE_CLOSED = "CLOSED"

class Participation(Storable):

    def __init__(self, store, bettor:Bettor, tournament:Tournament, score=0):
        super().__init__(store)
        self._bettor = bettor
        self._tournament = tournament
        self._score = score

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

    def load(self, condition = ''):
        self.store_mgr.run_query(f"SELECT * FROM {Betty().class_entity[type(self)]}" + (f" WHERE {condition}" if condition else '') + ";")

    def save(self):
        self.store_mgr.save(self)


