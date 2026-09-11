from .storable import Storable, CharField

class ScoringRule(Storable):
    _table_ = "scoring_rule"

    name = CharField(unique=True)
    description = CharField(required=False)

    def _init_(self, name:str|None=None, description:str|None=None, id:int|None=None):
        super().__init__(id)
        self.name = name
        self.description = description
