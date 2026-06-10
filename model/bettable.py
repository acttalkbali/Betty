from datetime import datetime

from .storable import Storable
from .phase import Phase
from .team import Team

BETTABLE_STATE_OPEN = "OPEN"
BETTABLE_STATE_RUNNING = "RUNNING"
BETTABLE_STATE_CLOSED = "CLOSED"

class Bettable(Storable):

    def __init__(self, store, phase: Phase, team_a: Team, team_b: Team, start_dt: datetime, outcome:int|None=None):
        super().__init__(store)
        self._name = f"{phase.name}:{team_a.name}-{team_b.name}"
        self._phase = phase
        self._team_a = team_a
        self._team_b = team_b
        self._start_dt = start_dt
        self._state = BETTABLE_STATE_OPEN if start_dt > datetime.now() else BETTABLE_STATE_RUNNING
        self._outcome = outcome

    # built_ins -----------------------------------------------------------------

    def __str__(self):
        return f'Bettable {self._team_a.name} - {self._team_b.name} [{start}]'

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

