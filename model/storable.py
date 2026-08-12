import copy
import re
from abc import ABC, abstractmethod, ABCMeta
from email.policy import default
from functools import reduce
from importlib.metadata import requires

STORABLE_ORDER_ASC = 'ASC'
STORABLE_ORDER_DESC = 'DESC'

def dbfy(name : str):
    if name:
        name = name.strip('_')
        pattern = re.compile(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
        name = pattern.sub('_', name).lower()
        return name
    else:
        return None

def dbfy_value(name : str):
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

    def dbfy_value(self):
        return f"'{self._value}'"

    def col_name(self):
        return self._name

    def dbfy_name(self, attr_name=None):
        return dbfy(self._name or attr_name)

    def __str__(self) -> str:
        return f"{self._value}"

    def __repr__(self) -> str:
        return f"{type(self)} {self._name}:{self._type}={self._value}"

class UniqueField(Field):
    def __init__(self, value, db_type=DbInt, name=None, required=True, dflt=None):
        super().__init__(value, db_type, name, required=required, dflt=dflt)

class UniqueConstraint:
    def __init__(self, field_names):
        self._field_names = field_names

class Referenceable(Field):
    def __init__(self, referred: Storable, db_type=DbInt, name=None, required=True, dflt=None):
        if isinstance(referred, Storable):
            super().__init__(referred.id, db_type, name, required, dflt)
            self._referred = referred
            self._id = referred.id
            self.store_mgr = referred.store_mgr
        else:
            super().__init__( referred, db_type, name, required, dflt)
            self._referred = None
            self._id = referred
            self.store_mgr = None

    @property
    def id(self):
        if self._referred:
            return self._referred.id
        else:
            return self._id

    @id.setter
    def id(self, value:int|None):
        self._id._value = value

    def dbfy_name(self, attr_name=None):
        return f"{super().dbfy_name(attr_name)}_id"

    def __str__(self):
        return str(self._referred if self._referred else self.id)

STORABLE_ENTITY_ATTR_NAME = '_table_'

class StorableMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        #print(f"Adding field attributes to class {name}")
        # Define class attributes
        if entity_name:=attrs.get(STORABLE_ENTITY_ATTR_NAME):
            #print(f"Adding class {name} : {entity_name} to entities mapping")
            Storable.entities[name] = entity_name
        attrs['_class_initialized'] = False
        attrs['_uniqueFields'] = None
        attrs['_uniqueConstraints'] = None
        attrs['_referenceables'] = None
        attrs['_fields'] = None
        if not attrs.get(STORABLE_ENTITY_ATTR_NAME, None):
            # if no table name is given, deduce our own from the class name
            attrs[STORABLE_ENTITY_ATTR_NAME] = dbfy(name)
        return super().__new__(mcs, name, bases, attrs)

class Storable(ABC, metaclass=StorableMeta):

    # class attributes
    #_class_initialized = False
    #_uniqueFields = None
    #_uniqueConstraints = None
    #_fields = None
    entities = dict()

    @classmethod
    def init_class(cls, instance):
        '''
        Collect the name of the attributes which are Fields, uniqueFields or part of UniqueConstraints
        '''
        instance_class = type(instance)
        if not instance_class._class_initialized:
            if instance_class._uniqueFields is None:
                instance_class._uniqueFields = []
                for k, v in instance.__dict__.items():
                    if isinstance(v, UniqueField):
                        instance_class._uniqueFields.append(k)

            if instance_class._uniqueConstraints is None:
                instance_class._uniqueConstraints = {k for k,v in instance.__dict__.items() if isinstance(v, UniqueConstraint)}
            if instance_class._fields is None:
                instance_class._fields = []
                for k, v in instance.__dict__.items():
                    if isinstance(v, Field):
                        instance_class._fields.append(k)
            if instance_class._referenceables is None:
                instance_class._referenceables = []
                for k, v in instance.__dict__.items():
                    if isinstance(v, Referenceable):
                        instance_class._referenceables.append(k)

            print(f"___ Initialized {type(instance)}\n   Unique Fields: {instance_class._uniqueFields}\n   Unique Constraints: {instance_class._uniqueConstraints}\n   Referenceables: {instance_class._referenceables}\n   Fields: {instance_class._fields}")
            instance_class._class_initialized = True

    def __init__(self, store_mgr, id=None):
        super().__init__()
        self.store_mgr = store_mgr
        self._id = UniqueField(id, required=False)

    @property
    def id(self):
        return self._id._value
    @id.setter
    def id(self, value:int|None):
        self._id._value = value

    @property
    def store(self):
        return self.store_mgr.get_store()

    def _load(self, condition = '', ordering:list[tuple[str,str]] = []):
        if not self._class_initialized:
            Storable.init_class(self)

        # Build the WHERE condition upon which to SELECT the record
        # If a unique key is filled in we use it
        # Else if a multi-column unique constraint exist and the corresponding instance attribute have valid values, use it

        conditions = [condition] if condition else []

        # Is a unique key filled in? If yes use it
        for uniqueFieldName in self._uniqueFields:
            if (field:=self.__getattribute__(uniqueFieldName)) is not None:
                if field._value is not None:
                    conditions.append(self.store.wrap_condition(field.col_name() or dbfy(uniqueFieldName), '=', field._value))

        if not conditions:
            for uniqueConstraint in self._uniqueConstraints:
                for field_name in self.__getattribute__(uniqueConstraint)._field_names:
                    if (field:=self.__getattribute__(field_name)) is not None:
                        try: # assume field instance
                            conditions.append(self.store.wrap_condition(field._name or field.dbfy_name(field_name), '=', field._value))
                        except AttributeError:
                            conditions.append(self.store.wrap_condition(field_name or dbfy(field_name), '=', field))
                    else:
                        conditions = []
                        break
                if conditions: # a unique constraint condition could be built
                    break

        if not conditions:
            # check for pre-filled foreign-keys (the '1 container' in a 1-N relationships)
            for refName in self._referenceables:
                if (field := self.__getattribute__(refName)) is not None:
                    if field._value is not None:
                        conditions.append(
                            self.store.wrap_condition(field.col_name() or dbfy(refName), '=', field._id))

        col_ordering = [f"{dbfy(field_name)} {direction}" for field_name, direction in ordering if field_name in self._fields]
        result = self.store_mgr.load(type(self), ' AND '.join(conditions), ', '.join(col_ordering))
        return result

    def fill(self, attr) :
        # fill-in the field attributes
        self._attr = attr # keep the data source
        for field_name in self._fields:
            field = self.__getattribute__(field_name)
            column_name = field.dbfy_name(field_name)
            field._value = attr.get(column_name, attr.get(field_name))
        return self

    def load(self, condition = ''):
        result = self._load(condition)
        if len(result)==1:
            # fill-in the field attributes of self
            self.fill(result[0])
        return result


    def load_all(self, condition = '', ordering:list[tuple[str,str]] = []):
        if not self._class_initialized:
            Storable.init_class(self)

        attrs = self._load(condition, ordering)
        result = []
        for attr in attrs:
            o = copy.deepcopy(self)
            result.append(o.fill(attr))
        return result, attrs

    def save(self) -> int:
        if not self._class_initialized:
            Storable.init_class(self)

        # Check if all required field have a value. If not and the field has a default, use it.
        col_list = []
        col_values = []
        print(self._fields)
        for attr_name in self._fields:
            field = self.__getattribute__(attr_name)
            if field._value is None:
                if field._required:
                    if field._dflt is not None:
                        # The field has noo value but a default is available
                        field._value = field._dflt

            if field._value is not None:
                col_list.append(field._name or field.dbfy_name(attr_name))
                col_values.append(field.dbfy_value())

        # If _id is None, this is considered an insertion, else an update
        if self._id is None or self._id._value is None:
            print(f"{type(self)} col_values={col_values} col_list={col_list}")
            self._id._value = self.store_mgr.get_store().insert(self.store_mgr.class_entity(type(self)), col_list, col_values)
        else:
            self.store_mgr.get_store().update(self.store_mgr.class_entity(type(self)), self.id, col_list, col_values)
        return self.id



