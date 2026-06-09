from datetime import datetime, timedelta
from .storable import Storable
from .betty import *

#from SqlStore import SqlStore

class SheepValue(Storable):

    def __init__(self, store, team:Team, tournament:Tournament, sheep_value:int):
        super().__init__(store)
        self._team = team
        self._team_id = team.id
        self._tournament = tournament
        self._tournament_id = tournament.id
        self._sheep_value = sheep_value

    def __str__(self):
        return f'{self._team.name} {self.tournament.name} Sheep Value: {self._sheep_value}'

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
        return self._tournament.id

    #property
    def team_id(self):
        return self._team.id

    def load(self, condition = ''):
        self.store_mgr.load(self)

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

