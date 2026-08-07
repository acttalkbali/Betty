import datetime

from UC_Bettor import tournament_status, calculate_score, E_PREDICTIONS, E_OUTCOMES
from UC_Time import input_outcome, display_bettable
from model import tournament
from model.bet import Bet
from model.bettable import Bettable
from model.bettor import Bettor
from model.betty import Betty
from model.participation import Participation
from model.phase import Phase
from model.ranking import Ranking
from model.team import Team
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

""" _______________ TOURNAMENT SETUP _______________ """

"""
UC Tournament Creation:
The admin creates the tournament, setting its name, start and end date
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
UC Team Creation:
The admin creates a bettable team, setting its name
"""

"""
UC Team Tournament assignment;
PRE tournament is selected
The admin assigns a bettable team to a tournament, setting its sheep price for the tournament
"""

""" _______________ TOURNAMENT OPERATION _______________ """

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

def open_tournament():
    """
    UC Tournament Publishing:
    PRE tournament is selected
    The admin opens the tournament to bettors. The tournament's web-site is created, an invitation e-mail wih the link is sent
    to the registered bettors (+ filtering +), and possibly to additional bettor candidates
    """
    print("<<<< Not implemented >>>>")

def betty_status():
    """
    UC Betty status
    Existing tournaments are listed together with their information.
    Namely status, start date, end date, #participants and for each phase: its status, start date, %age completion, #bettables, #bets.
    """
    tr_attr_dicts = Betty().query(
        f"SELECT id, name, start_dt, end_dt, state  "
        f"FROM {Tournament._table_} tr "
        f"ORDER BY start_dt DESC")

    for tr_attr_dict in tr_attr_dicts:
        print(f"Tournament: {tr_attr_dict['id']} {tr_attr_dict['name']} [{tr_attr_dict['start_dt']} - {tr_attr_dict['end_dt']}] {tr_attr_dict['state']}")
        bettable_attr_dicts = Betty().query(
            f"SELECT ba.id as bettable_id, ba.start_dt, t1.name as t1_name, t2.name as t2_name, ba.outcome, ba.state, ph.id as phase_id, ph.name as phase_name, ph.state as phase_state, ph.scoring "
            f"FROM {Bettable._table_} ba "
            f"JOIN {Phase._table_} ph ON ba.phase_id = ph.id "
            f"JOIN {Team._table_} t1 ON ba.a_team_id = t1.id "
            f"JOIN {Team._table_} t2 ON ba.b_team_id = t2.id "
            f"WHERE ph.tournament_id = {tr_attr_dict['id']} "
            f"ORDER BY ba.start_dt ASC")
        prv_phase_name = None
        for bettable_attr_dict in bettable_attr_dicts:
            if (phase_name:=bettable_attr_dict['phase_name']) != prv_phase_name:
                phase_name = phase_name.strip()
                prv_phase_name = phase_name
                print(f"    {phase_name} (Scoring rule: {bettable_attr_dict['scoring']})")
            print(f"        {bettable_attr_dict['bettable_id']} {bettable_attr_dict['start_dt']} {bettable_attr_dict['state']} {bettable_attr_dict['t1_name']} - {bettable_attr_dict['t2_name']} ")

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


def tournament_participation(silent=False) -> list[(int,str,str,int)]:
    """
    UC The admin get the list of a tournament's paticipants
    """
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

def quit()->int:
    """
    """
    UiAdminContext().tournament_selected_name = None
    return -1


def input_bettable_outcome():
    """
    UC The admin registers or corrects a bettable score after its completion:
    PRE RUNNING tournament T selected, CLOSED bettable selected
    The admin corrects the final score of the bettable.
    """

    if not UiAdminContext().tournament_selected:
        tournament_selection()
    if UiAdminContext().tournament_selected:
        # Get the bettable of which the start date is overdue and have not outcome
        attr_dicts = Betty().query(f"SELECT b.id, ta.name AS a_team_name, tb.name AS b_team_name, b.start_dt, b.state, p.name AS phase_name, b.outcome"
                                   f" FROM {Bettable._table_} b"
                                   f" JOIN {Team._table_} ta ON ta.id = b.a_team_id"
                                   f" JOIN {Team._table_} tb ON tb.id = b.b_team_id"
                                   f" JOIN {Phase._table_} p ON b.phase_id = p.id AND p.tournament_id={UiAdminContext().tournament_selected_id}"
                                   f" WHERE b.start_dt < '{datetime.datetime.now()}' AND b.outcome IS NULL"
                                   f" ORDER BY b.start_dt ASC")
        if attr_dicts:
            while (selection:=input_selection(attr_dicts, lambda x: display_bettable(x))) >= 0:
                input_outcome(attr_dicts[selection])
                compute_ranking()

if __name__ == '__main__':
    #load_dotenv()
    tournament_selection()
    options = [('Provide/Amend the outcome of a bettable', lambda : input_bettable_outcome()),
               ('Open tournament', lambda : open_tournament()),
               ('Tournament participation', tournament_participation),
               ('Compute ranking', lambda: compute_ranking()),
               ('Show ranking', lambda: show_ranking()),
               ('Status', lambda : betty_status()),
               ('Quit', lambda : quit())]
    selection = 0
    ret = None
    while ret != -1:
        info(f'_____ Selected tournament: {UiAdminContext().tournament_selected_name}')
        selection = input_selection(options, lambda x:x[0], exit_option=6)
        ret = options[selection][1]() # execute the action
