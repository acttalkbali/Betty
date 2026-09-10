from model.betty import Betty
from model import tournament
from model.bet import Bet
from model.bettable import Bettable
from model.bettor import Bettor
from model.betty import Betty
from model.participation import Participation
from model.phase import Phase
from model.ranking import Ranking
from model.sql_store import SqlStore
from model.team import Team

def query_tournament_bettables_with_teams(tournament_id:int) -> [tuple]:
    return SqlStore().run_query(
            f"SELECT ba.id, ba.start_dt, t1.name as t1°name, t2.name as t2°name, ba.outcome, ba.state, ph.id as phase°id, ph.name as phase°name, ph.state as phase°state, ph.scoring as phase°scoring "
            f"FROM {Bettable._table_} ba "
            f"JOIN {Phase._table_} ph ON ba.phase_id = ph.id "
            f"JOIN {Team._table_} t1 ON ba.a_team_id = t1.id "
            f"JOIN {Team._table_} t2 ON ba.b_team_id = t2.id "
            f"WHERE ph.tournament_id = {tournament_id} "
            f"ORDER BY ba.start_dt ASC")
    #todo bettables, bettable_attr_dicts = Bettable(phase=Phase(tournament={UiAdminContext().tournament_selected_id}, team_a=Team(), team_b=Team()).load_all(ordering=[('start_dt', 'ASC')])

def query_tournament_bettables(tournament_id:int) -> [tuple]:
    return SqlStore().run_query(
            f"SELECT b.id as bettable_id, b.start_dt, b.outcome, ph.id as phase°id, ph.name as phase°name, ph.scoring as phase°scoring "
            f"FROM {Bettable._table_} b "
            f"JOIN {Phase._table_} ph ON b.phase_id = ph.id "
            f"WHERE ph.tournament_id = {tournament_id} AND b.outcome IS NOT NULL "
            f"ORDER BY b.start_dt ASC")
    #todo bettables, bettable_attr_dicts = Bettable(phase=Phase(Betty(), Tournament={UiAdminContext().tournament_selected_id})).load_all(ordering=[('start_dt', 'ASC')])
