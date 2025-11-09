from prometheus_client import start_http_server, Gauge
import psycopg2
import time

# Настройки подключения
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "abzal"
DB_NAME = "postgres"

# Метрика: пользователи + привилегии
user_privileges_gauge = Gauge(
    "postgres_user_privileges",
    "User privileges in PostgreSQL (1=yes, 0=no)",
    ["role_name", "privilege"]
)

# QPS
qps_gauge = Gauge("postgres_qps", "Number of transactions per second in PostgreSQL")

# Uptime
uptime_gauge = Gauge("postgres_uptime_seconds", "PostgreSQL uptime in seconds")
uptime_hours_gauge = Gauge("postgres_uptime_hours", "PostgreSQL uptime in hours")

# Для расчета QPS
previous_tx_count = None
previous_time = None

def collect_metrics():
    global previous_tx_count, previous_time

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    cur = conn.cursor()

    # Пользователи и их привилегии
    cur.execute("SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolreplication FROM pg_roles;")
    roles = cur.fetchall()

    user_privileges_gauge.clear()  # очищаем старые значения
    for role in roles:
        role_name = role[0]
        privileges = {
            "superuser": role[1],
            "createrole": role[2],
            "createdb": role[3],
            "replication": role[4]
        }
        for priv, value in privileges.items():
            user_privileges_gauge.labels(role_name=role_name, privilege=priv).set(1 if value else 0)

    # QPS
    cur.execute("SELECT sum(xact_commit + xact_rollback) FROM pg_stat_database;")
    total_tx = float(cur.fetchone()[0])
    current_time = time.time()
    if previous_tx_count is not None and previous_time is not None:
        qps = (total_tx - previous_tx_count) / (current_time - previous_time)
        qps_gauge.set(qps)
    previous_tx_count = total_tx
    previous_time = current_time

    # Uptime
    cur.execute("SELECT EXTRACT(EPOCH FROM current_timestamp - pg_postmaster_start_time())")
    uptime_seconds = float(cur.fetchone()[0])
    uptime_gauge.set(uptime_seconds)
    uptime_hours_gauge.set(uptime_seconds / 3600)

    cur.close()
    conn.close()

if __name__ == "__main__":
    start_http_server(9101)
    print("Custom PostgreSQL exporter running on port 9101")
    while True:
        collect_metrics()
        time.sleep(15)
