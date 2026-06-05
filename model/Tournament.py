from datetime import datetime, date, timedelta
from Storable import Storable
from SqlStore import SqlStore

TOURNAMENT_STATE_OPEN = "OPEN"
TOURNAMENT_STATE_RUNNING = "RUNNING"
TOURNAMENT_STATE_CLOSED = "CLOSED"

class Tournament(Storable):

    def __init__(self, name:str, start_date:datetime = None, end_date:datetime = None):
        super().__init__()
        self._name = name or "unnamed"+str(id(self))
        self._dt_start = start_date or datetime.now()
        self._dt_end = max(self._dt_start, end_date or datetime.now() + timedelta(days=365))
        self._state = TOURNAMENT_STATE_OPEN if self._dt_start > datetime.now() else TOURNAMENT_STATE_RUNNING

    def __str__(self):
        return f'Tournament {self._name} starting on {self._dt_start}, ending on {self._dt_end}'

    def __repr__(self):
        return super().__repr__(self)

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, v):
        self._name = v or "unnamed" + str(id(self))

    @property
    def start_date(self):
        return self.__dt_start
    @start_date.setter
    def start_date(self, value : dt.datetime):
        """
        start date is changed only if it occurs before a set end date
        """
        if self._dt_start == self._dt_end:
            self._dt_end = value
        else:
            if self._dt_start < self._dt_end:
                self._dt_start = value

    @property
    def end_date(self):
        return self._dt_start
    @end_date.setter
    def end_date(self, value : DateTime):
        """
        end date is set only if it occurs on or after the start date
        """
        if value >= self._dt_start: #
            self._dt_end = value

    def load(self, condition = ''):
        Betty().get_store().run_query(f"SELECT * FROM {model().entity}" + (f" WHERE {condition}" if condition else '') + ";")

    def save(self):
        SqlStore().get_store().run_query(f"INSERT OR UPDATE {model().entity} (name, start, state) VALUES ({self._name}, {self.start_date}, {self.state});")

if __name__ == '__main__':
    t1 = Tournament("T1")
    t2 = Tournament("T2", datetime.now())
    t3 = Tournament("FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21), datetime(day=19, month=7, year=2026, hour=21))
    print(f'{t1.name} / {t2.name} / {t3.name}')
    t3.save()
    #t1.name = "Tournament 1"
    #t1.start_date = dt.datetime(2026, 7,15,20)

