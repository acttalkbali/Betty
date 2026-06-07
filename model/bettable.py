from datetime import datetime

from .storable import Storable
from .team import Team
from .phase import Phase

BETTABLE_STATE_OPEN = "OPEN"
BETTABLE_STATE_RUNNING = "RUNNING"
BETTABLE_STATE_CLOSED = "CLOSED"

class Bettable(Storable):

    def model():
        return {'entity': 'PHASE',
                'attribute_mapping': [('name', '_name'),
                                      ('team_a_id', '_team_a.id'),
                                      ('team_b_id', '_team_b.id'),
                                      ('start', '_start'),
                                      ('state', '_state')]}

    def __init__(self, phase: Phase, team_a: Team, team_b: Team, start: datetime, store):
        super().__init__(store)
        self._name = f"{phase.name}:{team_a.name}-{team_b.name}"
        self._team_a = team_a
        self._team_b = team_b
        self._start = start
        self._state = BETTABLE_STATE_OPEN if start > datetime.now() else BETTABLE_STATE_RUNNING

    def __str__(self):
        return f'Bettable {self._team_a.name} - {self._team_b.name} [{start}]'

    def __repr__(self):
        return super().__repr__(self)

