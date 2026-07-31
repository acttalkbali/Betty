from UC_Bettor import tournament_status
from UC_Time import input_outcome
from model.bet import Bet
from model.bettable import Bettable
from model.betty import Betty
from model.phase import Phase
from model.ranking import Ranking
from model.tournament import Tournament
from ui.console_ui import input_selection, info

#================== UI context

class UiAdminContext:
    """
    Holds context information relevant for the user interaction
    Attributes may be added during the user interactions
    Singleton class
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("CREATING UiAdminContext")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialised"):
            self.tournament_selected_name = None # todo may be redundant with self.tournament_selected
            self.tournament_selected_id = None # todo may be redundant with self.tournament_selected
            self.tournament_selected = None
            self._initialised = True

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

"""
Admin Use Cases implementation
"""

"""
UC Tournament Creation:
The admin creates the tournament, setting its name, start and end date
"""

def tournament_selection(states:list[str]=None) -> int:
    """
    UC tournament selection:
    The admin selects an existing tournament.
    POST Tournament selected
    """

    states_condition = f" tr.state IN ({str(states)[1:-1]})" if states else 'TRUE'
    attr_dicts = Betty().query(f"SELECT tr.id, tr.name, p.id AS participation_id, p.credit FROM participation p LEFT JOIN {Tournament._table_} tr ON p.tournament_id=tr.id WHERE {states_condition}")
    if len(attr_dicts)==0:
        info("No tournament available")
    else:
        if len(attr_dicts) > 1:
            selection = input_selection(attr_dicts, lambda attr_dict: attr_dict['name'])
        else:
            selection = 0
        UiAdminContext().tournament_selected_name = attr_dicts[selection]['name']
        UiAdminContext().tournament_selected_id = attr_dicts[selection]['id']
        UiAdminContext().tournament_selected = Tournament(Betty(), name=attr_dicts[selection]['name'], id=attr_dicts[selection]['id'])
        print(f"Selected tournament : {UiAdminContext().tournament_selected_id}")
        return selection
    return -1

"""
UC Team Creation:
The admin creates a bettable team, setting its name
"""

"""
UC Team Tournament assignment;
PRE tournament is selected
The admin assigns a bettable team to a tournament, setting its sheep price for the tournament
"""

"""
UC Phase Creation:
PRE tournament is selected
The admin creates a tournament phase, setting its type, name, number, wallet
"""

"""
UC Bettable Creation:
PRE tournament T is selected, T phase is selected
The admin creates a bettable event for the selected phase, setting the teams involved and its start date & time. 
If the start date and time is in the future, the bettable state is set to OPEN 
"""

"""
UC Tournament Publishing:
PRE tournament is selected
The admin opens the tournament to bettors. The tournament's web-site is created, an invitation e-mail wih the link is sent
to the registered bettors (+ filtering +), and possibly to additional bettor candidates
"""
def open_tournament():
    pass


def compute_ranking():
    """
    UC Tournament ranking:
    OPEN tournament T selected
    """

    if UiAdminContext().tournament_selected_id:
        attr_dicts = Betty().query(
            f"SELECT r.id, b.nickname, r.tournament_id, r.score, r.rank "
            f"FROM {Ranking._table_} r, {Tournament._table_} tr "
            f"WHERE r.tournament_id={UiAdminContext().tournament_selected_id} "
            f"ORDER BY r.score DESC")

        print(f"\n========== {UiAdminContext().tournament_selected_name} RANKING ==========")
        prv_score = ''
        ranking = 1
        for rank,attr_dict in enumerate(attr_dicts):
            if attr_dict['score'] != prv_score:
                # Not an ex-aequo
                prv_score = attr_dict['score']
                ranking = rank + 1
            print(f"{ranking:3} {attr_dict['nickname']:20} {attr_dict['score']:3} points")

        # todo recompute the ranking from the closed bettables and the bettor predictions"
        attr_dicts = Betty().query(
            f"SELECT b.id, bt.bettor_id, bt.prediction, bt.score "
            f"FROM {Bet._table_} bt, {Bettable._table_} b, {Phase} p "
            f"WHERE p.tournament_id={UiAdminContext().tournament_selected_id} AND b.phase_id=p.id "
            f"ORDER BY bt.bettor_id ASC, b._start_dt ASC")

        for attr_dict in attr_dicts:
            print("Consider bet {attr_dict}")

"""
UC The admin registers a bettable score after its completion:
PRE RUNNING tournament T selected, RUNNING bettable selected
The admin registers the final score of the bettable. The bettable is set to CLOSED. 
The bettor ranking is re-computed. 
"""

"""
UC The admin corrects a bettable score after its completion:
PRE RUNNING tournament T selected, CLOSED bettable selected
The admin corrects the final score of the bettable.
"""

def quit()->int:
    """
    """
    UiAdminContext().tournament_selected_name = None
    return -1

if __name__ == '__main__':
    #load_dotenv()
    tournament_selection()
    options = [('Provide/Amend the outcome of a bettable', lambda : input_outcome()),
               ('Open tournament', lambda : open_tournament()),
               ('Compute ranking', lambda: compute_ranking()),
               ('Status', lambda : tournament_status()),
               ('Quit', lambda : quit())]
    selection = 0
    ret = None
    while ret != -1:
        info(f'_____ Selected tournament: {UiAdminContext().tournament_selected_name}')
        selection = input_selection(options, lambda x:x[0], exit_option=6)
        ret = options[selection][1]() # execute the action
