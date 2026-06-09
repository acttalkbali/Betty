import psycopg
import psycopg.rows
import os

class SqlStore:
    _instance = None

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

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            print(f"CREATING SQL_STORE INSTANCE, CONFIG:{cls.DEFAULT_DB_CONFIG}")
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, **kwargs):
        if kwargs:
            self._conn = psycopg.connect(**kwargs)
        else:
            self._conn = psycopg.connect(**self.DEFAULT_DB_CONFIG)

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

    def setup_database(self):
        with self._conn.cursor() as cur:
            cur.execute(SETUP_SQL)
        self._conn.commit()
        print("Database setup complete.")

    def run_query(self,sql: str) -> list[tuple]:
        print(f"Executing {sql}")
        with self._conn as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute(sql)
                ret = cur.fetchall()
                print(f"->{ret}")
                return ret

    def run_commands(self,commands: list[str]) -> list[dict]:
        success = True
        cmds = ' '.join(commands)
        commands = [cmds]
        for command in commands:
            try:
                with self._conn as conn:
                    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                        cur.execute(command)
                conn.commit()
            except Exception as e:
                print(f"Failed: {command}: {e}")
                success = False
                break
        return success

    def insert_or_update(self, table:str, attr_list:list[str], attr_values:list[str], returning:str='id') -> int|None:
        # 'or_update' to be implemented
        id = None
        cmd = f"INSERT INTO {table} ({attr_list}) VALUES ({attr_values}) RETURNING {returning};"
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


    def check(label: str, result, assertion_fn, hint: str = ""):
        try:
            ok = assertion_fn(result)
        except Exception as e:
            ok = False
            hint = f"{hint} | assertion raised: {e}"
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status}  —  {label}")
        if not ok:
            print(f"         Result  : {result}")
            if hint:
                print(f"         Hint    : {hint}")

