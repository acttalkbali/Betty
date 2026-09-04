from .bettor import Bettor
from .sheep_value import SheepValue
from .storable import Storable, Many2OneField, Field, IntegerField


class SheepLivestock(Storable):

    # Model -----------------------------------------------------------------
    _table_ = "sheep_livestock"
    """
    Dans le sens où il faut participer à un tournoi pour acheter des moutons, le livestock pourrait être lié à la
    participation mais cela allonge l'accès au Bettor
    """

    sheep_value = Many2OneField(SheepValue.id)
    bettor = Many2OneField(Bettor.id)
    quantity = IntegerField()

    def __init__(self, sheep_value: SheepValue|int=None, bettor: Bettor|int=None, quantity: int=None, id:int|None=None):
        super().__init__()
        self.sheep_value = sheep_value
        self.bettor = bettor
        self.quantity = quantity

    def __str__(self):
        return f"{self.bettor}'s  {self.sheep_value.team_name if isinstance(self.sheep_value, SheepValue) else self.sheep_value} Sheep Quantity: {self.quantity}"

    def __repr__(self):
        return super().__repr__()

    #property
    def bettor_id(self) -> int|None:
        return self.bettor._id if isinstance(self.bettor, Bettor) else 0

    #property
    def sheep_value_id(self) -> int|None:
        return self.sheep_value._id if isinstance(self.sheep_value, SheepValue) else 0
