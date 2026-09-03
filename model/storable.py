import copy
import re
from abc import ABC, ABCMeta
from dataclasses import dataclass
from functools import reduce
from typing import Any

from model.sql_store import SqlStore

STORABLE_ORDER_ASC = 'ASC'
STORABLE_ORDER_DESC = 'DESC'
STORABLE_ENTITY_ATTR_NAME = '_table_'
STORABLE_TABLE_COLUMN_SEP = '°'

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

def joined_column(storable_cls, attribute_name = 'id'):
    return storable_cls._table_ + STORABLE_TABLE_COLUMN_SEP + attribute_name

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
        self._name = dbfy(name) if name else None
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
        return f"{self._type}={self._value}" # f"{type(self)} {self._name}:{self._type}={self._value}"

class UniqueField(Field):
    def __init__(self, value, db_type=DbInt, name=None, required=True, dflt=None):
        super().__init__(value, db_type, name, required=required, dflt=dflt)

class UniqueConstraint:
    def __init__(self, field_names):
        self._field_names = field_names

class Referenceable(Field):
    def __init__(self, storable_cls, referred: Storable|int, db_type=DbInt, name=None, required=True, dflt=None):
        self._storable_cls = storable_cls
        if isinstance(referred, Storable):
            super().__init__(referred.id, db_type, name, required, dflt)
            self._referred = referred
            self._id = referred.id
            #self.store_mgr = referred.store_mgr
        else:
            super().__init__( referred, db_type, name, required, dflt)
            self._referred = None
            self._id = referred
            #self.store_mgr = None

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
        '''
        returns the default column_name as <foreignTable>_id
        '''
        return f"{super().dbfy_name(self._name or attr_name)}_id"

    def __str__(self):
        return str(self._referred if self._referred else self.id)

    def __repr__(self) -> str:
        return f"{self._referred}={self.id}" # f"{type(self)} {self._name}:{self._type}={self._value}"

class StorableMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        #print(f"Adding field attributes to class {name}")
        # Define class attributes
        entity_name = attrs.get(STORABLE_ENTITY_ATTR_NAME)
        if entity_name:
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

        # create the class
        cls = super().__new__(mcs, name, bases, attrs)

        if name != "Storable":
            # Decorate the __init__ call of the Storable subclass with a call to cls.init_class as last instruction
            basic_init = cls.__init__
            def decorated_init(self, *args, **kwargs):
                basic_init(self, *args, **kwargs)
                self.__class__.init_class(self)
            cls.__init__ = decorated_init

        return cls


