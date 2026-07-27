from datetime import datetime, timedelta
from .storable import Storable, Referenceable
from .betty import *

#from SqlStore import SqlStore

TOURNAMENT_STATE_OPEN = "OPEN"
TOURNAMENT_STATE_RUNNING = "RUNNING"
TOURNAMENT_STATE_CLOSED = "CLOSED"

class Participation(Storable):

    def __init__(self, store, bettor:Bettor, tournament:Tournament, score=0, credit=0, id=None):
        super().__init__(store, id)
        self._bettor = Referenceable(bettor)
        self._tournament = Referenceable(tournament)
        self._score = Field(score)
        self._credit = Field(credit or tournament.sheep_credit)

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
        if self.id:
            condition += self.store.wrap_condition('id', '=', self.id)
        elif self._bettor and self._tournament:
            condition += self.store.wrap_condition('bettor_id', '=', self._bettor.id)
            condition += ' AND ' + self.store.wrap_condition('tournament_id', '=', self._tournament.id)
        results = self.store_mgr.load(type(self), condition)
        if len(results)==1:
            result = results[0]
            self._id = result['id']
            self._bettor = Bettor(self.store_mgr, id=result[f'{Betty().class_entity[Bettor]}_id'])
            self._tournament = Tournament(self.store_mgr, id=result[f'{Betty().class_entity[Tournament]}_id'])
            self._score = result['score']
            self._credit = result['credit']
            print(f"Filled {self}")
        self.store_mgr.run_query(f"SELECT * FROM {Betty().class_entity[type(self)]}" + (f" WHERE {condition}" if condition else '') + ";")



