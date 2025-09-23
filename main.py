import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "abzal"
}

def get_conn():
    conn_str = "host={host} port={port} dbname={dbname} user={user} password={password}".format(**DB)
    return psycopg2.connect(conn_str)

def run_query(sql):
    with get_conn() as conn:
        df = pd.read_sql(sql, conn)
    return df

def main():
    print("5 clubs")
    q1 = "select name, stadium_name from clubs limit 5"
    df1 = run_query(q1)
    print(df1)

    print("5 FCB players")
    q2 = "select * from players where current_club_name = 'Futbol Club Barcelona' order by last_season desc limit 5"
    df2 = run_query(q2)
    print(df2)

    print("Most agressive 10 players")
    q3 = "select p.name , (sum(a.red_cards)*2+sum(a.yellow_cards)) as agressivness from players p inner join appearances a on p.player_id = a.player_id group by p.player_id order by agressivness desc limit 10"
    df3 = run_query(q3)
    print(df3)

if __name__ == "__main__":
    main()