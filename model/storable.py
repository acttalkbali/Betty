import copy
import re
from abc import ABC, ABCMeta
from collections import OrderedDict
from collections.abc import Callable
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

def dbfy_name(name : str):
    return name.strip('_') if name else None

def dbfy_value(value):
    return f"'{value}'"

def joined_column(storable_cls, attribute_name = 'id'):
    return storable_cls._table_ + STORABLE_TABLE_COLUMN_SEP + attribute_name


DB_INTEGER = "INT"
DB_DATETIME = "TIMESTAMPTZ"
DB_TEXT = "TEXT"
DB_VARCHAR = "VARCHAR"
DB_FLOAT = "FLOAT"
DB_BOOLEAN = "BOOLEAN"
DB_AUTO_INC = "SERIAL"

MANY_TO_ONE_REPR = "*-|"
ONE_TO_MANY_REPR = "|-*"
ONE_TO_ONE_REPR = "|-|"
MANY_TO_MANY_REPR = "*-*"

class Field:
    def __init__(self,
                 unique:bool=False,
                 foreign=None,
                 default_value=None,
                 required:bool=True,
                 primary_key:bool=False,
                 db_type:str=DB_INTEGER,
                 check:Callable[Any,bool]=None):
        self.attribute_name = None
        self.sql_type = db_type # supplied by the subclass
        self.unique = unique
        self.foreign = foreign
        self.default_value = default_value
        self.required = required
        self.primary_key = primary_key # todo needed? Not sure this is useful as every storable has a primary key field added by the metaclass
        self.check = check
        self.owner_cls = None

    def dbfy_value(self, value):
        return f"'{value}'"

    def col_name(self):
        return self._name

    def dbfy_name(self, attr_name=None):
        return dbfy(self._name or attr_name)

    def __str__(self) -> str:
        return f"{self.owner_cls}.{self.attribute_name}:{self.sql_type}"

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

    def dbfy_value(self, value):
        return str(value).lower()


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

    def check_and_coerce(self, value):
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
            return value # Every field of the instance should already have been checked and coerced
        elif value is None: # we tolerate a None value as a placeholder
            return value
        else:
            # an actual foreign key value. Check it against the target field
            return self._target_field.check_and_coerce(value)

    def col_name(self):
        return self._name + '_id' # todo use target's pk attribute name, which may differ from 'id'

    def dbfy_name(self, attr_name=None):
        '''
        returns the default column_name as <foreignTable>_id
        '''
        return f"{super().dbfy_name(self._name or attr_name)}" # todo consider using the target's pk name, which may differ from 'id'

    def __str__(self):
        return super().__str__() + f"{MANY_TO_ONE_REPR}{self._target_field.owner_cls}"


class One2OneField(Many2OneField):
    def __init__(self, target_field:Field, db_type=DB_INTEGER, required=True, default_value=None, check=None):
        super().__init__(target_field=target_field, db_type=db_type, required=required, default_value=default_value, check=check)

    def __str__(self):
        return super().__str__() + f"{ONE_TO_ONE_REPR}{self._target_field.owner_cls}"


class Many2ManyField(Field):
    # todo To be implemented.
    def __init__(self, target_field:Field, db_type=DB_INTEGER, required=True, default_value:Any=None, check=None, relation_table_name=None):
        super().__init__(db_type=db_type, required=required, default_value=default_value, check=check)
        self._target_field = target_field

    def __str__(self):
        return super().__str__() + f"{MANY_TO_MANY_REPR}{self._target_field.owner_cls}"

    def check_and_coerce(self, value) -> Any:
        raise NotImplementedError


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
            attrs[pk_field_name] = serial
            attrs['_fields'] = OrderedDict({pk_field_name: serial})

            attrs['_class_initialized'] = False # todo no longer useful
            attrs['_unique_fields'] = OrderedDict({attr_name: attr_value for attr_name, attr_value in attrs.items() if isinstance(attr_value, Field) and attr_value.unique})
            attrs['_unique_constraints'] = OrderedDict({attr_name: attr_value for attr_name, attr_value in attrs.items() if isinstance(attr_value, UniqueConstraint)})
            attrs['_relation_fields'] = OrderedDict({attr_name: attr_value for attr_name, attr_value in attrs.items() if isinstance(attr_value, Field) and attr_value.foreign}) # todo rename to foreigns
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
        return cls

