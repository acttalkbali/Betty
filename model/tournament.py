from datetime import datetime, timedelta, timezone
from .storable import Storable, Field, CharField, DateField, IntegerField, StorableMeta

#from SqlStore import SqlStore

TOURNAMENT_STATE_OPEN = "OPEN"
TOURNAMENT_STATE_RUNNING = "RUNNING"
TOURNAMENT_STATE_CLOSED = "CLOSED"
TOURNAMENT_STATE_LOCKED = "LOCKED"

class Tournament(Storable):
    _table_ = "tournament"

    name = CharField(unique=True)
    start_dt = DateField()
    end_dt = DateField(check=lambda self, x: self.start_dt is None or x >= self.start_dt)
    state = CharField(default_value=TOURNAMENT_STATE_LOCKED)
    sheep_credit = IntegerField(default_value=500) # todo 0 as default?

    def __init__(self, id:int|None=None, name:str|None=None, start_date:datetime|None=None, end_date:datetime|None=None, sheep_credit:int=500):
        super().__init__(id)
        self.name = name
        self.start_dt = start_date
        self.end_dt = end_date #max(self._start_dt, end_date or datetime.now() + timedelta(days=365))
        self.state = TOURNAMENT_STATE_LOCKED if (start_date is None) else (TOURNAMENT_STATE_OPEN if start_date > datetime.now(timezone.utc) else TOURNAMENT_STATE_RUNNING)
        self.sheep_credit = sheep_credit

    def __str__(self):
        return f'Tournament {self.name} starting on {self.start_dt}, ending on {self.end_dt}'

    def __repr__(self):
        return super().__repr__()

    #@property
    #def start_dt(self):
    #    return self.start_dt
    #@start_dt.setter
    #def start_dt(self, value : datetime):
    #    """
    #    start date is changed only if it occurs before a set end date
    #    """
    #    if self.start_dt == self.end_dt:
    #        self.end_dt = value
    #    else:
    #        if self.start_dt < self.end_dt:
    #            self.start_dt = value

    #@property
    #def end_dt(self):
    #    return self.start_dt
    #@end_dt.setter
    #def end_dt(self, value : datetime):
    #    """
    #    end date is set only if it occurs on or after the start date
    #    """
    #    if value >= self.start_dt: #
    #        self.end_dt = value

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

