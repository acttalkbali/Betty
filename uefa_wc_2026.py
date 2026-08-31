from model.tournament import Tournament
from model.phase import Phase
from model.team import Team
from model.sheep_value import SheepValue
from model.bettable import Bettable
from datetime import datetime

def setup(betty):

    wc2026 = Tournament(betty,
                        name="FIFA World Cup 2026",
                        start_date=datetime.fromisoformat('2026-07-29 09:00:00+00'),
                        end_date=datetime.fromisoformat('2026-09-19 21:00:00+00'))
    phases:list[dict] = [
                {
                    'name' : '1st round',
                    'scoring': '630',
                    'pools': {
                        'Group A': [
                            ('South Africa', 100),
                            ('South Korea', 5),
                            ('Mexico', 40),
                            ('Czech Republic', 40)
                        ],
                        'Group B': [
                            ('Bosnia', 30),
                            ('Canada', 20),
                            ('Qatar', 1),
                            ('Switzerland', 40)
                        ],
                        'Group C': [
                            ('Brazil', 100),
                            ('Scotland', 30),
                            ('Haiti', 1),
                            ('Morocco', 15)
                        ],
                        'Group D' : [
                            ('Belgium', 40),
                            ('Iran', 10),
                            ('Egypt', 5),
                            ('New Zealand', 1)
                        ]
                    }
                }
            ]
    calendar = [
        ('2026-07-29 13:00+00', 'Mexico', 'South Africa'),
        ('2026-08-12 04:00+00', 'South Korea', 'Czech Republic'),
        ('2026-08-18 18:00+00', phases[0]['pools']['Group A'][3][0], phases[0]['pools']['Group A'][0][0]),
        ('2026-08-19 03:00+00', phases[0]['pools']['Group A'][2][0], phases[0]['pools']['Group A'][1][0]),
        ('2026-08-25 03:00+00', phases[0]['pools']['Group A'][3][0], phases[0]['pools']['Group A'][2][0]),
        ('2026-08-25 03:00+00', phases[0]['pools']['Group A'][0][0], phases[0]['pools']['Group A'][1][0]),
    ]

    wc2026.save()
    teams = {}
    for phase_dict in phases:
        phase = Phase(name=phase_dict['name'], tournament=wc2026, state="OPEN", scoring=phase_dict['scoring'])
        phase.save()
        for group_name, group_compo in phase_dict['pools'].items():
            for team_name, sheep_value in group_compo:
                teams[team_name] = Team(betty, team_name) # , wc2026, sheep_value
                teams[team_name].save()
                sheep_value = SheepValue(betty, teams[team_name], wc2026, sheep_value)
                sheep_value.save()
        for start_dt, team_a_name, team_b_name in calendar:
            bettable = Bettable(betty, phase, teams[team_a_name], teams[team_b_name], datetime.fromisoformat(start_dt))
            bettable.save()
