from abc import ABC, abstractmethod
from email.policy import default
from functools import reduce
from importlib.metadata import requires

def dbfy(name : str):
    return name.strip('_') if name else None

class DbFieldType(ABC):
    pass

class DbInt(DbFieldType):
    pass

class DbDate(DbFieldType):
    pass

class DbText(DbFieldType):
    pass

class DbFloat(DbFieldType):
    pass

class Field:
    def __init__(self, value, db_type=DbInt, name=None, required=True, dflt=None):
        self._value = value
        self._type = db_type
        self._name = dbfy(name)
        self._required = required
        self._dflt = dflt

class UniqueField(Field):
    def __init__(self, value, db_type=DbInt, name=None, required=True, dflt=None):
        super().__init__(value, db_type, name, required=required, dflt=dflt)

class UniqueConstraint:
    def __init__(self, field_names):
        self._field_names = field_names

class Referenceable(Field):
    def __init__(self, referred: Storable, db_type=DbInt, name=None, required=True, dflt=None):
        super().__init__(referred.id._value if isinstance(referred, Storable) else referred, db_type, name, required, dflt)
        self._referred = referred
        self.id = referred.id
        self.store_mgr = referred.store_mgr

class Storable(ABC):

    # class attributes
    _class_initialized = False
    _uniqueFields:list[str] = None
    _uniqueConstraints = None
    _fields = None

    @classmethod
    def init_class(cls, instance):
        '''
        Collect the name of the attributes which are Fields, uniqueFields or part of UniqueConstraints
        '''
        if not cls._class_initialized:
            if cls._uniqueFields is None:
                cls._uniqueFields = {k for k,v in instance.__dict__.items() if isinstance(v, UniqueField)}
            if cls._uniqueConstraints is None:
                cls._uniqueConstraints = {k for k,v in instance.__dict__.items() if isinstance(v, UniqueConstraint)}
            if cls._fields is None:
                cls._fields = {k for k,v in instance.__dict__.items() if isinstance(v, Field)}
            cls._class_initialized = True

    def __init__(self, store_mgr, id=None):
        super().__init__()
        self._id = id or None
        self.store_mgr = store_mgr
        if self._uniqueFields is None:
            self._uniqueFields = []
        self._uniqueConstraints = []

    @property
    def id(self):
        return self._id
    @id.setter
    def id(self, value:int|None):
        self._id = value

    @property
    def store(self):
        return self.store_mgr.get_store()

    def load(self, condition = ''):
        if not self._class_initialized:
            Storable.init_class(self)

        # Build the WHERE condition upon which to SELECT the record
        # If a unique key is filled in we use it
        # Else if a multi-column unique constraint exist and the corresponding instance attribute have valid values, use it

        conditions = []
        # Is a unique key filled in? If yes use it
        for uniqueFieldName, uniqueFieldValue in self._uniqueFields:
            if v:=self.__getattribute__(uniqueFieldName) is not None:
                conditions.append(self.store.wrap_condition(uniqueFieldValue.name or dbfy(uniqueFieldName), '=', v._value))

        if not conditions:
            for uniqueConstraint in self._uniqueConstraints:
                for field_name in uniqueConstraint._field_names:
                    if v:=self.__getattribute__(field_name) is not None:
                        try: # assume field instance
                            conditions.append(self.store.wrap_condition(field_name.name or dbfy(field_name), '=', v._value))
                        except:
                            conditions.append(self.store.wrap_condition(field_name or dbfy(field_name), '=', v))
                    else:
                        conditions = []
                        break
                if conditions: # a unique constraint condition could be built
                    break

        result = self.store_mgr.load(type(self), ' AND '.join(conditions))
        if len(result)==1:
            # fill-in the field attributes
            for field_name in self._fields:
                field = self.__getattribute__(field_name)
                field._value = result[0].get(field_name, result[0].get(dbfy(field_name)))

    def save(self):
        if not self._class_initialized:
            Storable.init_class(self)

        # Check if all required field have a value. If not and the field has a default, use it.
        col_list = []
        col_values = []
        for attr_name in self._fields:
            field = self.__getattribute__(attr_name)
            if field._value is None:
                if field._required:
                    if field._dflt is not None:
                        # The field has noo value but a default is available
                        field._value = field._dflt

            if field._value is not None:
                col_list.append(field._name or dbfy(attr_name))
                col_values.append(field._value)

        # If _id is None, this is considered an insertion, else an update
        if self._id is None:
            self._id = self.store_mgr.get_store().insert(self.store_mgr.class_entity(type(self)), col_list, col_values)
        else:
            self.store_mgr.get_store().update(self.store_mgr.get_store().class_entity(type(self)), self.id, col_list, col_values)
        return self._id



