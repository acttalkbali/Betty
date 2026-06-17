from .bettor import Bettor
from .sheep_value import SheepValue
from .storable import Storable

class SheepLivestock(Storable):
    """
    Dans le sens où il faut participer à un tournoi pour acheter des moutons, le livestock pourrait être lié à la
    participation mais cela allonge l'accès au Bettor
    """
    def __init__(self, store, sheep_value: SheepValue | int, bettor: Bettor | int, quantity: int):
        super().__init__(store)
        self._sheep_value = sheep_value
        self._bettor = bettor
        self._sheep_value = sheep_value
        self._quantity = quantity

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

    def load(self, condition = ''):
        conditions = []
        if self.id:
            conditions.append(self.store.wrap_condition('id', '=', self.id))
        else:
            if self._bettor:
                conditions.append(self.store.wrap_condition('bettor_id', '=', self._bettor.id))
            if self._sheep_value:
                conditions.append(self.store.wrap_condition('sheep_value_id', '=', self.sheep_value_id))
        result = self.store_mgr.load(type(self), ' AND '.join(conditions))
        if len(result)==1:
            self._quantity = result[0]['quantity']
            self._id = result[0]['id']
            self._bettor = self._bettor or result[0]['bettor_id']
            self._sheep_value = self._sheep_value or result[0]['sheep_value_id']
        return result

    def save(self):
        self.store_mgr.save(self)