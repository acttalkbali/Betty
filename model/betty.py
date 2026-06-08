from .bet import Bet
from .bettable import Bettable
from .bettor import Bettor
from .bteam import Bteam
from .phase import Phase
from .scoring_rule import ScoringRule
from .sheep_livestock import SheepLivestock
from .sheep_value import SheepValue
from .team import Team
from .tournament import Tournament
from .sql_store import SqlStore

from datetime import datetime, timedelta
from functools import reduce

class Betty:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("CREATING BETTY INSTANCE")
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_store(cls):
        return SqlStore()

    @classmethod
    def private_attribute(cls, attr: str) -> (str, str):
        return attr, '_' + attr

    @classmethod
    def class_entity(cls, pycls) -> str:
        dic ={Tournament: "tournament",
                Phase: "phase",
                Bettable: "bettable",
                Bettor: "bettor",
                Bet: "bet",
                Bteam: "bteam",
                Team: "team",
                SheepLivestock: "sheep_livestock",
                SheepValue: "sheep_value"}
        return dic.get(pycls)

    @classmethod
    def references_by_id(cls, pyclass, prefix='', nullable=False) -> str:
        entity = cls.class_entity(pyclass)
        if prefix:
            prefix += '_'
        return f"{prefix}{entity}_id {'INT' + (' NOT NULL' if not nullable else '')} REFERENCES {entity}(id)"

    @classmethod
    def relates_by_id(cls, pyclass, prefix='') -> str:
        #print(f"relates_by_id {pyclass}")
        entity = cls.class_entity(pyclass)
        if prefix:
            prefix += '_'
        attr = f"{prefix}{entity}_id"
        return attr, f"{attr}"


    def attribute_mapping(self, pycls):
        #print(f"attrinbute_mapping {Tournament} {pycls}")
        return {Tournament:
                     [Betty.private_attribute('name'),
                      Betty.private_attribute('start_dt'),
                      Betty.private_attribute('end_dt'),
                      Betty.private_attribute('state')],
                Phase:
                    [Betty.private_attribute('name'),
                     Betty.relates_by_id(Tournament)],
                Bettable:
                     [Betty.private_attribute('name'),
                      Betty.relates_by_id(Team, "a_"),
                      Betty.relates_by_id(Team, "b_")],
                Bettor:
                     [Betty.private_attribute('name'),
                      Betty.private_attribute('nickname'),
                      Betty.private_attribute('email'),
                      Betty.private_attribute('pwd')],
                Bet:
                     [Betty.private_attribute('prediction'),
                      Betty.private_attribute('')],
                Bteam:
                     [('', '')],
                Team:
                     [Betty.private_attribute('name'),
                      Betty.relates_by_id(Tournament)],

                SheepLivestock:
                     [('', '')],
                SheepValue:
                    [Betty.relates_by_id(Tournament),
                     Betty.relates_by_id(Team),
                     Betty.private_attribute('sheep_value')]
                }.get(pycls)

    @classmethod
    def schema(cls) -> list[str]:
        return [
            #f"""
            #DROP TYPE IF EXISTS TEMPORAL_STATE CASCADE;
            #""",
            #f"""
            #CREATE TYPE TEMPORAL_STATE AS ENUM('open','running','closed');
            #""",
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Tournament)} (
                 id SERIAL PRIMARY KEY,
                 name TEXT NOT NULL UNIQUE,
                 state TEXT, 
                 start_dt TIMESTAMPTZ,
                 end_dt TIMESTAMPTZ
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Phase)} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Tournament)},
                 name TEXT,
                 state TEXT NOT NULL
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Team)} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Tournament)},
                 name TEXT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(SheepValue)} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Tournament)},
                 {cls.references_by_id(Team)},
                 sheep_value INT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Bettable)} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Phase)},
                 {cls.references_by_id(Team, 'a')},
                 {cls.references_by_id(Team, 'b')},
                 start_dt TIMESTAMPTZ,
                 state TEXT NOT NULL
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Bteam)} (
                 id SERIAL PRIMARY KEY,
                 name TEXT UNIQUE NOT NULL
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Bettor)} (
                 id SERIAL PRIMARY KEY,
                 name TEXT NOT NULL,
                 nickname TEXT UNIQUE,
                 email TEXT UNIQUE,
                 pwd TEXT NOT NULL,
                 {cls.references_by_id(Bteam, nullable=True)}
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Bet)} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Bettable)},
                 {cls.references_by_id(Bettor)},
                 prediction INT NOT NULL
                 );
            """
        ]


    @classmethod
    def setup_db(cls):
        commands = [reduce(lambda res, c: res if (c == ' ' and (res=='' or res[-1]==' ')) else res + c,
                           cmd.replace("\n", " "),
                           '')
                    for cmd in cls.schema()]
        print('\n'.join(commands))
        store = cls.get_store()
        if store.run_commands(commands) == True:
            print('SCHEMA CREATED')

    @classmethod
    def query(cls, str) -> list[dict]:
        print(str)
        return self.get_store().query(str)

    @classmethod
    def load(cls, pycls, condition: str):
        self.query(
            f"SELECT * FROM {Betty().class_entity(pycls)}" + (f" WHERE {condition}" if condition else '') + ";")

    @classmethod
    def save(cls, entity) -> int | None:
        pycls = type(entity)
        attr_list = ', '.join(map(lambda x: x[0], Betty().attribute_mapping(pycls)))
        attr_values = ', '.join(map(
            lambda x: "'" + str(getattr(entity, x[1])) + "'",
            Betty().attribute_mapping(pycls)))
        entity = Betty.class_entity(pycls)
        return Betty().get_store().insert_or_update(entity, attr_list, attr_values)

if __name__ == "__main__":
    betty = Betty()

    betty.setup_db()
#    t1 = Tournament(betty, "T1")
#    t2 = Tournament(betty, "T2", datetime.now())
#    t3 = Tournament(betty, "FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21), datetime(day=19, month=7, year=2026, hour=21))
#    print(f'{t1.name} / {t2.name} / {t3.name}')
#    t3.save()
