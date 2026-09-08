from model.storable import Field, Storable, STORABLE_ENTITY_ATTR_NAME
from .bet import Bet
from .bettable import Bettable
from .bettor import Bettor
from .bteam import Bteam
from .phase import Phase
from .scoring_rule import ScoringRule
from .sheep_livestock import SheepLivestock
from .team import Team
from .tournament import Tournament
from .sheep_value import SheepValue
from .participation import Participation
from .ranking import Ranking
from .sql_store import SqlStore

from datetime import datetime, timedelta
from functools import reduce

class Betty:

    _instance = None
    _debug = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            if cls._debug: print("CREATING BETTY INSTANCE")
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_store(cls):
        return SqlStore()

    @classmethod
    def references_by_id(cls, pyclass, prefix='', nullable=False) -> str:
        entity = pyclass._table_
        if prefix:
            prefix += '_'
        return f"{prefix}{entity}_id {'INT' + (' NOT NULL' if not nullable else '')} REFERENCES {entity}(id)"


    @classmethod
    def schema(cls) -> list[str]:
        """
        :return: the commands to create the DB
        """
        return [
            #f"""
            #DROP TYPE IF EXISTS TEMPORAL_STATE CASCADE;
            #""",
            #f"""
            #CREATE TYPE TEMPORAL_STATE AS ENUM('open','running','closed');
            #""",
            f"""
            CREATE TABLE IF NOT EXISTS {Tournament._table_} (
                 id SERIAL PRIMARY KEY,
                 name TEXT NOT NULL UNIQUE,
                 state TEXT, 
                 start_dt TIMESTAMPTZ,
                 end_dt TIMESTAMPTZ,
                 sheep_credit INT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {Phase._table_} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Tournament)},
                 name TEXT,
                 state TEXT NOT NULL,
                 scoring TEXT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {Team._table_} (
                 id SERIAL PRIMARY KEY,
                 name TEXT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {SheepValue._table_} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Tournament)},
                 {cls.references_by_id(Team)},
                 sheep_value INT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {Bettable._table_} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Phase)},
                 {cls.references_by_id(Team, 'a')},
                 {cls.references_by_id(Team, 'b')},
                 start_dt TIMESTAMPTZ,
                 state TEXT NOT NULL,
                 outcome TEXT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {Bteam._table_} (
                 id SERIAL PRIMARY KEY,
                 name TEXT UNIQUE NOT NULL
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {Bettor._table_} (
                 id SERIAL PRIMARY KEY,
                 name TEXT NOT NULL,
                 nickname TEXT UNIQUE,
                 email TEXT UNIQUE,
                 pwd TEXT NOT NULL,
                 {cls.references_by_id(Bteam, nullable=True)}
                 );
            """,
            f"""
              CREATE TABLE IF NOT EXISTS {SheepLivestock._table_} (
                   id SERIAL PRIMARY KEY,
                   {cls.references_by_id(Bettor)},
                   {cls.references_by_id(SheepValue)},
                   quantity INT
                   );
              """,
            f"""
             CREATE TABLE IF NOT EXISTS {Participation._table_} (
                  id SERIAL PRIMARY KEY,
                  {cls.references_by_id(Tournament)},
                  {cls.references_by_id(Bettor)},
                  credit INT,
                  score FLOAT
                  );
             """,
            f"""
            CREATE TABLE IF NOT EXISTS {Bet._table_} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Bettable)},
                 {cls.references_by_id(Bettor)},
                 prediction TEXT,
                 score FLOAT,
                 CONSTRAINT UC_Bet UNIQUE ({Bettable._table_}_id,{Bettor._table_}_id)
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {Ranking._table_} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Tournament)},
                 {cls.references_by_id(Bettor)},
                 rank INT NOT NULL,
                 score FLOAT,
                 UNIQUE ({cls.references_by_id(Tournament)}, {cls.references_by_id(Bettor)})
                 );
            """
        ]

    @classmethod
    def setup_db(cls): # todo move to sql_store
        commands = [reduce(lambda res, c: res if (c == ' ' and (res=='' or res[-1]==' ')) else res + c,
                           cmd.replace("\n", " "),
                           '')
                    for cmd in cls.schema()]
        if cls._debug: print('\n'.join(commands))
        store = cls.get_store()
        if store.run_commands(commands) == True:
            if cls._debug: print('SCHEMA CREATED')

    @classmethod
    def drop_db(cls): # todo move to sql_store
        """
        Run the commands to delete the DB
        :return: None
        """

        commands = [f"DROP TABLE IF EXISTS {table} CASCADE;" for table in Storable.entities.values()]
        if cls._debug: print(f'betty: {commands}')
        store = cls.get_store()
        if store.run_commands(commands, force_debug=True) == True:
            if cls._debug: print('DB TABLES DROPPED')


if __name__ == "__main__":
    betty = Betty()
    betty.setup_db()

