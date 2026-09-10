from datetime import datetime, timedelta
from .storable import Storable, CharField

class Team(Storable):
    _table_ = "team"

    name = CharField(required=True, unique=True)

    def __init__(self, name:str|None=None, id:int|None=None):
        super().__init__(id)
        self.name = name
        #self._tournament = tournament

    def __str__(self):
        return f'{self.name or self.pk_value()}'

    def __repr__(self):
        return super().__repr__()


if __name__ == '__main__':
    from .tournament import Tournament
    t1 = Tournament(name="T1")
    t2 = Tournament(name="T2", start_dt=datetime.now())
    t3 = Tournament(name="FIFA World Cup 2026", start_date=datetime(day=11, month=6, year=2026, hour=21), end_date=datetime(day=19, month=7, year=2026, hour=21))
    print(f'{t1.name} / {t2.name} / {t3.name}')
    t3.save()
