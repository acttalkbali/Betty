from model.betty import Betty
from model import tournament
from model.bet import Bet
from model.bettable import Bettable
from model.bettor import Bettor
from model.betty import Betty
from model.participation import Participation
from model.phase import Phase
from model.ranking import Ranking
from model.storable import STORABLE_ORDER_DESC, joined_column
from model.team import Team
from model.tournament import Tournament

def query_tournament_bettables_with_teams(tournament_id:int) -> [tuple]:
    return Betty().query(
            f"SELECT ba.id as bettable_id, ba.start_dt, t1.name as t1_name, t2.name as t2_name, ba.outcome, ba.state, ph.id as phase_id, ph.name as phase_name, ph.state as phase_state, ph.scoring "
            f"FROM {Bettable._table_} ba "
            f"JOIN {Phase._table_} ph ON ba.phase_id = ph.id "
            f"JOIN {Team._table_} t1 ON ba.a_team_id = t1.id "
            f"JOIN {Team._table_} t2 ON ba.b_team_id = t2.id "
            f"WHERE ph.tournament_id = {tournament_id} "
            f"ORDER BY ba.start_dt ASC")
    #todo bettables, bettable_attr_dicts = Bettable(phase=Phase(Tournament={UiAdminContext().tournament_selected_id}, team_a=Team(Betty()), team_b=Team(Betty())).load_all(ordering=[('start_dt', 'ASC')])

def query_tournament_bettables(tournament_id:int) -> [tuple]:
    return Betty().query(
            f"SELECT b.id as bettable_id, b.outcome, p.id as phase_id "
            f"FROM {Bettable._table_} b, {Phase._table_} p "
            f"WHERE b.phase_id = p.id AND p.tournament_id = {UiAdminContext().tournament_selected_id} AND b.outcome IS NOT NULL "
            f"ORDER BY b.start_dt ASC")
    #todo bettables, bettable_attr_dicts = Bettable(phase=Phase(Betty(), Tournament={UiAdminContext().tournament_selected_id})).load_all(ordering=[('start_dt', 'ASC')])
