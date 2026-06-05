import Tournament
import Phase
import Bettable
import Bettor
import Bet
import Bteam
import Team
import SheepLivestock
import SheepValue

def private_attribute(attr:str) -> (str,str):
    return attr, '_'+attr

def references_by_id(entity, prefix='', nullable=False) -> str:
    return f"{prefix}_{Betty.model[entity]['entity']}_id {'NOT NULL ' if not nullable else ''} REFERENCES {Betty.model[entity]['entity']}(id)"

def relates_by_id(entity, prefix='') -> str:
    return f"{prefix}_{Betty.model[entity]['entity']}_id"


class Betty:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            _instance = super().__new__()
        return cls._instance

    def get_store(self):
        return SqlStore()


    model = {Tournament:
                    {'entity': 'tournament',
                     'attributes': [private_attribute('name'),
                                    private_attribute('start'),
                                    private_attribute('state')]},
                Phase:
                    {'entity': 'phase',
                     'attributes' : [private_attribute('name'),
                                     relates_by_id(Tournament)]},
                Bettable:
                    {'entity': 'bettable',
                     'attributes' : [private_attribute('name'),
                                     private_attribute('team_a_id'),
                                     relates_by_id]},
                Bettor:
                    {'entity': 'bettor',
                     'attributes': [private_attribute('name'),
                                    private_attribute('nickname'),
                                    private_attribute('pwd'),
                                    private_attribute('email')]},
                Bet:
                    {'entity': 'bet',
                     'attributes': [private_attribute('prediction'),
                                    private_attribute('')]},
                Bteam:
                    {'entity': 'bteam',
                     'attributes': [('', '')]},
                Team:
                    {'entity': 'team',
                     'attributes': [('', '')]},
                Sheep_Livestock:
                    {'entity': 'sheep_livestock',
                     'attributes': [('', '')]},
                Sheep_Value:
                    {'entity': 'sheep_value',
                     'attributes': [('', '')]},
                }

    schema = f"""
        CREATE TABLE IF NOT EXISTS {model[Tournament].entity} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             name TEXT,
             state ENUM('OPEN', 'RUNNING', 'CLOSED')  NOT NULL
             );

        CREATE TABLE IF NOT EXISTS {model[Phase].entity} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             {references_by_id(Tournament)},
             name TEXT,
             state ENUM('OPEN', 'RUNNING', 'CLOSED') NOT NULL
             );
    
        CREATE TABLE IF NOT EXISTS {model[Bettable].entity} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             {references_by_id(Phase)},
             {references_by_id(Team, 'a')},
             {references_by_id(Team, 'b')},
             start DATETIME,
             state ENUM('OPEN', 'RUNNING', 'CLOSED')  NOT NULL
             );
    
        CREATE TABLE IF NOT EXISTS {model[Bettor].entity} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             name TEXT NOT NULL,
             nickname TEXT UNIQUE,
             email TEXT UNIQUE,
             pwd TEXT NOT NULL,
             {references_by_id(Bteam, nullable=True)},
             );
    
        CREATE TABLE IF NOT EXISTS {model[Bet].entity} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             {references_by_id(Bettable)},
             {references_by_id(Bettor)},
             prediction INT NOT NULL
             );
    
    
        CREATE TABLE IF NOT EXISTS {model[Bteam].entity} (
             id INT AUTO_INCREMENT PRIMARY_KEY,
             name TEXT UNIQUE NOT NULL
             );
        """

    def define_entity(self, cls):
        define_entity

    def setup_db(self):
        define_entity(self.get_model(Tournament))

print(Betty.schema)
