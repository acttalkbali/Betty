from model.betty import Betty, Tournament, Participation, Team, Bet, Bettable, Bettor
from model.sheep_livestock import SheepLivestock
from model.sheep_value import SheepValue


#from dotenv import load_dotenv

#================== Basic UI console functions

def int_or_none(s:str)->int|None:
    """
    converts and returns the supplied string to an int if it represents a valid number, or else return None
    :param s:
    :return:
    """
    try:
        n = int(s)
    except:
        n = None
    return n

def input_int(prompt:str, n_min:int, n_max:int)->int:
    """
    Request an int in the range [n_min .. n_max]
    :param prompt: The prompt to display
    :param n_min:
    :param n_max:
    :return:
    """
    n = None
    while n is None or n < n_min or n > n_max:
        n = int_or_none(input(f"{prompt} [{n_min}-{n_max}] : "))
    return n

def input_selection(options:list[Any], fn: callable, exit_option=0)->int:
    """
    :param options:
    :param fn: a 'key' function for the option, used for display
    :return: -1 if exit menu selected else the index of the chosen selection
    """
    if exit_option == 0:
        print("0: exit menu")

    for i, option in enumerate(options):
        print(f"{i+1}: {fn(option)}")

    return input_int("Your selection", 0 if exit_option==0 else 1, len(options))-1 # -1 so it can be used as an index

def error_msg(msg:str)->None:
    """
    Displays an error message
    :param msg:
    :return:
    """
    print(f"*** {msg} ***")

def yes_no(question:str) -> bool:
    """
    Input a yes / no choice
    :param question: the question for which the response is due
    :return: True if answer is yes, False if the answer is no
    """
    answer = ''
    while answer not in ['y', 'n']:
        answer = input(f"{question} [y/n] : ").lower()
    return answer == 'y'

def info(msg:str)->None:
    """
    displays an informational message
    :param msg:
    :return:
    """
    print(msg)

#================== UI context

