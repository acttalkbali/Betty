from datetime import datetime, timedelta
from .storable import Storable, Field, DbText, UniqueField

class Team(Storable):
    _table_ = "team"

    def __init__(self, store=None, name:str|None=None, id:int|None=None):
        super().__init__(store, id)
        self._name = UniqueField(name, DbText)

    def __str__(self):
        return f'{self._name or self._id}'

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


if __name__ == '__main__':
    from .tournament import Tournament
    t1 = Tournament(name="T1")
    t2 = Tournament(name="T2", start_dt=datetime.now())
    t3 = Tournament(name="FIFA World Cup 2026", start_date=datetime(day=11, month=6, year=2026, hour=21), end_date=datetime(day=19, month=7, year=2026, hour=21))
    print(f'{t1.name} / {t2.name} / {t3.name}')
    t3.save()
    #t1.name = "Tournament 1"
    #t1.start_date = dt.datetime(2026, 7,15,20)

