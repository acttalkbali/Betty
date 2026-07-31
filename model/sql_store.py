import psycopg
import psycopg.rows
import os

class SqlStore:

    _instance = None
    _debug = False # Set to True to have debug information in the console

    DEFAULT_DB_CONFIG = {
        #"host": os.getenv("DB_HOST"),
        #"port": os.getenv("DB_PORT"),
        #"dbname": os.getenv("DB_NAME"),
        #"user": os.getenv("DB_USER"),
        #"password": os.getenv("DB_PWD")
        "host": 'localhost',
        "port": 5432,
        "dbname": 'betty',
        "user": 'postgres',
        "password": 'postgres'
    }
    def debug(self, s, force:bool=False):
        if force or self._debug: print(s)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            #print(f"CREATING SQL_STORE INSTANCE, CONFIG:{cls.DEFAULT_DB_CONFIG}")
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **kwargs):
        if not hasattr(self, "_initialised"):
            if kwargs:
                self._conn = psycopg.connect(**kwargs)
            else:
                print(self.DEFAULT_DB_CONFIG)
                self._conn = psycopg.connect(**self.DEFAULT_DB_CONFIG)
                print(self._conn)
            self._initialised = True

    def reset(self) -> None:
        cls._instance = None
    # ─────────────────────────────────────────────────────────────────────────────
    # HELPERS — do not modify
    # ─────────────────────────────────────────────────────────────────────────────
    def get_conn(self):
        return self._conn

    def wrap_value(value: Any) -> str:
        """
        Wraps the supplied value into the appropriate SQL command string attribute format.
        """
        return f"'{value}'"

    def wrap_condition(self, attr:str, op:str, value:Any) -> str:
        """
        Wraps the supplied value into the appropriate SQL command condition format.
        """
        return f"{attr}{op}'{value}'"

    #def setup_database(self):
    #    with self._conn.cursor() as cur:
    #        cur.execute(SETUP_SQL)
    #    self._conn.commit()
    #    print("Database setup complete.")

    def run_query(self,sql: str) -> list[tuple]:
        self.debug(f"Executing {sql}")
        if self._conn.closed:
            self._conn = psycopg.connect(**self.DEFAULT_DB_CONFIG)
        with self._conn as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute(sql)
                ret = cur.fetchall()
                self.debug(f"->{ret}")
                return ret

    def run_commands(self,commands: list[str], force_debug:bool=False) -> bool:
        success = True
        cmds = ' '.join(commands)
        commands = [cmds]
        self.debug(f"IN run_commands connection is {"CLOSED" if self._conn.closed else "OPEN"}")
        if self._conn.closed:
            self._conn = psycopg.connect(**self.DEFAULT_DB_CONFIG)
        command = ''
        try:
            for command in commands:
                with self._conn as conn:
                    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                        cur.execute(command)
                    conn.commit()
                self.debug(f"Succeeded: {command}", force_debug)
                self.debug(f"Post commit run_commands connection is {"CLOSED" if self._conn.closed else "OPEN"}")
        except Exception as e:
            print(f"Failed: {command}: {e}")
            success = False

        self.debug(f"OUT run_commands connection is {"CLOSED" if self._conn.closed else "OPEN"}")
        return success

    def insert(self, table:str, attr_list:list[str], attr_values:list[str], returning:str='id') -> int|None:
        id = None
        cmd = f"INSERT INTO {table} ({', '.join(attr_list)}) VALUES ({', '.join(attr_values)}) RETURNING {returning};"
        if self._conn.closed:
            self._conn = psycopg.connect(**self.DEFAULT_DB_CONFIG)
        try:
            with self._conn as conn:
                with conn.cursor() as cur:
                    cur.execute(cmd)
                    rows = cur.fetchone()
                    if rows:
                        id = rows[0]
                    conn.commit()
                    print(f"Success {id} <- {cmd}")
        except Exception as e:
            print(f"Failed to {cmd} : {e}")
        return id

    def update(self, table:str, id, attr_list:list[str], attr_values:list[str]) -> int|None:
        condition = f"id={id}" if isinstance(id, int) else f"id={id.dbfy_value()}"
        attr_value_pairs = ', '.join([f"{attr}={value}" for attr, value in zip(attr_list, attr_values)])
        cmd = f"UPDATE {table} SET {attr_value_pairs} WHERE {condition} RETURNING id;"
        if self._conn.closed:
            self._conn = psycopg.connect(**self.DEFAULT_DB_CONFIG)
        try:
            with self._conn as conn:
                with conn.cursor() as cur:
                    cur.execute(cmd)
                    if cur.rowcount == 1:
                        rows = cur.fetchone()
                        if rows:
                            id = rows[0]
                    conn.commit()
                    self.debug(f"Success {id} <- {cmd}")
        except Exception as e:
            print(f"Failed to {cmd} : {e}")
        return id