class UiBettorContext:
    """
    Holds context information relevant for the user interaction
    Attributes may be added during the user interactions
    Singleton class
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("CREATING UiBettorContext")
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
    bettor = Bettor(Betty(), name, pwd, email, nickname)
    if not bettor.save:
        print("Sorry, registration failed") # todo explain why
        return None
    else:
        bettor.save()
        UiBettorContext().logged_in = bettor
        return bettor

def login(bettor_name, bettor_pwd) -> Bettor|None:
    """
    UC bettor login:
    A registered bettor logs-in to Betty using its pseudo or email address and password.
    The tournaments to which he is registered are listed.
    POST bettor logged-in
    """
    bettor_name = bettor_name or input("Your name: ")
    bettor_pwd = bettor_pwd or input("Password: ")
    bettor = Bettor(Betty(), name=bettor_name)
    result = bettor.load()
    if len(result)==1:
        # bettor filled-in successfully
        if bettor._pwd._value != bettor_pwd:
            "Incorrect password. Login denied"
            UiBettorContext().logged_in = None
            return None
        else:
            UiBettorContext().logged_in = bettor
            info("You are logged in")
            print(f"logged_in = {UiBettorContext().logged_in}")
            return bettor
    else:
        error_msg(f"{bettor_name} is not registered")
        if yes_no("Do you want to register? "):
            return register()

def logout(bettor)->int:
    """
    UC bettor logout:
    A registered bettor logs-out from Betty
    POST bettor logged-out
    """
    UiBettorContext().logged_out = False
    UiBettorContext().tournament_selected_name = None
    return -1

def tournament_registration(bettor)->None:
    """
    UC Tournament registration:
    PRE bettor logged-in
    Betty selects the open tournaments
    The bettor selects the open tournament into which he wants to participate (automatic selection if only one tournament opened)
    The bettor wallet is credited with the Tournament's setup wallet.
    """
    if  UiBettorContext().logged_in:
        # Select the existing future or ongoing tournaments to which the bettor hasn't yet registered to
        attr_dicts = Betty().query(f"SELECT tr.id,tr.name,tr.start_dt,tr.end_dt,tr.sheep_credit,p.bettor_id FROM tournament tr FULL JOIN participation p ON p.tournament_id=tr.id WHERE p.tournament_id IS NULL AND end_dt > NOW() ORDER BY tr.start_dt;") # AND p.bettor_id={UiBettorContext().logged_in.id}
        # filter out already registered tournaments
        attr_dicts = list(filter(lambda x: x['bettor_id'] != UiBettorContext().logged_in.id, attr_dicts))
        if len(attr_dicts)==0:
            info("Sorry, there are no other tournament(s) to register to")
        else:
            selection = input_selection(attr_dicts, lambda attr_dict: attr_dict['name'])
            if selection >= 0:
                tournament = Tournament(Betty(),id=attr_dicts[selection]['id'])
                participation = Participation(Betty(), bettor, tournament, credit=attr_dicts[selection]['sheep_credit'])
                participation.save()
                UiBettorContext().tournament_selected_name = attr_dicts[selection]['name']
                UiBettorContext().tournament_selected_id = attr_dicts[selection]['id']
                print(f"Selected tournament : {UiBettorContext().tournament_selected_id}")
                UiBettorContext().participation_id = participation.id
                UiBettorContext().credit = attr_dicts[selection]['sheep_credit']

def tournament_selection(bettor, states:list[str]=None) -> int:
    """
    UC tournament selection:
    PRE bettor logged-in
    The bettor selects an open tournament from those to which he has registered.
    POST Tournament selected
    """
    if  UiBettorContext().logged_in:
        states_condition = f" AND tr.state IN ({str(states)[1:-1]})" if states else ''
        attr_dicts = Betty().query(f"SELECT tr.id, tr.name, p.id AS participation_id, p.credit FROM participation p LEFT JOIN tournament tr ON p.tournament_id=tr.id WHERE p.bettor_id={bettor.id} {states_condition}")
        if len(attr_dicts)==0:
            if yes_no("You have no ongoing tournament. Register to one?"):
                tournament_registration(bettor)
        else:
            if len(attr_dicts) > 1:
                selection = input_selection(attr_dicts, lambda attr_dict: attr_dict['name'])
            else:
                selection = 0
            UiBettorContext().tournament_selected_name = attr_dicts[selection]['name']
            UiBettorContext().tournament_selected_id = attr_dicts[selection]['id']
            UiBettorContext().tournament_selected = Tournament(Betty(), name=attr_dicts[selection]['name'], id=attr_dicts[selection]['id'])
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

def buy_sheeps(bettor):
    """
    UC The Bettor constitutes its sheep livestock
    PRE bettor logged in, OPEN tournament T selected,
    The Bettor buys sheep. Its wallet is debited accordingly
    """
    if  UiBettorContext().logged_in:
        if not UiBettorContext().tournament_selected_id:
            info("Select a tournament first")
        else:
            tournament_id = UiBettorContext().tournament_selected_id
            # Retrieve the teams value for this tournament

            attr_dicts = Betty().query(
                f"SELECT t.id, t.name, s.sheep_value, s.id FROM team t, sheep_value s WHERE s.tournament_id={tournament_id} AND s.team_id = t.id  ORDER BY s.sheep_value DESC"
            )
            # Choose from the applicable OPEN bettables??
            # load the bettor sheep livestock
            lvs_attr_dicts = Betty().query(
                f"SELECT t.id, t.name, l.quantity, s.id FROM sheep_livestock l, sheep_value s, team t WHERE s.tournament_id={tournament_id} AND s.id = l.sheep_value_id AND l.bettor_id = {bettor.id} AND t.id = s.team_id ORDER BY s.sheep_value DESC"
            )
            livestock = {attr_dict['name']:attr_dict['quantity'] for attr_dict in lvs_attr_dicts }
            while True:
                choices = []
                participation = Participation(Betty(), id=UiBettorContext().participation_id)
                participation.load()
                credit = participation._credit._value #UiBettorContext().credit
                info(f"Your credit: {credit}")
                for attr_dict in attr_dicts:
                    max_sheeps = credit // int(attr_dict['sheep_value'])
                    qty = livestock.get(attr_dict['name'], '')
                    choices.append(f"{attr_dict['name']} value {attr_dict['sheep_value']} (max {max_sheeps})" + (f" <<--- {qty} --->>" if qty else ""))

                selection = input_selection(choices, lambda x: x)
                if selection >= 0:
                    max_sheeps = credit // int(attr_dicts[selection]['sheep_value'])
                    n = input_int(f"Number of sheeps to buy (max {max_sheeps} according to your current credit ({credit})", 0, max_sheeps)
                    # Update credit accordingly
                    UiBettorContext().credit -= n * int(attr_dicts[selection]['sheep_value'])
                    sheep_livestock = SheepLivestock(Betty(), sheep_value=attr_dicts[selection]['id'], bettor=bettor.id, quantity=n)
                    sheep_livestock.save()
                    livestock[attr_dicts[selection]['name']] = n
                else:
                    break
            if selection >= 0:
                participation = Participation(Betty(), id=UiBettorContext().participation_id)
                participation.load()
                participation.credit = UiBettorContext().credit
                participation.save()


def bet(bettor):
    """
    UC Bet:
    PRE bettor logged-in, OPEN/RUNNING tournament T selected
    The bettor enters its bet for any of the OPEN available T bettable
    """
    if  UiBettorContext().logged_in:
        if not UiBettorContext().tournament_selected_id:
            tournament_selection(bettor, ['OPEN', 'RUNNING'])
        if UiBettorContext().tournament_selected_id:
            attr_dicts = Betty().query(f"SELECT b.id, b.a_team_id, b.b_team_id, b.start_dt, p.id AS phase_id FROM bettable b, phase p, tournament tr WHERE b.phase_id=p.id AND p.tournament_id = tr.id AND p.tournament_id={UiBettorContext().tournament_selected_id} AND b.start_dt > NOW() ORDER BY b.start_dt ASC")

            # Choose from the applicable OPEN bettables
            choices = []
            for attr_dict in attr_dicts:
                print(attr_dicts)
                team_a = Team(Betty(), id=attr_dict['a_team_id'])
                team_b = Team(Betty(), id=attr_dict['b_team_id'])
                team_a.load()
                team_b.load()
                bettable = Bettable(Betty(), attr_dict['phase_id'], team_a, team_b, attr_dict['start_dt'], id=attr_dict['id'])
                bet = Bet(Betty(), bettor, bettable)
                result = bet.load() # load the bet if it already exists
                choices.append((bettable,bet))
                #choices.append(f"{attr_dict['start_dt']} : {team_a.name} - {team_b.name}")
            selection = input_selection(choices, lambda x: f"{x[0]._start_dt} {x[0]._a_team._referred._name._value} - {x[0]._b_team._referred._name._value}" + (f" << {x[1]._prediction._value} >>" if x[1]._prediction._value else ''))

            if selection >= 0:
                prediction = input(f"{choices[selection][0]} result prediction (1=A, 2=B, 12=A or B, 10=A or draw, 20=B or draw): ")
                choices[selection][1]._prediction._value = int(prediction)
                choices[selection][1].save()
                info("Your prediction has been registered")
        else:
            error_msg("Yor must first select a tournament")
    else:
        error_msg("You must be logged in to make a bet")

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
            attr_dicts = Betty().query(f"SELECT b.id, b.a_team_id, b.b_team_id, b.start_dt, b.state FROM bettable b, phase p, tournament tr WHERE b.phase_id = p.id AND p.tournament_id=tr.id ORDER BY b.start_dt ASC")
            for attr_dict in attr_dicts:
                team_a = Team(Betty(), id=attr_dict['a_team_id'])
                team_b = Team(Betty(), id=attr_dict['b_team_id'])
                team_a.load()
                team_b.load()
                print(f"{attr_dict['start_dt']} : {team_a} - {team_b}")


def show_ranking(bettor):
    """
    UC Tournament ranking:
    PRE bettor logged-in, OPEN tournament T selected
    The bettor choose 'tournament ranking' from the available actions.
    The tournament's current bettor ranking is listed.
    """
    if UiBettorContext().logged_in:
        if UiBettorContext().tournament_selected_id:
            attr_dicts = Betty().query(
                f"SELECT r.id, b.nickname, r.tournament_id, r.score, r.rank FROM ranking r, tournament tr, bettor b WHERE r.tournament_id={UiBettorContext().tournament_selected_id} ORDER BY r.score DESC")

            print(f"========== {UiBettorContext().tournament_selected_name} RANKING ==========")
            prv_score = ''
            for rank,attr_dict in enumerate(attr_dicts):
                if attr_dict['r.score'] != prv_score:
                    prv_score = attr_dict['score']
                    ranking = rank + 1
                print(f"{ranking:3} {attr_dict['b.nickname']:20} {attr_dict['score']:3} points")


if __name__ == '__main__':
    #load_dotenv()
    bettor = login('wys','wys') # todo remove these hard-coded parameter values
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
        info(f'_____ Selected tournament: {UiBettorContext().tournament_selected_name}')
        selection = input_selection(options, lambda x:x[0], exit_option=6)
        ret = options[selection][1]() # execute the action
