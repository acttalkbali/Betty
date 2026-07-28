from model.storable import DbFieldType, Field
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

    entities_mapping = {
           Tournament: "tournament",
           Phase: "phase",
           Bettable: "bettable",
           Bettor: "bettor",
           Participation: 'participation',
           Bet: "bet",
           Bteam: "bteam",
           Team: "team",
           SheepLivestock: "sheep_livestock",
           SheepValue: "sheep_value",
           Ranking: "ranking"
           }

    @classmethod
    def class_entity(cls, pycls) -> str:
        """
        :param pycls: The python model class
        :return: The store entity for the supplied python model class
        """
        return cls.entities_mapping.get(pycls)

    def attribute_mappings(self, pycls):
        """
        :param pycls: The python model class
        :return: The micro object-relational definition for the specified python model class
        """
        #print(f"attrinbute_mapping {Tournament} {pycls}")
        return {Tournament:
                     [Betty.private_attribute('name'),
                      Betty.private_attribute('start_dt'),
                      Betty.private_attribute('end_dt'),
                      Betty.private_attribute('state'),
                      Betty.private_attribute('sheep_credit')],
                Phase:
                    [Betty.private_attribute('name'),
                     Betty.relates_by_id(Tournament),
                     Betty.private_attribute('state'),
                     Betty.private_attribute('scoring'),
                     ],
                Bettable:
                     [Betty.private_attribute('start_dt'),
                      Betty.relates_by_id(Phase),
                      Betty.relates_by_id(Team, 'a'),
                      Betty.relates_by_id(Team, 'b'),
                      Betty.private_attribute('state'),
                      Betty.private_attribute('outcome')],
                Bettor:
                     [Betty.private_attribute('name'),
                      Betty.private_attribute('nickname'),
                      Betty.private_attribute('email'),
                      Betty.private_attribute('pwd')],
                Participation:
                     [Betty.relates_by_id(Tournament),
                      Betty.relates_by_id(Bettor),
                      Betty.private_attribute('credit'),
                      Betty.private_attribute('score')
                     ],
                Bet:
                     [Betty.relates_by_id(Bettor),
                      Betty.relates_by_id(Bettable),
                      Betty.private_attribute('prediction'),
                      Betty.private_attribute('score')],
                Bteam:
                     [('', '')],
                Team:
                     [Betty.private_attribute('name')],
                SheepLivestock:
                     [Betty.relates_by_id(Bettor),
                      Betty.relates_by_id(SheepValue),
                      Betty.private_attribute('quantity')],
                SheepValue:
                    [Betty.relates_by_id(Tournament),
                     Betty.relates_by_id(Team),
                     Betty.private_attribute('sheep_value')],
                Ranking:
                    [Betty.relates_by_id(Tournament),
                     Betty.relates_by_id(Bettor),
                     Betty.private_attribute('ranking'),
                     Betty.private_attribute('score')]
                }.get(pycls)

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
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Tournament)} (
                 id SERIAL PRIMARY KEY,
                 name TEXT NOT NULL UNIQUE,
                 state TEXT, 
                 start_dt TIMESTAMPTZ,
                 end_dt TIMESTAMPTZ,
                 sheep_credit INT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Phase)} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Tournament)},
                 name TEXT,
                 state TEXT NOT NULL,
                 scoring TEXT
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Team)} (
                 id SERIAL PRIMARY KEY,
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
                 state TEXT NOT NULL,
                 outcome TEXT
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
              CREATE TABLE IF NOT EXISTS {cls.class_entity(SheepLivestock)} (
                   id SERIAL PRIMARY KEY,
                   {cls.references_by_id(Bettor)},
                   {cls.references_by_id(SheepValue)},
                   quantity INT
                   );
              """,
            f"""
             CREATE TABLE IF NOT EXISTS {cls.class_entity(Participation)} (
                  id SERIAL PRIMARY KEY,
                  {cls.references_by_id(Tournament)},
                  {cls.references_by_id(Bettor)},
                  credit INT,
                  score FLOAT
                  );
             """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Bet)} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Bettable)},
                 {cls.references_by_id(Bettor)},
                 prediction INT NOT NULL,
                 score FLOAT,
                 CONSTRAINT UC_Bet UNIQUE ({cls.class_entity(Bettable)}_id,{cls.class_entity(Bettor)}_id)
                 );
            """,
            f"""
            CREATE TABLE IF NOT EXISTS {cls.class_entity(Ranking)} (
                 id SERIAL PRIMARY KEY,
                 {cls.references_by_id(Tournament)},
                 {cls.references_by_id(Bettor)},
                 rank INT NOT NULL,
                 score FLOAT
                 );
            """
        ]

    @classmethod
    def setup_db(cls): # todo move to sql_store
        commands = [reduce(lambda res, c: res if (c == ' ' and (res=='' or res[-1]==' ')) else res + c,
                           cmd.replace("\n", " "),
                           '')
                    for cmd in cls.schema()]
        print('\n'.join(commands))
        store = cls.get_store()
        if store.run_commands(commands) == True:
            print('SCHEMA CREATED')

    @classmethod
    def drop_db(cls): # todo move to sql_store
        """
        Run the commands to delete the DB
        :return: None
        """
        commands = [f"DROP TABLE IF EXISTS {table} CASCADE;" for table in cls.entities_mapping.values()]

        store = cls.get_store()
        if store.run_commands(commands) == True:
            print('DB TABLES DROPPED')

    @classmethod
    def query(cls, command) -> list[dict]:
        """
        Execute the supplied query command on the DB
        :param command:
        :return:
        """
        print(command)
        return Betty().get_store().run_query(command)

    @classmethod
    def load(cls, pycls, condition: str): # todo hide SQL-specifics in sql_store
        """
        loads all records for the model entity matching the specified condition from the DB
        :param pycls: The python model class
        :param condition: the condition, expressed as a DB-specific expression, that the entities must meet to be loaded.
        :return:
        """
        table = Betty().class_entity(pycls)
        if table:
            query = f"SELECT * FROM {table}" + (f" WHERE {condition}" if condition else '') + ";"
            return Betty().get_store().run_query(query)
        else:
            return None

    @classmethod
    def save(cls, entity) -> int | None:
        """
        Inserts or update the supplied model entity in the DB.
        Insertion/update depends on whether the id attribute of the entity is None (=> insertion) or not (=> update)
        The stored entity attributes are those returned ny attribute_mappings for the entity python class. Their
        values are obtained from the entity using the same attribute mapping

        :param entity: a model entity
        :return: the id of the newly stored entity or else None
        """
        return entity.save()
        pycls = type(entity)
        attr_list = map(lambda x: x[0], Betty().attribute_mappings(pycls))
        attr_values = []
        for mapping in Betty().attribute_mappings(pycls):
            entity_attr = getattr(entity, mapping[1])
            if isinstance(entity_attr, Field):
                value = entity_attr.dbfy_value()
            if callable(entity_attr):
                # attribute available in the entity as a callable object, typically a bound method
                value = entity_attr()
            else:
                # attribute available in the entity as a regular object attribute
                value = entity_attr
            attr_values.append("NULL" if value is None else f"'{str(value)}'")
        if entity.id is None or entity.id._value is None:
            entity.id = Betty().get_store().insert(Betty().class_entity(type(entity)), attr_list, attr_values)
        else:
            Betty().get_store().update(Betty().class_entity(type(entity)), entity.id, attr_list, attr_values)
        return entity.id

if __name__ == "__main__":
    betty = Betty()

    betty.setup_db()
#    t1 = Tournament(betty, "T1")
#    t2 = Tournament(betty, "T2", datetime.now())
#    t3 = Tournament(betty, "FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21), datetime(day=19, month=7, year=2026, hour=21))
#    print(f'{t1.name} / {t2.name} / {t3.name}')
#    t3.save()
