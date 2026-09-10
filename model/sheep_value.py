from datetime import datetime, timedelta
from .storable import Storable, Many2OneField, IntegerField
from .tournament import Tournament
from .team import Team
#from SqlStore import SqlStore

class SheepValue(Storable):
    _table_ = "sheep_value"

    team = Many2OneField(Team.id)
    tournament =  Many2OneField(Tournament.id)
    sheep_value = IntegerField(check=lambda inst, x: x > 0)

    def __init__(self, team:Team|int=None, tournament:Tournament|int=None, sheep_value:int=None, id:int|None=None):
        super().__init__(id)
        self.team = team
        self.tournament = tournament
        self.sheep_value = sheep_value

    def __str__(self):
        return f'{self.team.name} {self.tournament.name} Sheep Value: {self.sheep_value}'

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
        return self.tournament._id if isinstance(self.tournament, Tournament) else 0
    #property
    def team_id(self) -> int|None:
        return self.team._id if isinstance(self.team, Team) else 0

    #property
    def team_name(self):
        return self.team.name if isinstance(self.team, Team) else f"Team {self.team_id}"


if __name__ == '__main__':
    from .betty import Betty
    betty = Betty()
    t1 = Tournament(betty, "T1")
    t2 = Tournament(betty, "T2", datetime.now())
    t3 = Tournament(betty, "FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21), datetime(day=19, month=7, year=2026, hour=21))
    print(f'{t1.name} / {t2.name} / {t3.name}')
    t3.save()

