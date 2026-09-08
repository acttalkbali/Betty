import copy
import re
from abc import ABC, ABCMeta
from functools import reduce
from datetime import datetime
from typing import Any

from model.join import Join
from model.sql_store import SqlStore

STORABLE_ORDER_ASC = 'ASC'
STORABLE_ORDER_DESC = 'DESC'
STORABLE_ENTITY_ATTR_NAME = '_table_'
STORABLE_TABLE_COLUMN_SEP = '°'
STORABLE_PK_FIELD_ATTR = '_pk'
STORABLE_PK_DEFAULT_ATTR = 'id'

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


DB_INTEGER = "INT"
DB_DATETIME = "TIMESTAMPTZ"
DB_TEXT = "TEXT"
DB_VARCHAR = "VARCHAR"
DB_FLOAT = "FLOAT"
DB_BOOLEAN = "BOOLEAN"
DB_AUTO_INC = "SERIAL"

class Field:
    def __init__(self, unique:bool=False, foreign=None, default_value=None, required:bool=True, primary_key:bool=False, db_type:str=DB_INTEGER, check=None):
        self.attribute_name = None
        self.sql_type = db_type # supplied by the subclass
        self.unique = unique
        self.foreign = foreign
        self.default_value = default_value
        self.required = required
        self.primary_key = primary_key # todo needed?
        self.check = check
        self.owner_cls = None

    #def __init__(self, value, db_type=DbInt, name=None, required=True, dflt=None):
    #    self._value = value
    #    self._type = db_type
    #    self._name = dbfy(name) if name else None
    #    self._required = required
    #    self._dflt = dflt

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

    def __set_name__(self, owner, name):
        self._name = dbfy(name)
        self.attribute_name = name
        self.owner_cls = owner

    def __get__(self, instance, owner):
        if instance:
            return instance.__dict__[self.attribute_name]
        else:
            return self # Class-call, return the descriptor

    def __set__(self, instance, value):
        '''
        update the instance field to the supplied value.
        The instance is marked as dirty if there is a actual value change and the attribute is added
        to instance dirty_field set (So we know what columns to sql UPDATE).
        :param instance: the instance to which this field belongs
        :param value: the value to set
        :return: None
        :exception: ValueError: unsupported value
        '''
        if value is None and self.default_value:
            value = self.default_value

        #if value is None and self.required: todo check at save time
        #    raise ValueError("value is required")

        try:
            value = self.check_and_coerce(value)
        except ValueError as e:
            raise e

        if callable(self.check) and not self.check(instance, value):
            raise ValueError("check constraint violation")

        value_change = False
        try:
            current_value = instance.__dict__[self.attribute_name]
            value_change = current_value != value
        except KeyError as e:
            # No value yet. Won't mark as dirty
            instance.__dict__[self.attribute_name] = value

        if value_change:
            instance.__dict__[self.attribute_name] = value
            if self.attribute_name != instance._pk_field_name:  # Avoid using id to flag dirt
                instance._is_dirty = True
                instance._dirty_fields.add(self.attribute_name)

    def sql_def(self):
        return f"{self.attribute_name} {self.sql_type}" \
               + (' NOT NULL' if self.required else '') \
               + (' UNIQUE' if self.unique else '') \
               + (' PRIMARY KEY' if self.primary_key else '') \
               + ((' DEFAULT ' + self.default_value) if self.default_value else '')

    def check_and_coerce(self, value):
        '''
        Default method. No check
        :param value:
        :return: the supplied value or the default if the value is None
        '''
        return value or self.default_value


class BooleanField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, db_type=DB_BOOLEAN)

    def check_and_coerce(self, value) -> bool:
        '''
        Verify value is an int or a stringified int
        :param value: the value to be checked
        :return: the value coerced to a bool
        :exception ValueError: never raised
        '''
        if value is None:
            return self.default_value
        return True if value else False


class IntegerField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, db_type=DB_INTEGER)

    def check_and_coerce(self, value) -> int:
        '''
        Verify value is an int or a stringified int
        :param value: the value to be checked
        :return: the value coerced to an int
        :exception ValueError: if value may not be coerced to an int
        '''
        if value is None:
            return self.default_value
        if isinstance(value, int):
            return value
        return int(value) # may raise ValueError


class SerialField(Field):
    def __init__(self, unique:bool=True, foreign:bool=False, default_value=None, required=False, primary_key:bool=True, check=None):
        super().__init__(unique, foreign, default_value, required, primary_key, DB_AUTO_INC, check)

    def check_and_coerce(self, value) -> int|None:
        '''
        Verify value is an (possibly stringified) int or None. However, if None, don't use the default
        :param value: the value to be checked
        :return: the value coerced to an int
        :exception ValueError: if value may not be coerced to an int
        '''
        if isinstance(value, int):
            return value
        elif value is None:
            return None
        else:
            return int(value) # may raise ValueError


