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
from datetime import datetime, timedelta

class Betty:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print("CREATING BETTY INSTANCE")
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_store(self):
        return None #SqlStore()

    @classmethod
    def private_attribute(cls, attr: str) -> (str, str):
        return attr, '_' + attr

    @classmethod
    def class_entity(cls, pycls):
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
        return f"{prefix}{entity}_id {'NOT NULL' if not nullable else ''} REFERENCES {entity}(id)"

    @classmethod
    def relates_by_id(cls, pyclass, prefix='') -> str:
        print(f"relates_by_id {pyclass}")
        entity = cls.class_entity(pyclass)
        if prefix:
            prefix += '_'
        attr = f"{prefix}{entity}_id"
        return attr, f"_{attr}"


    def attribute_mapping(self, pycls):
        print(f"attrinbute_mapping {Tournament} {pycls}")
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
                      Betty.relates_by_id(Team, "a"),
                      Betty.relates_by_id(Team, "b")],
                Bettor:
                     [Betty.private_attribute('name'),
                      Betty.private_attribute('nickname'),
                      Betty.private_attribute('pwd'),
                      Betty.private_attribute('email')],
                Bet:
                     [Betty.private_attribute('prediction'),
                      Betty.private_attribute('')],
                Bteam:
                     [('', '')],
                Bteam:
                     [('', '')],
                SheepLivestock:
                     [('', '')],
                SheepValue: [('', '')]
                }.get(pycls)

    @classmethod
    def schema(cls):
        return f"""
        CREATE TABLE IF NOT EXISTS {cls.class_entity(Tournament)} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             name TEXT,
             state ENUM('OPEN', 'RUNNING', 'CLOSED')  NOT NULL,
             start_dt DATETIME,
             end_dt DATETIME
             );

        CREATE TABLE IF NOT EXISTS {cls.class_entity(Phase)} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             {cls.references_by_id(Tournament)},
             name TEXT,
             state ENUM('OPEN', 'RUNNING', 'CLOSED') NOT NULL
             );

        CREATE TABLE IF NOT EXISTS {cls.class_entity(Bettable)} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             {cls.references_by_id(Phase)},
             {cls.references_by_id(Team, 'a')},
             {cls.references_by_id(Team, 'b')},
             start_dt DATETIME,
             state ENUM('OPEN', 'RUNNING', 'CLOSED') NOT NULL
             );

        CREATE TABLE IF NOT EXISTS {cls.class_entity(Bettor)} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             name TEXT NOT NULL,
             nickname TEXT UNIQUE,
             email TEXT UNIQUE,
             pwd TEXT NOT NULL,
             {cls.references_by_id(Bteam, nullable=True)},
             );

        CREATE TABLE IF NOT EXISTS {cls.class_entity(Bet)} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             {cls.references_by_id(Bettable)},
             {cls.references_by_id(Bettor)},
             prediction INT NOT NULL
             );

        CREATE TABLE IF NOT EXISTS {cls.class_entity(Bteam)} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             name TEXT UNIQUE NOT NULL
             );
        """

    @classmethod
    def run_query(cls, str):
        print(str)

    @classmethod
    def setup_db(cls):
        print(cls.schema())

    @classmethod
    def save(cls, entity):
        pycls = type(entity)
        attr_list = ','.join(map(lambda x: x[0], Betty().attribute_mapping(pycls)))
        attr_values = ','.join(map(
            lambda x: "'" + str(getattr(entity, x[1])) + "'",
            Betty().attribute_mapping(pycls)))
        Betty().run_query(f"INSERT OR UPDATE {Betty.class_entity(pycls)} ({attr_list}) VALUES ({attr_values});")

if __name__ == "__main__":
    betty = Betty()

    betty.setup_db()
    t1 = Tournament(betty, "T1")
    t2 = Tournament(betty, "T2", datetime.now())
    t3 = Tournament(betty, "FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21), datetime(day=19, month=7, year=2026, hour=21))
    print(f'{t1.name} / {t2.name} / {t3.name}')
    #t3.save()
