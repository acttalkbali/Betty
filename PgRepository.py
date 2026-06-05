import psycopg
from TournamentRepository import Repository
# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — do not modify
# ─────────────────────────────────────────────────────────────────────────────
def get_conn():
    return psycopg.connect(**DB_CONFIG)

def run_query(sql: str) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(sql)
            return cur.fetchall()

def run_write(sql: str) -> list[dict] | None:
    with get_conn() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute(sql)
            conn.commit()
            try:
                return cur.fetchall()
            except Exception:
                return None


class PgRepository(Repository):
    def __init__(self, db_name, db_user, db_pass, host = 'localhost', port='5432'):
        super().__init__()
        self._config  = {
            "host": host,
            "port": port,
            "dbname": db_name,
            "user": db_user,
            "password": db_pass,
        }

    def connect(self):
        return psycopg.connect(**self._config)

    def run_query(sql: str) -> list[dict]:
        with get_conn() as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                cur.execute(sql)
                return cur.fetchall()

    def load_user_view(self):
        pass

    def load_admin_view(self):
        pass

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

