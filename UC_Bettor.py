from model.betty import Betty, Tournament, Participation, Team, Bet, Bettable, Bettor
from model.phase import Phase
from model.ranking import Ranking
from model.sheep_livestock import SheepLivestock
from model.sheep_value import SheepValue

import ui.console_ui as ui
from model.sql_store import SqlStore

#from dotenv import load_dotenv


#================== UI context
E_PREDICTIONS = ('1', '2', '0', '10', '20', '12')
E_OUTCOMES = ('1', '2', '0')

class UiBettorContext:
    """
    Holds context information relevant for the user interaction
    Attributes may be added during the user interactions
    Singleton class
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            #print("CREATING UiBettorContext")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialised"):
            self.logged_in = None
            self.tournament_selected_name = None # todo may be redundant with self.tournament_selected
            self.tournament_selected_id = None # todo may be redundant with self.tournament_selected
            self.tournament_selected = None
            self.participation_id = None
            self.credit = None
            self._initialised = True

    def reset(self) -> None:
        cls._instance = None

#================== UI control

def register() -> Bettor|None:
    """
    UC Bettor creation:
    A wannabe-bettor registers to the Betty application, setting its email address, password and pseudo.
    """
    name = input("Enter name: ")
    nickname = input("Enter nickname: ")
    email = input("Enter email: ")
    pwd = input("Enter password: ")
    # Todo check email address
    # Todo hide password
    bettor = Bettor(name=name, pwd=pwd, email=email, nickname=nickname)
    if not bettor.save:
        print("Sorry, registration failed") # todo explain why
        return None
    else:
        bettor.save()
        UiBettorContext().logged_in = bettor
        return bettor

def login(bettor_name='', bettor_pwd='') -> Bettor|None:
    """
    UC bettor login:
    A registered bettor logs-in to Betty using its pseudo or email address and password.
    The tournaments to which he is registered are listed.
    POST bettor logged-in
    """
    bettor_name = bettor_name or input("Your name: ")
    bettor_pwd = bettor_pwd or input("Password: ")
    bettor = Bettor(name=bettor_name)
    result = bettor.load()
    if len(result)==1:
        # bettor filled-in successfully
        if bettor.pwd._value != bettor_pwd:
            "Incorrect password. Login denied"
            UiBettorContext().logged_in = None
            return None
        else:
            UiBettorContext().logged_in = bettor
            ui.info(f"Welcome {bettor_name}, you are now logged in")
            #print(f"logged_in = {UiBettorContext().logged_in}")
            return bettor
    else:
        ui.error_msg(f"{bettor_name} is not registered")
        if ui.yes_no("Do you want to register? "):
            return register()

def logout(bettor:Bettor)->int:
    """
    UC bettor logout:
    A registered bettor logs-out from Betty
    POST bettor logged-out
    """
    UiBettorContext().logged_out = False
    UiBettorContext().tournament_selected_name = None
    return -1

def tournament_registration(bettor:Bettor)->None:
    """
    UC Tournament registration:
    PRE bettor logged-in
    Betty selects the open tournaments
    The bettor selects the open tournament into which he wants to participate (automatic selection if only one tournament opened)
    The bettor wallet is credited with the Tournament's setup wallet.
    """
    if  UiBettorContext().logged_in:
        # Select the existing future or ongoing tournaments to which the bettor hasn't yet registered to
        attr_dicts = SqlStore().run_query(f"SELECT tr.id,tr.name,tr.start_dt,tr.end_dt,tr.sheep_credit,p.bettor_id FROM {Tournament._table_} tr FULL JOIN participation p ON p.bettor_id = {bettor.id} AND p.tournament_id=tr.id WHERE p.tournament_id IS NULL AND end_dt > NOW() ORDER BY tr.start_dt;") # AND p.bettor_id={UiBettorContext().logged_in.id}
        # filter out already registered tournaments
        attr_dicts = list(filter(lambda x: x['bettor_id'] != UiBettorContext().logged_in.id, attr_dicts))
        if len(attr_dicts)==0:
            ui.info("Sorry, there currently is no other tournament available for registration")
        else:
            selection = ui.input_selection(attr_dicts, lambda attr_dict: attr_dict['name'])
            if selection >= 0:
                tournament = Tournament(id=attr_dicts[selection]['id'])
                participation = Participation(bettor=bettor, tournament=tournament, credit=attr_dicts[selection]['sheep_credit'])
                participation.save()
                UiBettorContext().tournament_selected_name = attr_dicts[selection]['name']
                UiBettorContext().tournament_selected_id = attr_dicts[selection]['id']
                print(f"Selected tournament : {UiBettorContext().tournament_selected_id}")
                UiBettorContext().participation_id = participation.id
                UiBettorContext().credit = attr_dicts[selection]['sheep_credit']

def tournament_selection(bettor:Bettor, states:list[str]=None) -> int:
    """
    UC tournament selection:
    PRE bettor logged-in
    The bettor selects an open tournament from those to which he has registered.
    POST Tournament selected
    """
    if  UiBettorContext().logged_in:
        states_condition = f" AND tr.state IN ({str(states)[1:-1]})" if states else ''
        attr_dicts = SqlStore().run_query(f"SELECT tr.id, tr.name, p.id AS participation_id, p.credit FROM participation p LEFT JOIN {Tournament._table_} tr ON p.tournament_id=tr.id WHERE p.bettor_id={bettor.id} {states_condition}")
        if len(attr_dicts)==0:
            if ui.yes_no("You have no ongoing tournament. Register to one?"):
                tournament_registration(bettor)
        else:
            if len(attr_dicts) > 1:
                selection = ui.input_selection(attr_dicts, lambda attr_dict: attr_dict['name'])
            else:
                ui.info("You have no other ongoing tournament. Consider registering to one if you so wish.")
                selection = 0
            UiBettorContext().tournament_selected_name = attr_dicts[selection]['name']
            UiBettorContext().tournament_selected_id = attr_dicts[selection]['id']
            UiBettorContext().tournament_selected = Tournament(name=attr_dicts[selection]['name'], id=attr_dicts[selection]['id'])
            print(f"Selected tournament : {UiBettorContext().tournament_selected_id}")
            UiBettorContext().participation_id = attr_dicts[selection]['participation_id']
            UiBettorContext().credit = attr_dicts[selection]['credit']
            return selection
    return -1


"""
todo
UC BTeam setup:
The admin creates a BTeam and assigns some registered bettors to it
"""

def buy_sheeps(bettor:Bettor):
    """
    UC The Bettor constitutes its sheep livestock
    PRE bettor logged in, OPEN tournament T selected,
    The Bettor buys sheep. Its wallet is debited accordingly
    """
    if  UiBettorContext().logged_in:
        if not UiBettorContext().tournament_selected_id:
            ui.info("Select a tournament first")
        else:
            tournament_id = UiBettorContext().tournament_selected_id
            # Retrieve the teams value for this tournament

            attr_dicts = SqlStore().run_query(
                f"SELECT t.id, t.name, s.sheep_value, s.id FROM {Team._table_} t, {SheepValue._table_} s WHERE s.tournament_id={tournament_id} AND s.team_id = t.id  ORDER BY s.sheep_value DESC"
            )
            # Choose from the applicable OPEN bettables??
            # load the bettor sheep livestock
            lvs_attr_dicts = SqlStore().run_query(
                f"SELECT t.id, t.name, l.quantity, s.id FROM {SheepLivestock._table_} l, {SheepValue._table_} s, team t WHERE s.tournament_id={tournament_id} AND s.id = l.sheep_value_id AND l.bettor_id = {bettor.id} AND t.id = s.team_id ORDER BY s.sheep_value DESC"
            )
            livestock = {attr_dict['name']:attr_dict['quantity'] for attr_dict in lvs_attr_dicts }
            while True:
                choices = []
                participation = Participation(id=UiBettorContext().participation_id)
                participation.load()
                credit = participation.credit._value #UiBettorContext().credit
                ui.info(f"Your credit: {credit}")
                for attr_dict in attr_dicts:
                    max_sheeps = credit // int(attr_dict['sheep_value'])
                    qty = livestock.get(attr_dict['name'], '')
                    team_sheep_value = f"{attr_dict['name']} value {attr_dict['sheep_value']} (max {max_sheeps}) "
                    choices.append(team_sheep_value + ('.' * (45 - len(team_sheep_value))) + f" {qty if qty else '':2}")

                selection = ui.input_selection(choices, lambda x: x)
                if selection >= 0:
                    max_sheeps = credit // int(attr_dicts[selection]['sheep_value'])
                    n = ui.input_int(f"Number of sheeps to buy (max {max_sheeps} according to your current credit ({credit})", 0, max_sheeps)
                    # Update credit accordingly
                    UiBettorContext().credit -= n * int(attr_dicts[selection]['sheep_value'])
                    sheep_livestock = SheepLivestock(sheep_value=attr_dicts[selection]['id'], bettor=bettor.id, quantity=n)
                    sheep_livestock.save()
                    livestock[attr_dicts[selection]['name']] = n
                    participation.credit._value = UiBettorContext().credit
                    participation.save()
                else:
                    break
            # todo update credit along the livestock update
            #if selection >= 0:
            #    participation = Participation(id=UiBettorContext().participation_id)
            #    participation.load()
            #    participation.credit = UiBettorContext().credit
            #    participation.save()


def bet(bettor:Bettor):
    """
    UC Bet:
    PRE bettor logged-in, OPEN/RUNNING tournament T selected
    The bettor enters its bet for any of the OPEN available T bettable
    """
    if  UiBettorContext().logged_in:
        if not UiBettorContext().tournament_selected_id:
            tournament_selection(bettor, ['OPEN', 'RUNNING'])
        if UiBettorContext().tournament_selected_id:
            attr_dicts = SqlStore().run_query(f"SELECT b.id, b.a_team_id, b.b_team_id, b.start_dt, p.id AS phase_id \
                                         FROM {Bettable._table_} b, {Phase._table_} p, {Tournament._table_} tr \
                                         WHERE b.phase_id=p.id AND p.tournament_id = tr.id \
                                           AND p.tournament_id={UiBettorContext().tournament_selected_id} \
                                           AND b.start_dt > NOW() \
                                         ORDER BY b.start_dt ASC")

            # Choose from the applicable OPEN bettables
            choices = []
            for attr_dict in attr_dicts:
                #print(attr_dicts)
                team_a = Team(id=attr_dict['a_team_id'])
                team_b = Team(id=attr_dict['b_team_id'])
                team_a.load()
                team_b.load()
                bettable = Bettable(phase=attr_dict['phase_id'], team_a=team_a, team_b=team_b, start_dt=attr_dict['start_dt'], id=attr_dict['id'])
                bet = Bet(bettor=bettor, bettable=bettable)
                result = bet.load() # load the bet if it already exists
                choices.append((bettable,bet))
                #choices.append(f"{attr_dict['start_dt']} : {team_a.name} - {team_b.name}")
            selection = ui.input_selection(choices, lambda x: f"{x[0]._start_dt} {x[0]._a_team._referred._name._value} - {x[0]._b_team._referred._name._value}" + (f" << {x[1]._prediction._value} >>" if x[1]._prediction._value else ''))

            if selection >= 0:
                while (prediction:= input(f"{choices[selection][0]} result prediction (1=A wins | 2=B wins | 12=A or B wins | 10=A wins or draw | 20=B wins or draw | 0 draw): ").strip()) not in ['', '0', '1', '2', '12', '10', '20']:
                    pass # Not a valid entry, just try again
                if prediction != '':
                    choices[selection][1]._prediction._value = int(prediction)
                    choices[selection][1].save()
                    ui.info("Your prediction has been recorded")
        else:
            ui.error_msg("Yor must first select a tournament")
    else:
        ui.error_msg("You must be logged in to make a bet")

def calculate_score(prediction:int, outcome:int) -> int:
    s_prediction = str(prediction)
    s_outcome = str(outcome)
    if prediction == outcome:
        return 6
    elif len(s_prediction)==2 and s_outcome in s_prediction:
        return 3
    else:
        return 0

def tournament_status():
    """
    UC Tournament status:
    PRE bettor logged-in, OPEN tournament T selected
    The bettor choose 'tournament status' from the available actions.
    The tournament's bettable are listed in accordance with their status
    """
    if  UiBettorContext().logged_in:
        if not UiBettorContext().tournament_selected_id:
            tournament_selection(bettor, ['OPEN', 'RUNNING'])
        if UiBettorContext().tournament_selected_id:
            attr_dicts = SqlStore().run_query(f"SELECT b.id, b.a_team_id, b.b_team_id, b.start_dt, b.state, b.outcome, bt.prediction"
                                       f" FROM {Bettable._table_} b"
                                       f" JOIN {Phase._table_} p ON b.phase_id = p.id"
                                       f" JOIN {Tournament._table_} tr ON p.tournament_id=tr.id"
                                       f" FULL JOIN {Bet._table_} bt ON bt.bettable_id=b.id"
                                       f" ORDER BY b.start_dt ASC")
            for attr_dict in attr_dicts:
                team_a = Team(id=attr_dict['a_team_id'])
                team_b = Team(id=attr_dict['b_team_id'])
                team_a.load()
                team_b.load()
                bettable_str = f"{attr_dict['start_dt']} : {team_a} - {team_b}"
                if attr_dict['prediction'] or attr_dict['outcome']:
                    bettable_str += " " + ('.' * (70 - len(bettable_str)))
                    bettable_str += f"{attr_dict['prediction']:3}" if attr_dict['prediction'] else "   "
                    bettable_str += f"{attr_dict['outcome']:3}" if attr_dict['outcome'] else "   "
                    if attr_dict['prediction'] and attr_dict['outcome']:
                        bettable_str += f" => {calculate_score(attr_dict['prediction'], attr_dict['outcome'])} points"
                print(bettable_str)


def show_ranking(bettor:Bettor):
    """
    UC Tournament ranking:
    PRE bettor logged-in, OPEN tournament T selected
    The bettor choose 'tournament ranking' from the available actions.
    The tournament's current bettor ranking is listed.
    """
    if UiBettorContext().logged_in:
        if UiBettorContext().tournament_selected_id:
            attr_dicts = SqlStore().run_query(
                f"SELECT r.id, b.nickname, r.tournament_id, r.score, r.rank "
                f"FROM {Ranking._table_} r, {Tournament._table_} tr, {Bettor._table_} b "
                f"WHERE r.tournament_id={UiBettorContext().tournament_selected_id} "
                f"ORDER BY r.score DESC")

            print(f"\n========== {UiBettorContext().tournament_selected_name} RANKING ==========")
            prv_score = ''
            ranking = 1
            for rank,attr_dict in enumerate(attr_dicts):
                if attr_dict['score'] != prv_score:
                    # Not an ex-aequo
                    prv_score = attr_dict['score']
                    ranking = rank + 1
                print(f"{ranking:3} {attr_dict['nickname']:20} {attr_dict['score']:3} points")


if __name__ == '__main__':
    #load_dotenv()
    #bettor = login('wys','wys') # todo remove these hard-coded parameter values
    bettor = login() # todo remove these hard-coded parameter values
    if bettor:
        tournament_selection(bettor)
        options = [('Make a bet', lambda : bet(bettor)),
                   ('Show ranking', lambda : show_ranking(bettor)),
                   ('Buy sheeps', lambda : buy_sheeps(bettor)),
                   ('Status', lambda : tournament_status()),
                   ('Switch to another tournament', lambda: tournament_selection(bettor, ["OPEN", "RUNNING"])),
                   ('Register to another tournament', lambda : tournament_registration(bettor)),
                   ('Logout', lambda : logout(bettor))]
        selection = 0
        ret = None
        while ret != -1:
            ui.info(f'_____ Selected tournament: {UiBettorContext().tournament_selected_name}')
            selection = ui.input_selection(options, lambda x:x[0], exit_option=6)
            ret = options[selection][1]() # execute the action