class CharField(Field):
    def __init__(self, *args, **kwargs ):
        max_len = kwargs.pop('max_len', None)
        db_type = f"{DB_VARCHAR}({max_len})" if max_len else DB_TEXT
        super().__init__(*args, **kwargs, db_type=db_type)
        self.max_len = max_len

    def check_and_coerce(self, value) -> str:
        '''
        Verify the stringified version of the value isn't too long
        :param value: the value to be checked
        :return: the value coerced to a string
        :exception ValueError: if the coerced value is longer than max_len
        '''
        if value is None:
            return self.default_value
        str_value = str(value)
        if self.max_len and len(str_value) > self.max_len:
            raise ValueError(f'Too long value \\{value}\\ for {self.attribute_name}. Max length is {self.max_len}')
        return str_value


class FloatField(Field):
    def __init__(self, unique: bool = False, foreign: bool = False, default_value=None, required: bool = True,
                 primary_key: bool = False, check = None):
        super().__init__(unique, foreign, default_value, required, primary_key, DB_FLOAT, check)

    def check_and_coerce(self, value) -> str:
        '''
        Verify the stringified version of the value isn't too long
        :param value: the value to be checked
        :return: the value coerced to a string
        :exception ValueError: if the coerced value is longer than max_len
        '''
        if value is None:
            return self.default_value
        return float(value)


class DateField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, db_type=DB_DATETIME)

    def check_and_coerce(self, value) -> str:
        '''
        Verify the stringified version of the value isn't too long
        :param value: the value to be checked
        :return: the value coerced to a string
        :exception ValueError: if the coerced value is longer than max_len
        '''
        if value is None:
            return self.default_value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        elif isinstance(value, datetime):
            return value
        else:
            raise ValueError(f'Not a valid datetime')


class Many2OneField(Field):
    def __init__(self, target_field:Field, db_type=DB_INTEGER, name=None, required=True, default_value=None, check=None):
        super().__init__(unique=False, db_type=db_type, required=required, default_value=default_value, foreign=True, check=check) # todo name=name ?
        self._target_field = target_field

    def check_and_coerce(self, value) -> Any:
        if isinstance(value, self._target_field.owner_cls):
            #self._referred = value
            #self._id = value.__getattribute__(self._target_field.attribute_name)
            foreign_key_value = value.__getattribute__(value._pk_field_name)
            return self._target_field.check_and_coerce(foreign_key_value)
        elif value is None: # we tolerate a None value as placeholder
            return value
        else:
            return self._target_field.check_and_coerce(value) # The actual foreign key value

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


class One2OneField(Field):
    def __init__(self, storable_cls, target_field:Field, db_type=DB_INTEGER, required=True, default_value=None, check=None):
        super().__init__(db_type, required=required, default_value=default_value, unique=True, foreign=True, check=check)
        self._storable_cls = storable_cls
        self._target_field = target_field

    def check_and_coerce(self, value) -> str:
        '''
        Verify the stringified version of the value isn't too long
        :param value: the value to be checked
        :return: the value coerced to a string
        :exception ValueError: if the coerced value is longer than max_len
        '''
        if isinstance(value, Storable):
            self._referred = value
            self._id = value.getattr(self.target_field.attribute_name)
            #self.store_mgr = referred.store_mgr
        else:
            self.foreign_value = self.target_field.check_and_coerce(value)
            self._referred = None
            #self.store_mgr = None


class UniqueConstraint:
    def __init__(self, fields:[Field], name:str=""):
        self.fields = fields
        self.name = name # or "uc_" + '_'.join(map(lambda field: field.owner_cls.__name__, fields))

    def sql_def(self):
        return f"CONSTRAINT {self.name} UNIQUE (" \
               + ','.join(map(lambda field: field._name, self.fields)) \
               + ')'


