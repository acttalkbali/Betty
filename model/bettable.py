from datetime import datetime, timezone
from importlib.metadata import requires

from .storable import Storable, Referenceable, Field, DbDate, DbText, UniqueConstraint
from .phase import Phase
from .team import Team

BETTABLE_STATE_OPEN = "OPEN"
BETTABLE_STATE_RUNNING = "RUNNING"
BETTABLE_STATE_CLOSED = "CLOSED"

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
    def __init__(self, store, phase: Phase|int, team_a: Team|int, team_b: Team|int, start_dt: datetime, outcome:int|None=None, id:int|None=None):
        super().__init__(store, id)
        self._name = f"{phase.name if isinstance(phase,Phase) else str(phase)}:{team_a.name if isinstance(team_a, Team) else str(team_a)} - {team_b.name if isinstance(team_b, Team) else str(team_b)}"
        self._phase = Referenceable(phase)
        self._a_team = Referenceable(team_a)
        self._b_team = Referenceable(team_b)
        self._start_dt = Field(start_dt, DbDate, required=False) # Todo required=True?
        self._state = Field(BETTABLE_STATE_OPEN if start_dt > datetime.now(timezone.utc) else BETTABLE_STATE_RUNNING, DbText, dflt=BETTABLE_STATE_OPEN)
        self._outcome = Field(outcome, DbText, required=False)
        self._constraint = UniqueConstraint(["_phase", "_team_a", "_team_b"])

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f'Bettable {self._team_a.name} - {self._team_b.name} [{self._start_dt}]'

    def __repr__(self):
        return super().__repr__()

    # properties -----------------------------------------------------------------

    @property
    def phase_id(self):
        return self._phase.id

    @property
    def a_team_id(self):
        return self._team_a.id

    @property
    def b_team_id(self):
        return self._team_b.id

    # storable -----------------------------------------------------------------

    def load(self, condition=''):
        return self.store_mgr.load(self, f"phase_id={self.phase_id} AND team_a_id={self.team_a_id} AND team_b_id={self.team_b_id}" + (f" AND {condition}" if condition else ''))

