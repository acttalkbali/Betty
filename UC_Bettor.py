from model.betty import Betty, Tournament, Participation, Team, Bet, Bettable, Bettor

#from dotenv import load_dotenv

def input_selection(options, fn):
    print("0: exit menu")
    for i, option in enumerate(options):
        print(f"{i+1}: {fn(option)}")
    # todo check input value
    return int(input("Your selection: "))-1 # -1 so it can be used as an index

def error_msg(msg):
    print(f"*** {msg} ***")

def yes_no(question):
    while (answer:=(input(f"{question} [y/n] : ").lower())) not in ['y', 'n']:
        pass
    print(f"yesno <{answer}>")
    return answer == 'y'

def info(msg:str):
    print(msg)

"""
UC Bettor creation:
A wannabe-bettor registers to the Betty application, setting its email address, password and pseudo.
"""
def register() -> Bettor|None:
    name = input("Enter name: ")
    nickname = input("Enter nickname: ")
    email = input("Enter email:")
    pwd = input("Enter password: ")
    # Todo check email address
    # Todo hide password
    bettor = Bettor(Betty(), name, pwd, email, nickname)
    if not bettor.save:
        print("Sorry, registration failed") # todo explain why
        return None
    else:
        bettor.save()
        bettor.logged_in = True
        return bettor


"""
UC bettor login:
A registered bettor logs-in to Betty using its pseudo or email address and password.
The tournaments to which he is registered are listed.
POST bettor logged-in
"""
def login(bettor_name, bettor_pwd) -> Bettor|None:
    bettor_name = bettor_name or input("Your name: ")
    bettor_pwd = bettor_pwd or input("Password: ")
    bettor = Bettor(Betty(), name=bettor_name)
    result = bettor.load()
    if len(result)==1:
        # bettor filled-in successfully
        if bettor._pwd != bettor_pwd:
            "Incorrect password. Login denied"
            bettor.logged_in = False
            return None
        else:
            bettor.logged_in = True
            info("You are logged in")
            return bettor
    else:
        error_msg(f"{bettor_name} is not registered")
        if yes_no("Do you want to register? "):
            return register()

"""
UC Tournament registration:
PRE bettor logged-in
Betty selects the open tournaments
The bettor selects the open tournament into which he wants to participate (automatic selection if only one tournament opened)
The bettor wallet is credited with the Tournament's setup wallet.
"""
def tournament_registration(bettor):
    if bettor.logged_in:
        attr_dicts = Betty().query("SELECT id,name,start_dt,end_dt FROM tournament WHERE end_dt > NOW()")
        selection = input_selection(attr_dicts, lambda attr_dict: attr_dict['name'])
        if selection >= 0:
            tournament = Tournament(Betty(),id=attr_dicts[selection]['id'])
            participation = Participation(Betty(), bettor, tournament)
            participation.save()

"""
UC tournament selection:
PRE bettor logged-in
The bettor selects an open tournament from those to which he has registered.
POST Tournament selected
"""
def tournament_selection(bettor, states:list[str]=None) -> int:
    if bettor.logged_in:
        states_condition = f" AND t.state IN ({str(states)[1:-1]})" if states else ''
        attr_dicts = Betty().query(f"SELECT t.id,t.name FROM participation p, tournament t WHERE p.bettor_id={bettor.id} {states_condition}")
        if len(attr_dicts) > 1:
            selection = input_selection(attr_dicts, lambda attr_dict: attr_dict['t.name'])
            bettor.tournament_selected = attr_dicts[selection]['t.name']
        elif len(attr_dicts)==1:
            bettor.tournament_selected = attr_dicts[0]
        else:
            if yes_no("You have no ongoing tournament. Register to one?"):
                tournament_registration(bettor)


"""
UC BTeam setup:
The admin creates a BTeam and assigns some registered bettors to it
"""

"""
UC The Bettor sets up its sheep livestock
PRE bettor logged in, OPEN tournament T selected,
The Bettor buys sheep. Its wallet is debited accordingly
"""

"""
UC Bet:
PRE bettor logged-in, OPEN/RUNNING tournament T selected
The bettor enters its bet for any of the OPEN available T bettable
"""
def bet(bettor):
    if bettor.logged_in:
        if not bettor.tournament_selection:
            tournament_selection(bettor, ['OPEN', 'RUNNING'])
        if bettor.tournament_selected:
            attr_dicts = Betty().query(f"SELECT b.id, b.team_a_id, b.team_b_id, start_dt FROM bettable b, tournament tr WHERE b.tournament_id=tr.id AND b.start_dt < NOW() ORDER BY b.start_dt ASC")
            Betty().query("SELECT t")
            choices = []
            for attr_dict in attr_dicts:
                team_a = Team(Betty(), id=attr_dict['b.team_a_id'])
                team_b = Team(Betty(), id=attr_dict['b.team_b_id'])
                team_a = team_a.load_by_id()
                team_b = team_b.load_by_id()
                choices.append(f"{attr_dict['start_dt']} : {team_a} - {team_b}")

            selection = input_selection(choices, lambda x: x)
            if selection > 0:
                prediction = input(f"{choices[selection]} result prediction (0=nul, 1=A , 2=B, 12=A or B, 10=A or nul, 20=B or nul")
                Bet(Betty(), bettor, tuples[selection][0], prediction).save()

"""
UC Tournament status:
PRE bettor logged-in, OPEN tournament T selected
The bettor choose 'tournament status' from the available actions.
The tournament's bettable are listed in accordance with their status
"""

"""
UC Tournament ranking:
PRE bettor logged-in, OPEN tournament T selected
The bettor choose 'tournament ranking' from the available actions.
The tournament's current bettor ranking is listed. 
"""
def show_ranking(bettor):
    if bettor.logged_in:


if __name__ == '__main__':
    #load_dotenv()
    bettor = login('wys','wys')
    tournament = tournament_selection(bettor)
    input_selection([(
        'Make a bet', lambda : bet(bettor)),
        'Show ranking', lambda : ])