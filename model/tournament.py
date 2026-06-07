from datetime import datetime, timedelta
from .storable import Storable
from .betty import *

#from SqlStore import SqlStore

TOURNAMENT_STATE_OPEN = "OPEN"
TOURNAMENT_STATE_RUNNING = "RUNNING"
TOURNAMENT_STATE_CLOSED = "CLOSED"

class Tournament(Storable):

    def __init__(self, store, name:str, start_date:datetime = None, end_date:datetime = None):
        super().__init__(store)
        self._name = name or "unnamed"+str(id(self))
        self._start_dt = start_date or datetime.now()
        self._end_dt = max(self._start_dt, end_date or datetime.now() + timedelta(days=365))
        self._state = TOURNAMENT_STATE_OPEN if self._start_dt > datetime.now() else TOURNAMENT_STATE_RUNNING

    def __str__(self):
        return f'Tournament {self._name} starting on {self._start_dt}, ending on {self._end_dt}'

    def __repr__(self):
        return super().__repr__(self)

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, v):
        self._name = v or "unnamed" + str(id(self))

    @property
    def start_dt(self):
        return self._start_dt
    @start_dt.setter
    def start_dt(self, value : datetime):
        """
        start date is changed only if it occurs before a set end date
        """
        if self._start_dt == self._end_dt:
            self._end_dt = value
        else:
            if self._start_dt < self._end_dt:
                self._start_dt = value

    @property
    def end_dt(self):
        return self._start_dt
    @end_dt.setter
    def end_dt(self, value : datetime):
        """
        end date is set only if it occurs on or after the start date
        """
        if value >= self._start_dt: #
            self._end_dt = value

    def load(self, condition = ''):
        self.store_mgr.run_query(f"SELECT * FROM {Betty().class_entity[type(self)]}" + (f" WHERE {condition}" if condition else '') + ";")

    def save(self):
        self.store_mgr.save(self)

if __name__ == '__main__':
    from .betty import Betty
    betty = Betty()
    t1 = Tournament(betty, "T1")
    t2 = Tournament(betty, "T2", datetime.now())
    t3 = Tournament(betty, "FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21), datetime(day=19, month=7, year=2026, hour=21))
    print(f'{t1.name} / {t2.name} / {t3.name}')
    t3.save()
    #t1.name = "Tournament 1"
    #t1.start_date = dt.datetime(2026, 7,15,20)