class StorableMeta(ABCMeta):
    def __new__(mcs, name, bases, attrs):
        #print(f"Adding field attributes to class {name}")
        # Define class attributes
        entity_name = attrs.get(STORABLE_ENTITY_ATTR_NAME)
        if entity_name:
            #print(f"Adding class {name} : {entity_name} to entities mapping")
            Storable.entities[name] = entity_name

            # Add class attributes:
            # Add two class attributes:
            #   id as a SerialField
            #   _pk_field_name to hold the mapping from attribute name to field, populated through the Field __set_name__ method
            pk_field_name = attrs.get(STORABLE_PK_FIELD_ATTR) or STORABLE_PK_DEFAULT_ATTR
            attrs['_pk_field_name'] = pk_field_name
            serial = SerialField()
            attrs['_fields'] = {pk_field_name: serial}
            attrs[pk_field_name] = serial

            attrs['_class_initialized'] = False # todo no longer useful
            attrs['_uniqueFields'] = {attr_name: attr_value for attr_name, attr_value in attrs.items() if isinstance(attr_value, Field) and attr_value.unique}
            attrs['_uniqueConstraints'] = {attr_name: attr_value for attr_name, attr_value in attrs.items() if isinstance(attr_value, UniqueConstraint)}
            attrs['_referenceables'] = {attr_name: attr_value for attr_name, attr_value in attrs.items() if isinstance(attr_value, Field) and attr_value.foreign} # todo rename to foreigns
            attrs['_fields'].update({attr_name: attr_value for attr_name, attr_value in attrs.items() if isinstance(attr_value, Field)})

            attrs['_dirty_fields'] = set()

            if attrs.get(STORABLE_ENTITY_ATTR_NAME, None) is None:
                # if no table name is given, deduce our own from the class name
                attrs[STORABLE_ENTITY_ATTR_NAME] = dbfy(name)


        # create the class
        cls = super().__new__(mcs, name, bases, attrs)

        # Add a reference to the class in each descriptor
        for  attr in attrs:
            if isinstance(attr, Field):
                attr.owner_cls = cls

        #if name != "Storable":
        #    # Decorate the __init__ call of the Storable subclass with a call to cls.init_class as last instruction
        #    basic_init = cls.__init__
        #    def decorated_init(self, *args, **kwargs):
        #        basic_init(self, *args, **kwargs)
        #        self.__class__.init_class(self)
        #    cls.__init__ = decorated_init

        return cls