@dataclass
class Join:
    """Class for keeping track of join"""
    joined_cls: Storable
    src_col_name: str
    value: Any

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
                        v._name = k
                        instance_class._referenceables.append(k)

            #print(f"___ Initialized {type(instance)}\n   Unique Fields: {instance_class._uniqueFields}\n   Unique Constraints: {instance_class._uniqueConstraints}\n   Referenceables: {instance_class._referenceables}\n   Fields: {instance_class._fields}")
            instance_class._class_initialized = True

    def __init__(self, store_mgr=None, id=None):
        super().__init__()
        #self.store_mgr = store_mgr or Betty()
        self._id = UniqueField(id, required=False)

    @property
    def id(self):
        return self._id._value
    @id.setter
    def id(self, value:int|None):
        self._id._value = value

    #@property
    #def store(self):
    #    return self.store_mgr.get_store()

    def derive_conditions_and_joins(self, consider_joins:bool=True) -> tuple[[], []]:
        '''
        Derive
        a) equality conditions from filled-in regular or unique fields
        b) joins with on-condition from referenceables filled-in with entities
        c) equality conditions from referenceables filled-in with an id only
        returns:
        '''
        sql_store = SqlStore()

        conditions = []
        joins = []

        # Is a unique key filled in? If yes use it
        for uniqueFieldName in self._uniqueFields:
            # For each Unique fields, we add the '=' condition if the field has a value
            if (field:=self.__getattribute__(uniqueFieldName)) is not None:
                if field._value is not None:
                    conditions.append(sql_store.wrap_condition(field.col_name() or dbfy(uniqueFieldName), '=', field._value))

        # Add an '=' condition for non-unique pre-filled fields?
        for fieldName in self._fields:
            if fieldName not in self._uniqueFields and fieldName not in self._referenceables:
                # For each regular fields, we add the '=' condition if the field has a value
                if (field:=self.__getattribute__(fieldName)) is not None:
                    if field._value is not None:
                        conditions.append(sql_store.wrap_condition(field.col_name() or dbfy(fieldName), '=', field._value))

        if not conditions:
            # For Unique Constraints, spanning several columns/fields, we add the condition if all participating fields have values
            for uniqueConstraint in self._uniqueConstraints:
                for field_name in self.__getattribute__(uniqueConstraint)._field_names:
                    field = self.__getattribute__(field_name)
                    if field is not None:
                        try: # assume field instance
                            if field._value:
                                conditions.append(sql_store.wrap_condition(field.dbfy_name(field_name) or field._name, '=', field._value))
                        except AttributeError:
                            if field:
                                conditions.append(sql_store.wrap_condition(field_name or dbfy(field_name), '=', field))
                    else:
                        conditions = []
                        break
                if conditions: # a unique constraint condition could be built
                    break

        join_columns = []
        if consider_joins:
            # check for pre-filled foreign-keys (the '1 container' in a 1-N relationships)
            for refName in self._referenceables:
                referenceable = self.__getattribute__(refName)
                if referenceable is not None:
                    joined_cls = referenceable._storable_cls
                    src_col_name = dbfy(refName)
                    join = None
                    if self._referred:
                        # load related entities too
                        # if id is None, we'll join on attribute equality rather than on attribute value equality
                        join = Join(joined_cls, src_col_name, self._referred.id)
                        # Recurse on the referred entity
                        ref_conditions, ref_joins = self._referred.derive_conditions_and_joins(consider_joins=consider_joins)
                        joins.append(join)
                        joins.extend(ref_joins)
                        conditions.extend(ref_conditions)

                    elif referenceable._id:
                        join = Join(joined_cls, src_col_name, referenceable._id)
                        joins.append(join) # JOIN table refName ON refName.id = id-value

                    if join:
                        # add the joined table attributes to the query
                        if joined_cls._fields: # !! May be false if no instance of the joined_class has been created yet
                            join_columns.extend(
                                [f"{src_col_name}.{dbfy(name) + ('_id' if name in joined_cls._referenceables else '')}"
                                 f" AS {dbfy(refName)}{STORABLE_TABLE_COLUMN_SEP}{dbfy(name) + ('_id' if name in joined_cls._referenceables else '')}"
                                 for name in joined_cls._fields])

    def _load(self, condition = '',ordering:list[tuple[str,str]] = [], consider_joins:bool = False, ):
        if not self._class_initialized:
            Storable.init_class(self)

        # Build the WHERE condition upon which to SELECT the record
        # If a unique key is filled in we use it
        # Else if a multi-column unique constraint exist and the corresponding instance attribute have valid values, use it
        sql_store = SqlStore()
        conditions = [condition] if condition else []

        conditions, joins = self.derive_conditions_and_joins()

        col_ordering = [f"{dbfy(field_name)} {direction}" for field_name, direction in ordering if field_name in self._fields]

        result = sql_store.load(type(self), joins, join_columns, ' AND '.join(conditions), ', '.join(col_ordering))
        return result

    def fill(self, attr) -> "Storable":
        # fill-in the field attributes
        print(f"...... Filling new {type(self)} from {attr}")
        self._attr = attr # keep the data source
        for field_name in self._fields:
            if field_name in self._referenceables:
                # if attr contains referenceable_XXX data, let's create an object for it
                referenceable = self.__getattribute__(field_name)
                entityClass = referenceable._storable_cls
                prefix = entityClass._table_ + STORABLE_TABLE_COLUMN_SEP
                # Fill the object with attributes not related to the current entity
                if reduce(lambda a,x: a or x.startswith(prefix), attr.keys(), False):
                    # There is some entity data todo what about only the id available?
                    filtered_attr = {k.split(prefix)[-1] : v for k,v in attr.items() if STORABLE_TABLE_COLUMN_SEP in k}
                    referenced_entity = entityClass()
                    referenceable._referred = referenced_entity.fill(filtered_attr)
                    #self.__setattr__(field_name, referenceable)
            else:
                field = self.__getattribute__(field_name)
                column_name = field.dbfy_name(field_name)
                field._value = attr.get(column_name, attr.get(field_name))
        #print(self.show())
        return self

    def load(self, condition = ''):
        result = self._load(condition)
        if len(result)==1:
            # fill-in the field attributes of self
            self.fill(result[0])
        return result


    def load_all(self, condition = '', ordering:list[tuple[str,str]] = [], consider_joins:bool = True):
        if not self._class_initialized:
            Storable.init_class(self)

        attrs = self._load(condition, ordering, consider_joins=consider_joins)
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
                col_list.append(field.dbfy_name(attr_name) or field._name)
                col_values.append(field.dbfy_value())

        # If _id is None, this is considered an insertion, else an update
        if self._id is None or self._id._value is None:
            print(f"{type(self)} col_values={col_values} col_list={col_list}")
            self._id._value = SqlStore().insert(self._table_, col_list, col_values)
        else:
            SqlStore().update(self._table_, self.id, col_list, col_values)
        return self.id

    def show(self) -> str:
        field_values = {f_name: f_value for f_name, f_value in map(lambda field_name: (field_name, self.__getattribute__(field_name)),self._fields)}
        return f"############# {type(self)} : {field_values}"