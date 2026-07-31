"""
UC The tournament starts:
Five minutes before the start of the first bettable of a tournament T, T state is set to RUNNING
"""
from datetime import datetime

from ui.console_ui import input_selection, info
from model.bettable import Bettable, BETTABLE_STATE_CLOSED, BETTABLE_OUTCOME_DRAW, BETTABLE_OUTCOME_A_WINS, \
    BETTABLE_OUTCOME_B_WINS
from model.betty import Betty
from model.phase import Phase
from model.team import Team
from model.tournament import Tournament

"""
UC A bettable starts:
Five minutes before the start of a bettable, its state is set to RUNNING 
"""
def display_bettable(attr_dict):
    ret = f"{attr_dict['tournament_name']}, {attr_dict['phase_name']} : {attr_dict['start_dt']} : {attr_dict['a_team_name']} - {attr_dict['b_team_name']}"
    if outcome:=attr_dict['outcome']:
        if outcome == BETTABLE_OUTCOME_DRAW:
            ret += "  => Draw"
        else:
            ret += "  => Winner: "
            ret += attr_dict['a_team_name'] if attr_dict['outcome']==BETTABLE_OUTCOME_A_WINS else attr_dict['b_team_name']
    return ret

def input_outcome(attr_dict):
    bettable = Bettable(Betty(), id=attr_dict['id'])
    bettable.load()
    outcome_selected = input_selection([f"{attr_dict['a_team_name']} wins", f"{attr_dict['b_team_name']} wins", "draw"])
    if outcome_selected >= 0:
        if outcome_selected == 0:
            outcome = BETTABLE_OUTCOME_A_WINS
        if outcome_selected == 1:
            outcome = BETTABLE_OUTCOME_B_WINS
        elif outcome_selected == 2:
            outcome = BETTABLE_OUTCOME_DRAW # Draw
        bettable._outcome._value = outcome
        bettable._state._value = BETTABLE_STATE_CLOSED
        attr_dict['outcome'] = outcome
        bettable.save()

if __name__ == '__main__':
    # Get the bettable of which the start date is overdue and have not outcome
    attr_dicts = Betty().query(f"SELECT b.id, ta.name AS a_team_name, tb.name AS b_team_name, b.start_dt, b.state, p.name AS phase_name, tr.name AS tournament_name, b.outcome"
                               f" FROM {Bettable._table_} b"
                               f" JOIN {Team._table_} ta ON ta.id = b.a_team_id"
                               f" JOIN {Team._table_} tb ON tb.id = b.b_team_id"
                               f" JOIN {Phase._table_} p ON b.phase_id = p.id"
                               f" JOIN {Tournament._table_} tr ON p.tournament_id=tr.id"
                               f" WHERE b.start_dt < '{datetime.now()}' AND b.outcome IS NULL"
                               f" ORDER BY b.start_dt ASC")
    if attr_dicts:
        while (selection:=input_selection(attr_dicts, lambda x: display_bettable(x))) >= 0:
            input_outcome(attr_dicts[selection])
    else:
        info("There is no running bettable needing to be closed")