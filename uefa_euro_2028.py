from model.tournament import Tournament
from model.phase import Phase
from model.team import Team
from model.sheep_value import SheepValue
from model.bettable import Bettable
from datetime import datetime

def setup(betty):
    euro2028 = Tournament(betty,
                        name="UEFA Euro 2028",
                        start_date=datetime.fromisoformat('2028-06-11 21:00:00+00'),
                        end_date=datetime.fromisoformat('2028-07-19 21:00:00+00'))
    phases = [
                {
                    'name' : '1st round',
                    'scoring': '630',
                    'pools': {
                        'Group A': [
                            ('Germany', 100),
                            ('Belgium', 5),
                            ('Cyprus', 40),
                            ('Luxembourg', 40)
                        ]
                    }
                }
            ]
    calendar = [
    ]

    euro2028.save()
    teams = {}
    for phase_dict in phases:
        phase = Phase(name=phase_dict['name'], tournament=euro2028, state="OPEN", scoring=phase_dict['scoring'])
        phase.save()
        for group_name, group_compo in phase_dict['pools'].items():
            for team_name, sheep_value in group_compo:
                teams[team_name] = Team(betty, team_name) # , wc2026, sheep_value
                teams[team_name].save()
                sheep_value = SheepValue(betty, teams[team_name], euro2028, sheep_value)
                sheep_value.save()
        for start_dt, team_a_name, team_b_name in calendar:
            bettable = Bettable(phase=phase, team_a=teams[team_a_name], team_b=teams[team_b_name], start_dt=datetime.fromisoformat(start_dt))
            bettable.save()
