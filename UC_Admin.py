from UC_Bettor import tournament_status, calculate_score, E_PREDICTIONS, E_OUTCOMES
from UC_Time import input_outcome
from model import tournament
from model.bet import Bet
from model.bettable import Bettable
from model.bettor import Bettor
from model.betty import Betty
from model.participation import Participation
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
    attr_dicts = Betty().query(f"SELECT tr.id, tr.name, tr.start_dt FROM {Tournament._table_} tr WHERE {states_condition}")
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
        # Select the tournament's bettables which have a non-NULL outcome
        bettable_attr_dicts = Betty().query(
            f"SELECT b.id as bettable_id, b.outcome, p.id as phase_id "
            f"FROM {Bettable._table_} b, {Phase._table_} p, {Tournament._table_} tr "
            f"WHERE b.phase_id = p.id AND p.tournament_id = {UiAdminContext().tournament_selected_id} AND b.outcome IS NOT NULL "
            f"ORDER BY b.start_dt ASC")

        prv_score = ''
        ranking = 1

        scoring = dict()
        bet_score = dict()
        for prediction in E_PREDICTIONS:
            for outcome in E_OUTCOMES:
                bet_score[(prediction,outcome)] = calculate_score(prediction, outcome)

        for bettable_attr_dict in bettable_attr_dicts:
            # Select all bettor predictions for that bettable
            bet_attr_dicts = Betty().query(
                f"SELECT bt.prediction, bt.bettor_id, br.nickname "
                f"FROM {Bet._table_} bt, {Bettor._table_} br "
                f"WHERE bt.bettable_id = {bettable_attr_dict['bettable_id']} AND bt.bettor_id = br.id "
                f"ORDER BY br.nickname, bt.prediction ASC")

            for bet_attr_dict in bet_attr_dicts:
                scoring[(bet_attr_dict['bettor_id'],bet_attr_dict['nickname'])] = \
                        scoring.get((bet_attr_dict['bettor_id'], bet_attr_dict['nickname']) , 0) \
                        + bet_score[(bet_attr_dict['prediction'],bettable_attr_dict['outcome'])]

        print(f"\n========== {UiAdminContext().tournament_selected_name} RANKING ==========")
        prv_score = ''
        ranking = 1
        for rank, bettor_score in enumerate(sorted(scoring.items(), key=lambda x: x[1], reverse=True)):
            if bettor_score[1] != prv_score:
                # Not an ex-aequo
                prv_score = bettor_score[1]
                ranking = rank + 1
            print(f"{ranking:3} {bettor_score[0][1]:20} {bettor_score[1]:3} points")
            r = Ranking(Betty(), tournament=UiAdminContext().tournament_selected_id, bettor=bettor_score[0][0])
            r.load()
            r._rank._value=ranking
            r._score._value=bettor_score[1]
            r.save()

        # Handle the bettor with no bet yet
        ranking += 1
        for name, nickname, nbets, id in filter(lambda x: x[2]==0, tournament_participation(silent=True)):
            print(f"{ranking:3} {nickname:20} 0 points")
            r = Ranking(Betty(), tournament=UiAdminContext().tournament_selected_id, bettor=id)
            r.load()
            r._rank._value=ranking
            r._score._value=0
            r.save()




def show_ranking():
    """
    UC Tournament ranking:
    PRE bettor logged-in, OPEN tournament T selected
    The bettor choose 'tournament ranking' from the available actions.
    The tournament's current bettor ranking is listed.
    """
    if UiAdminContext().tournament_selected:
        attr_dicts = Betty().query(
            f"SELECT r.id, br.nickname, r.tournament_id, r.score, r.rank "
            f"FROM {Ranking._table_} r "
            f"JOIN {Bettor._table_} br ON r.bettor_id = br.id "
            f"WHERE r.tournament_id={UiAdminContext().tournament_selected_id} "
            f"ORDER BY r.rank ASC")

        print(f"\n========== {UiAdminContext().tournament_selected_name} RANKING ==========")
        prv_score = ''
        ranking = 1
        for rank,attr_dict in enumerate(attr_dicts):
            if attr_dict['score'] != prv_score:
                # Not an ex-aequo
                prv_score = attr_dict['score']
                ranking = rank + 1
            print(f"{ranking:3} {attr_dict['nickname']:20} {attr_dict['score']:3} points")

"""
UC The admin get the list of a tournament's paticipants
"""
def tournament_participation(silent=False) -> list[(int,str,str,int)]:
    if not UiAdminContext().tournament_selected:
        tournament_selection()
    if UiAdminContext().tournament_selected:
        attr_dicts = Betty().query(
            f"SELECT br.name, br.nickname, br.id "
            f"FROM {Participation._table_} p "
            f"FULL JOIN {Bettor._table_} br ON p.bettor_id=br.id "
            f"WHERE p.tournament_id={UiAdminContext().tournament_selected_id} "
            f"ORDER BY br.name ASC")

        if not silent: print(f"{UiAdminContext().tournament_selected_name} participants:")

        bet_stats = []
        for attr_dict in attr_dicts:
            bettor_attr_dicts = Betty().query(
                f"SELECT COUNT(bt.id) as bet_counter, br.nickname "
                f"FROM {Bet._table_} bt "
                f"JOIN {Bettor._table_} br ON bt.bettor_id={attr_dict['id']} "
                f"JOIN {Bettable._table_} ba ON bt.bettable_id=ba.id "
                f"JOIN {Phase._table_} ph ON ph.id=ba.phase_id AND ph.tournament_id={UiAdminContext().tournament_selected_id} "
                f"GROUP BY br.nickname")
            nb_bets = bettor_attr_dicts[0]['bet_counter'] if bettor_attr_dicts else 0
            bet_stats.append((attr_dict['name'],attr_dict['nickname'],nb_bets,attr_dict['id'],))

        result = sorted(bet_stats, key=lambda x: x[2], reverse=True)
        if not silent:
            for bet_stat in result:
                print(f"   {bet_stat[0]} as {bet_stat[1]} : {bet_stat[2]} bets")
        return result

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
               ('Tournament participation', tournament_participation),
               ('Compute ranking', lambda: compute_ranking()),
               ('Show ranking', lambda: show_ranking()),
               ('Status', lambda : tournament_status()),
               ('Quit', lambda : quit())]
    selection = 0
    ret = None
    while ret != -1:
        info(f'_____ Selected tournament: {UiAdminContext().tournament_selected_name}')
        selection = input_selection(options, lambda x:x[0], exit_option=6)
        ret = options[selection][1]() # execute the action