def wrap_condition(attr:str, op:str, value:Any) -> str:
    """
    Wraps the supplied value into the appropriate SQL command condition format.
    """
    return f"{attr}{op}'{value}'"

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
            #if instance_class._uniqueFields is None:
            #    instance_class._uniqueFields = []
            #    for k, v in instance.__dict__.items():
            #        if isinstance(v, UniqueField):
            #            instance_class._uniqueFields.append(k)

            if instance_class._uniqueConstraints is None:
                instance_class._uniqueConstraints = {k for k,v in instance.__dict__.items() if isinstance(v, UniqueConstraint)}

            #if instance_class._fields is None:
            #    instance_class._fields = []
            #    for k, v in instance.__dict__.items():
            #        if isinstance(v, Field):
            #           instance_class._fields.append(k)
            #if instance_class._referenceables is None:
            #    instance_class._referenceables = []
            #    for k, v in instance.__dict__.items():
            #        if isinstance(v, Referenceable):
            #            v._name = k
            #            instance_class._referenceables.append(k)

            #print(f"___ Initialized {type(instance)}\n   Unique Fields: {instance_class._uniqueFields}\n   Unique Constraints: {instance_class._uniqueConstraints}\n   Referenceables: {instance_class._referenceables}\n   Fields: {instance_class._fields}")
            instance_class._class_initialized = True

    def __init__(self, id=None):
        super().__init__()
        #self.store_mgr = store_mgr or Betty()
        self.__setattr__(self._pk_field_name, id) # todo Check that this pass through the descriptor __set__

    @property
    def id(self):
        return self._id._value
    @id.setter
    def id(self, value:int|None):
        self._id._value = value

    #@property
    #def store(self):
    #    return self.store_mgr.get_store()

    def derive_conditions_and_joins(self, consider_joins:bool, inspected:set[Storable], col_prefix:str='') -> tuple[list[str], list[Join]]:
        '''
        Derive
        a) equality conditions from filled-in regular or unique fields
        b) joins with on-condition from referenceables filled-in with entities
        c) equality conditions from referenceables filled-in with an id only
        returns:
        '''
        if self in inspected:
            return [],[]

        conditions = []
        joins = []

        # Is a unique key filled in? If yes use it
        for uniqueFieldName, field in self._uniqueFields.items():
            # For each Unique fields, we add the '=' condition if the field has a value
            field_value = self.__getattribute__(uniqueFieldName)
            if field_value is not None:
                conditions.append(wrap_condition(col_prefix + (field._name or dbfy(uniqueFieldName)), '=', field_value))

        # Add an '=' condition for non-unique pre-filled fields?
        #for fieldName, field in self._fields.items():
        #    if self._uniqueFields.get(fieldName, None) is None and self._referenceables.get(fieldName, None) is None:
        #        # For each regular fields, we add the '=' condition if the field has a value
        #        field_value = self.__getattribute__(fieldName)
        #        if field_value is not None:
        #            conditions.append(wrap_condition(col_prefix + (field._name or dbfy(fieldName)), '=', field_value))

        if not conditions:
            # For Unique Constraints, spanning several columns/fields, we add the condition if all participating fields have values
            for uniqueConstraintName, field in self._uniqueConstraints.items():
                # for each field part of the constraint
                for field in self.__getattribute__(uniqueConstraintName).fields:
                    field_value = self.__getattribute__(field._name)
                    if field_value:
                        conditions.append(wrap_condition(col_prefix + field._name, '=', field_value))
                    else:
                        # Not all field of the constraint have a value
                        conditions = []
                        break
                if conditions: # a unique constraint condition could be built
                    break

        join_columns = []
        if consider_joins:
            # check for pre-filled foreign-keys (the '1 container' in a 1-N relationships)
            for foreign_field_name, field in self._referenceables.items():
                referenceable = self.__getattribute__(foreign_field_name)
                if referenceable is not None:
                    joined_cls = referenceable._storable_cls
                    src_col_name = dbfy(foreign_field_name)
                    join = None
                    if referenceable._referred:
                        # load related entities too
                        # if id is None, we'll join on attribute equality rather than on attribute value equality
                        join = Join(joined_cls, src_col_name, referenceable._referred.id, [])
                        # Recurse on the referred entity
                        ref_conditions, ref_joins = referenceable._referred.derive_conditions_and_joins(consider_joins, inspected, dbfy(foreign_field_name)+".")
                        joins.append(join)
                        joins.extend(ref_joins)
                        conditions.extend(ref_conditions)

                    elif referenceable._id:
                        join = Join(joined_cls=joined_cls, src_col_name=src_col_name, value=referenceable._id, joined_col_names=None)
                        joins.append(join) # JOIN table refName ON refName.id = id-value

                    if join:
                        # add the joined table attributes to the query
                        if join.joined_cls._fields: # !! May be false if no instance of the joined_class has been created yet
                            join.joined_col_names = [f"{src_col_name}.{dbfy(name) + ('_id' if name in join.joined_cls._referenceables else '')}"
                                 f" AS {dbfy(foreign_field_name)}{STORABLE_TABLE_COLUMN_SEP}{dbfy(name) + ('_id' if name in join.joined_cls._referenceables else '')}"
                                 for name in join.joined_cls._fields]
        return conditions, joins

    def _load(self, condition = '', ordering:list[tuple[str,str]] = [], consider_joins:bool = False, ):
        if not self._class_initialized: # todo : Still necessary?
            Storable.init_class(self)

        # Build the WHERE condition upon which to SELECT the record
        # If a unique key is filled in we use it
        # Else if a multi-column unique constraint exist and the corresponding instance attribute have valid values, use it
        sql_store = SqlStore()
        conditions = [condition] if condition else []
        inspected = set()
        more_conditions, joins = self.derive_conditions_and_joins(True, inspected)
        conditions.extend(more_conditions)

        col_ordering = [f"{dbfy(field_name)} {direction}" for field_name, direction in ordering if field_name in self._fields]

        result = sql_store.load(type(self), joins, ' AND '.join(conditions), ', '.join(col_ordering))
        return result

    def fill(self, attr) -> "Storable":
        # fill-in the field attributes
        print(f"...... Filling new {type(self)} from {attr}")
        self._attr = attr # keep the data source
        for field_name, field in self._fields.items():
            if field_name in self._referenceables:
                # if attr contains referenceable_XXX data, let's create an object for it
                #referenceable = self.__getattribute__(field_name)
                entityClass = field._target_field.owner_cls
                prefix = entityClass._table_ + STORABLE_TABLE_COLUMN_SEP
                # Fill the object with attributes not related to the current entity
                if reduce(lambda a,x: a or x.startswith(prefix), attr.keys(), False):
                    # There is some entity data todo what about only the id available?
                    filtered_attr = {k.split(prefix)[-1] : v for k,v in attr.items() if STORABLE_TABLE_COLUMN_SEP in k}
                    referenced_entity = entityClass()
                    target = referenced_entity.fill(filtered_attr)
                    self.__setattr__(field_name, target)
                else:
                    # simply set the foreign key value if available
                    if foreign_key_value := attr.get(field_name + '_id'):
                        self.__setattr__(field_name, foreign_key_value)
            else:
                column_name = field.dbfy_name(field_name)
                value = attr.get(column_name, attr.get(field_name))
                self.__setattr__(field_name, value)
        #print(self.show())
        return self

    def load(self, condition = ''):
        result = self._load(condition)
        if len(result)==1:
            # fill-in the field attributes of self
            self.fill(result[0])
        return result


    def load_all(self, condition = '', ordering:list[tuple[str,str]] = [], consider_joins:bool = True):
        #if not self._class_initialized:
        #    Storable.init_class(self)

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
                    if field._default_value is not None:
                        # The field has noo value but a default is available
                        field._value = field._default_value

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