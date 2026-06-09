from datetime import datetime, timedelta
from .storable import Storable
from .sheep_value import SheepValue
from .betty import *

#from SqlStore import SqlStore

class Team(Storable):

    def __init__(self, store, name:str, tournament:Tournament=None, sheep_value:int=None):
        super().__init__(store)
        self._id = None
        self._name = name or "unnamed"+str(id(self))
        self._tournament = tournament
        self._sheep_value = SheepValue(store, self, tournament, sheep_value)

    def __str__(self):
        return f'Team {self._name}'

    def __repr__(self):
        return super().__repr__()

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, v):
        self._name = v or "unnamed" + str(id(self))

    #property
    def tournament_id(self):
        return self._tournament._id

    def load(self, condition):
        self.store_mgr.load(self, f"tournament_id={self.tournament_id}" + (f" AND {condition}" if condition else ''))

    def load_by_id(self):
        self.store_mgr.load(self, f"id={self._id}")

    def save(self):
        self.store_mgr.save(self)
        if self._tournament and self._sheep_value:
            self._sheep_value.save()

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

