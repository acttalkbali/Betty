from datetime import datetime, timezone
from importlib.metadata import requires

from .storable import Storable, Referenceable, Field, DbDate, DbText, UniqueConstraint
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

    """
    id SERIAL PRIMARY KEY,
    {cls.references_by_id(Phase)},
    {cls.references_by_id(Team, 'a')},
    {cls.references_by_id(Team, 'b')},
    start_dt TIMESTAMPTZ,
    state TEXT NOT NULL,
    outcome TEXT
    """
    def __init__(self, store=None, phase: Phase|int|None=None, team_a: Team|int|None=None, team_b: Team|int|None=None, start_dt: datetime|None=None, outcome:int|None=None, id:int|None=None):
        super().__init__(store, id)
        self._name = f"{phase.name if isinstance(phase,Phase) else str(phase)}:{team_a.name if isinstance(team_a, Team) else str(team_a)} - {team_b.name if isinstance(team_b, Team) else str(team_b)}"
        self._phase = Referenceable(Phase, phase)
        self._a_team = Referenceable(Team, team_a)
        self._b_team = Referenceable(Team, team_b)
        self._start_dt = Field(start_dt, DbDate, required=False) # Todo required=True?
        self._state = None #Field(None if start_dt is None else BETTABLE_STATE_OPEN if start_dt > datetime.now(timezone.utc) else BETTABLE_STATE_RUNNING, DbText, dflt=BETTABLE_STATE_OPEN)
        self._outcome = Field(outcome, DbText, required=False)
        self._constraint = UniqueConstraint(["_phase", "_a_team", "_b_team"])

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f'Bettable {self._a_team} - {self._b_team} [{self._start_dt}]'

    def __repr__(self):
        return super().__repr__()

    # properties -----------------------------------------------------------------

    @property
    def phase_id(self):
        return self._phase.id

    @property
    def a_team_id(self):
        return self._a_team.id

    @property
    def b_team_id(self):
        return self._b_team.id

    # storable -----------------------------------------------------------------
