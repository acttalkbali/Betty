from datetime import datetime, timezone
from importlib.metadata import requires

from .storable import Storable, Field, CharField, Many2OneField, DateField, UniqueConstraint
from .phase import Phase
from .team import Team

BETTABLE_STATE_OPEN = "OPEN"
BETTABLE_STATE_RUNNING = "RUNNING"
BETTABLE_STATE_CLOSED = "CLOSED"

BETTABLE_OUTCOME_A_WINS = "1"
BETTABLE_OUTCOME_B_WINS = "2"
BETTABLE_OUTCOME_DRAW = "0"

class Bettable(Storable):
    _table_ = "bettable"

    phase = Many2OneField(Phase.id)
    a_team = Many2OneField(Team.id)
    b_team = Many2OneField(Team.id, check=lambda inst, x: x is None or inst.a_team is None or x != inst.a_team)
    start_dt = DateField(required=False) # # Todo required=True?
    state = CharField(default_value=BETTABLE_STATE_OPEN)
    outcome = CharField(required=False)

    constraint = UniqueConstraint([phase, a_team, b_team])

    def __init__(self, phase: Phase|int=None, team_a: Team|int=None, team_b: Team|int=None, start_dt: datetime=None, outcome:int|None=None, id:int|None=None):
        super().__init__(id)
        self.name = f"{phase.name if isinstance(phase,Phase) else str(phase)}:{team_a.name if isinstance(team_a, Team) else str(team_a)} - {team_b.name if isinstance(team_b, Team) else str(team_b)}"
        self.phase = phase
        self.a_team = team_a
        self.b_team = team_b
        self.start_dt = start_dt
        self.state = None if start_dt is None else BETTABLE_STATE_OPEN if start_dt > datetime.now(timezone.utc) else BETTABLE_STATE_RUNNING
        self.outcome = outcome
        #self.constraint = UniqueConstraint(["_phase", "_team_a", "_team_b"])

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f'Bettable {self.a_team} - {self.b_team} [{self.start_dt}]'

    def __repr__(self):
        return super().__repr__()

    # properties -----------------------------------------------------------------

    @property
    def phase_id(self):
        return self.phase.id

    @property
    def a_team_id(self):
        return self.a_team.id

    @property
    def b_team_id(self):
        return self.b_team.id

    # storable -----------------------------------------------------------------
