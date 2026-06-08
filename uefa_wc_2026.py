from model.tournament import Tournament
from model.phase import Phase
from model.team import Team
from model.bettable import Bettable
from datetime import datetime

def setup(betty):
    wc2026 = Tournament(betty, "FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21),
                    datetime(day=19, month=7, year=2026, hour=21))

    phases = {
        '1st round': {
            'Group A': {
                'South Africa': 100,
                'South Korea': 5,
                'Mexico': 40,
                'Czech Republic': 40
            },
            'Group B': {
                'Bosnia': 30,
                'Canada': 20,
                'Qatar': 1,
                'Switzerland': 40
            },
            'Group B': {
                'Brazil': 100,
                'Scotland': 30,
                'Haiti': 1,
                'Morocco': 15
            },
            'Group D' : {
                'Belgium' : 40,
                'Iran' : 10,
                'Egypt' : 5,
                'New Zealand' : 1
            }
        }
    }

    wc2026.save()
    for phase_name, phase_groups in phases.items():
        Phase(betty,phase_name, wc2026).save()
        for group_name, group_compo in phase_groups.items():
            for team_name, sheep_value in group_compo.items():
                Team(betty, team_name, wc2026, sheep_value).save()
