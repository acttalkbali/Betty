from .bettor import Bettor
from .sheep_value import SheepValue
from .storable import Storable, Referenceable, Field


class SheepLivestock(Storable):
    _table_ = "sheep_livestock"
    """
    Dans le sens où il faut participer à un tournoi pour acheter des moutons, le livestock pourrait être lié à la
    participation mais cela allonge l'accès au Bettor
    """
    def __init__(self, store, sheep_value: SheepValue|int=None, bettor: Bettor|int=None, quantity: int=None, id:int|None=None):
        super().__init__(store)
        self._sheep_value = Referenceable(sheep_value)
        self._bettor = Referenceable(bettor)
        self._quantity = Field(quantity)

    def __str__(self):
        return f"{self._bettor}'s  {self._sheep_value.team_name if isinstance(self._sheep_value, SheepValue) else self._sheep_value} Sheep Quantity: {self._quantity}"

    def __repr__(self):
        return super().__repr__()

    #property
    def bettor_id(self) -> int|None:
        return self._bettor._id if isinstance(self._bettor, Bettor) else 0

    #property
    def sheep_value_id(self) -> int|None:
        return self._sheep_value._id if isinstance(self._sheep_value, SheepValue) else 0
