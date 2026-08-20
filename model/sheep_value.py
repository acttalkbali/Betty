from datetime import datetime, timedelta
from .storable import Storable, Referenceable, Field
from .tournament import Tournament
from .team import Team
#from SqlStore import SqlStore

class SheepValue(Storable):
    _table_ = "sheep_value"

    def __init__(self, store=None, team:Team|int=None, tournament:Tournament|int=None, sheep_value:int=None, id:int|None=None):
        super().__init__(store, id)
        self._team = Referenceable(Team, team)
        #self._team_id = team.id
        self._tournament = Referenceable(Tournament, tournament)
        #self._tournament_id = tournament.id
        self._sheep_value = Field(sheep_value)

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
        return self._tournament._id if isinstance(self._tournament, Tournament) else 0
    #property
    def team_id(self) -> int|None:
        return self._team._id if isinstance(self._team, Team) else 0

    #property
    def team_name(self):
        return self._team._name if isinstance(self._team, Team) else f"Team {self.team_id}"


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