def wrap_condition(attr:str, op:str, value:Any) -> str:
    """
    Wraps the supplied value into the appropriate SQL command condition format.
    """
    return f"{attr}{op}{value}"

class Storable(ABC, metaclass=StorableMeta):

    entities = dict()

    def __init__(self, id=None):
        super().__init__()
        self.__setattr__(self._pk_field_name, id) # todo Check that this pass through the descriptor __set__

    def pk_value(self):
        return self.__getattribute__(self._pk_field_name)

    def set_pk_value(self, value):
        return self.__setattr__(self._pk_field_name, value)

    @property
    def id(self):
        return self._id._value
    @id.setter
    def id(self, value:int|None):
        self._id._value = value

    def derive_conditions_and_joins(self, consider_joins:bool, inspected:set[tuple[Storable,str]], col_prefix:str='') -> tuple[list[str], list[Join]]:
        '''
        Derive
        a) equality conditions from filled-in regular or unique fields
        b) joins with on-condition from referenceables filled-in with entities
        c) equality conditions from referenceables filled-in with an id only
        returns:
        '''

        conditions = []
        joins = []

        # Is the primary key filled in?
        pk_value = self.pk_value()
        if pk_value is None:
            # If no, check for unique fields
            # Is a unique key filled in? If yes use it
            for uniqueFieldName, field in self._unique_fields.items():
                # For each Unique fields, we add the '=' condition if the field has a value
                field_value = self.__getattribute__(uniqueFieldName)
                if field_value is not None:
                    conditions.append(wrap_condition(col_prefix + (field._name or dbfy(uniqueFieldName)), '=', field.dbfy_value(field_value)))
        else:
            if not inspected: # top-call
                # If no, use it
                conditions.append(wrap_condition(self._pk_field_name, '=', pk_value))

        # Add an '=' condition for non-unique pre-filled fields?
        # todo  Not a wonderful idea as it may result in a too coercive WHERE condition when the entity is the result of a load
        # todo  Alternative to investigate: allow fields to be assigned a Condition object. The advantage is that the
        # todo  condition cand be more generic, like eg a range/enum check
        #for fieldName, field in self._fields.items():
        #    if self._unique_fields.get(fieldName, None) is None and self.relation_fields.get(fieldName, None) is None:
        #        # For each regular fields, we add the '=' condition if the field has a value
        #        field_value = self.__getattribute__(fieldName)
        #        if field_value is not None:
        #            conditions.append(wrap_condition(col_prefix + (field._name or dbfy(fieldName)), '=', field_value))

        if not conditions:
            # For Unique Constraints, spanning several columns/fields, we add the condition if all participating fields have values
            for unique_constraint_name, field in self._unique_constraints.items():
                # for each field part of the constraint
                for field in self.__getattribute__(unique_constraint_name).fields:
                    field_value = self.__getattribute__(field._name)
                    if field_value and not isinstance(field_value, Storable):
                        conditions.append(wrap_condition(col_prefix + field.col_name(), '=', field.dbfy_value(field_value)))
                    else:
                        # Not all field of the constraint have a value
                        conditions = []
                        break
                if conditions: # a unique constraint condition could be built
                    break

        if consider_joins:
            # check for pre-filled foreign-keys (the '1 container' in a 1-N relationships)
            for foreign_field_name, foreign_field in self._relation_fields.items():
                foreign_value = self.__getattribute__(foreign_field_name)
                if foreign_value is not None:
                    joined_cls = foreign_field._target_field.owner_cls
                    src_col_name = foreign_field.col_name()
                    if isinstance(foreign_value, Storable):
                        # load related entities too
                        # if id is None, we'll join on attribute equality rather than on attribute value equality
                        joined_col_names = \
                            [f"{foreign_field._name}.{joined_field.col_name()}" #+ ('_id' if name in join.joined_cls._relation_fields else '')
                             f" AS {dbfy(foreign_field_name)}{STORABLE_TABLE_COLUMN_SEP}{joined_field.col_name()}" # + ('_id' if name in join.joined_cls._relation_fields else ''
                                 for joined_field_name, joined_field in joined_cls._fields.items()]
                        join = Join(joined_cls=joined_cls,
                                    src_field=foreign_field,
                                    target_col_name=foreign_field.col_name(),
                                    value=getattr(foreign_value, foreign_value._pk_field_name),
                                    joined_col_names=joined_col_names)
                        # prevent infinite recursion
                        if (joined_cls,src_col_name) not in inspected:
                            # Recurse on the related entity
                            inspected.add((joined_cls,src_col_name))
                            ref_conditions, ref_joins = foreign_value.derive_conditions_and_joins(consider_joins, inspected, dbfy(foreign_field_name)+".")
                            joins.append(join)
                            joins.extend(ref_joins)
                            foreign_pk_value = foreign_value.pk_value()
                            if foreign_pk_value:
                                conditions.append(wrap_condition(foreign_field.col_name(), '=', foreign_pk_value))
                            conditions.extend(ref_conditions)

                    elif foreign_value is not None:
                        # Foreign is an actual key value, the join ON condition will use it. Furthermore we don't select the joined table attributes
                        join = Join(joined_cls=joined_cls, src_field=foreign_field, value=foreign_value, joined_col_names=[], target_col_name=foreign_field.col_name())
                        joins.append(join) # JOIN table refName ON refName.id = id-value
                        conditions.append(wrap_condition(src_col_name, '=', foreign_value))

        return conditions, joins

    def _load(self, condition = '', ordering:list[tuple[str,str]] = [], consider_joins:bool = False, ):
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
        #print(f"...... Filling new {type(self)} from {attr}")
        self._attr = attr # keep the data source
        for field_name, field in self._fields.items():
            if field_name in self._relation_fields:
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
        attrs = self._load(condition, ordering, consider_joins=consider_joins)
        result = []
        for attr in attrs:
            o = copy.deepcopy(self)
            result.append(o.fill(attr))
        return result, attrs

    def save(self) -> int:
        # Check if all required field have a value. If not and the field has a default, use it.
        col_list = []
        col_values = []
        print(self._fields)
        for field_name, field in self._fields.items():
            if field.sql_type != 'SERIAL':
                field_value = self.__getattribute__(field_name)
                if field_value is None:
                    if field.required:
                        if field.default_value is not None:
                            # The field has no value but a default is available
                            self.__setattr__(field_name, field.default_value)
                            field_value = field.default_value
                if field_value is not None:
                    if isinstance(field_value, Storable):
                        col_list.append(field.col_name())
                        col_values.append(dbfy_value(field_value.pk_value()))
                    else:
                        col_list.append(field.col_name())
                        col_values.append(field.dbfy_value(field_value))
                else:
                    if field.required:
                        raise ValueError(f"Field {field_name} is required")

        # If _id is None, this is considered an insertion, else an update
        if self.pk_value() is None:
            print(f"{type(self)} col_values={col_values} col_list={col_list}")
            self.set_pk_value(SqlStore().insert(self._table_, col_list, col_values))
        else:
            SqlStore().update(self._table_, self.id, col_list, col_values)
        return self.id

    def show(self) -> str:
        field_values = {f_name: f_value for f_name, f_value in map(lambda field_name: (field_name, self.__getattribute__(field_name)),self._fields)}
        return f"############# {type(self)} : {field_values}"