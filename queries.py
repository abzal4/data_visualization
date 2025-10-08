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
    print("Players with Most goals  in 23/24 season")
    q1 = """select c.domestic_competition_id as league,c.name as club,p.name as player, goals from(select a.player_id as id, sum(a.goals) as goals from appearances a 
            left join games g on a.game_id = g.game_id 
            where g.competition_type = 'domestic_league' and (a."date" between '2023-07-01' and '2024-08-10') group by a.player_id) as s
            left join players p on s.id = p.player_id 
            left join clubs c on p.current_club_id = c.club_id 
            order by goals desc limit 5"""
    df1 = run_query(q1)
    print(df1)

    print("Most successfull partners (Clubs with the most transfer spendings between them)")
    q2 = """SELECT * FROM (
            select t.from_club_name, t.to_club_name, count(*) as transfers, sum(t.market_value_in_eur) as total_spendings from transfers t 
            group by t.from_club_name, t.to_club_name 
            order by total_spendings desc
            ) z_q WHERE total_spendings IS NOT NULL"""
    df2 = run_query(q2)
    print(df2)

    print("Average home goals of clubs for last 5 years")
    q3 = """select c."name", round((sum(g.home_club_goals)::numeric/count(g.game_id)),2) as gaols_per_match  from clubs c left join games g on c.club_id = g.home_club_id where g."date" between '2020-09-21' and '2025-09-21' group by c.club_id """
    df3 = run_query(q3)
    print(df3)

    print("The most attendance for clubs(at home)")
    q4 = """select c.name, max(g.attendance) from  clubs c left join games g on c.club_id = g.home_club_id group by c.club_id  order by max desc"""
    df4 = run_query(q4)
    print(df4)

    print("Players with the most minutes for 23/24 season")
    q5 = """select p."name", sum(a.minutes_played) as minutes from players p
            left join appearances a on p.player_id = a.player_id 
            where (a."date" between '2023-07-01' and '2024-08-10') 
            group by p.player_id 
            order by minutes desc"""
    df5 = run_query(q5)
    print(df5)

    print("Clubs with the most expenses for the last 10 years")
    q6 = """select c.name, sum(t.market_value_in_eur) as expenses from clubs c
            left join transfers t on c.club_id = t.to_club_id 
            where t.transfer_date  >'2015-07-01' 
            group by c."name" 
            order by expenses desc"""
    df6 = run_query(q6)
    print(df6)

    print("Top 10 the most aggressive players(most red and yellow cards)")
    q7 = """select p."name" , (sum(a.red_cards)*2+sum(a.yellow_cards)) as agressivness from players p 
            inner join appearances a on p.player_id = a.player_id 
            group by p.player_id 
            order by agressivness desc limit 10"""
    df7 = run_query(q7)
    print(df7)

    print("Average attendance for clubs")
    q8 = """select c."name", round(avg(g.attendance),0) as att from clubs c
            left join games g on c.club_id = g.home_club_id 
            group by c.club_id 
            order by att desc"""
    df8 = run_query(q8)
    print(df8)

    print("The most finals in Champions League for the last 10 years")
    q9 = """select c."name", count(*) as CL_finals from clubs c 
            left join games g on c.club_id = g.home_club_id or c.club_id = g.away_club_id 
            where g.competition_id ='CL' and g.round = 'Final' and g.season >=2015
            group by c.club_id 
            order by cl_finals desc"""
    df9 = run_query(q9)
    print(df9)

    print("Best coaches and their games")
    q10 = """with t as 
            (select g.home_club_manager_name as manager, count(*)  as total from games g
            group by g.home_club_manager_name),
            w as
            (select g.home_club_manager_name as manager,count(*) as won from games g  
            where g.home_club_goals > g.away_club_goals 
            group by g.home_club_manager_name)
            select t.manager, t.total, w.won from t 
            left join w on t.manager = w.manager 
            where w.won is not null
            order by won desc """
    df10 = run_query(q10)
    print(df10)

if __name__ == "__main__":
    main()
