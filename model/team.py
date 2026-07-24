from datetime import datetime, timedelta
from .storable import Storable

#from SqlStore import SqlStore

class Team(Storable):
    _table_ = "team"

    def __init__(self, store, name:str|None=None, id:int|None=None):
        super().__init__(store)
        self._id = id
        self._name = name or "unnamed"+str(self.id)
        #self._tournament = tournament

    def __str__(self):
        return f'{self._name}'

    def __repr__(self):
        return super().__repr__()

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, v):
        self._name = v or "unnamed" + str(id(self))

    #property
    def tournament_id(self):
        return self._tournament._id

    def load(self, condition:str = ''):
        # todo use the mini model mapping to hide the attribute names
        if self.id:
            condition += self.store.wrap_condition('id', '=', self.id)
        elif self._name:
            condition += self.store.wrap_condition('name', '=', self._name)
        results = self.store_mgr.load(type(self), condition)
        if len(results)==1:
            self._name = results[0]['name']
            self._id = results[0]['id']
            #self._tournament_id = results[0]['tournament_id']
            #self._sheep_value = results[0]['sheep_value']
            #print(f"Filled {self}")
        return results

    def load_by_id(self):
        raise NotImplementedError

    def save(self):
        self.store_mgr.save(self)
        #if self._tournament and self._sheep_value:
        #    self._sheep_value.save()

if __name__ == '__main__':
    from .betty import Betty
    betty = Betty()
    t1 = Tournament(betty, "T1")
    t2 = Tournament(betty, "T2", datetime.now())
    t3 = Tournament(betty, "FIFA World Cup 2026", datetime(day=11, month=6, year=2026, hour=21), datetime(day=19, month=7, year=2026, hour=21))
    print(f'{t1.name} / {t2.name} / {t3.name}')
    t3.save()
    #t1.name = "Tournament 1"
    #t1.start_date = dt.datetime(2026, 7,15,20)

