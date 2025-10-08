import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# --- Настройки подключения к PostgreSQL ---
DB_CONFIG = {
    "host": "localhost",		#your host
    "port": 5432,               #your port
    "user": "postgres",			#your user
    "password": "1234",			#your password
    "database": "football_db"  
}

# --- SQL для создания таблиц ---
CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS public.clubs (
        club_id int4 NOT NULL,
        club_code varchar(100) NULL,
        "name" varchar(150) NULL,
        domestic_competition_id varchar(10) NULL,
        total_market_value varchar(50) NULL,
        squad_size int4 NULL,
        average_age numeric(4, 1) NULL,
        foreigners_number int4 NULL,
        foreigners_percentage numeric(4, 1) NULL,
        national_team_players int4 NULL,
        stadium_name varchar(150) NULL,
        stadium_seats int4 NULL,
        net_transfer_record varchar(50) NULL,
        coach_name varchar(100) NULL,
        last_season int4 NULL,
        filename varchar(255) NULL,
        url varchar(255) NULL,
        CONSTRAINT clubs_pkey PRIMARY KEY (club_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.players (
        player_id int4 NOT NULL,
        first_name varchar(50) NULL,
        last_name varchar(50) NULL,
        "name" varchar(100) NULL,
        last_season varchar(10) NULL,
        current_club_id int4 NULL,
        player_code varchar(50) NULL,
        country_of_birth varchar(100) NULL,
        city_of_birth varchar(100) NULL,
        country_of_citizenship varchar(100) NULL,
        date_of_birth date NULL,
        sub_position varchar(50) NULL,
        "position" varchar(50) NULL,
        foot varchar(10) NULL,
        height_in_cm int4 NULL,
        contract_expiration_date date NULL,
        agent_name varchar(100) NULL,
        image_url text NULL,
        url text NULL,
        current_club_domestic_competition_id varchar(10) NULL,
        current_club_name varchar(100) NULL,
        market_value_in_eur numeric NULL,
        highest_market_value_in_eur numeric NULL,
        CONSTRAINT players_pkey PRIMARY KEY (player_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.games (
        game_id INT PRIMARY KEY,
        competition_id VARCHAR(10),
        season INT,
        round VARCHAR(50),
        date DATE,
        home_club_id INT,
        away_club_id INT,
        home_club_goals INT,
        away_club_goals INT,
        home_club_position INT,
        away_club_position INT,
        home_club_manager_name VARCHAR(100),
        away_club_manager_name VARCHAR(100),
        stadium VARCHAR(100),
        attendance INT,
        referee VARCHAR(100),
        url TEXT,
        home_club_formation VARCHAR(50),
        away_club_formation VARCHAR(50),
        home_club_name VARCHAR(100),
        away_club_name VARCHAR(100),
        aggregate VARCHAR(10),
        competition_type VARCHAR(50)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.appearances (
        appearance_id varchar(20) NOT NULL,
        game_id int4 NULL,
        player_id int4 NULL,
        player_club_id int4 NULL,
        player_current_club_id int4 NULL,
        "date" date NULL,
        player_name varchar(100) NULL,
        competition_id varchar(20) NULL,
        yellow_cards int4 NULL,
        red_cards int4 NULL,
        goals int4 NULL,
        assists int4 NULL,
        minutes_played int4 NULL,
        CONSTRAINT appearances_pkey PRIMARY KEY (appearance_id),
        CONSTRAINT fk_appearances_player FOREIGN KEY (player_id) REFERENCES public.players(player_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.player_valuations (
        player_id int4 NULL,
        "date" date NULL,
        market_value_in_eur numeric NULL,
        current_club_id int4 NULL,
        player_club_domestic_competition_id varchar(10) NULL,
        CONSTRAINT fk_valuations_player FOREIGN KEY (player_id) REFERENCES public.players(player_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.transfers (
        player_id int4 NULL,
        transfer_date date NULL,
        transfer_season varchar(10) NULL,
        from_club_id int4 NULL,
        to_club_id int4 NULL,
        from_club_name varchar(100) NULL,
        to_club_name varchar(100) NULL,
        transfer_fee varchar(50) NULL,
        market_value_in_eur numeric NULL,
        player_name varchar(100) NULL,
        CONSTRAINT fk_transfers_player FOREIGN KEY (player_id) REFERENCES public.players(player_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.game_lineups (
        game_lineups_id varchar(50) NOT NULL,
        "date" date NULL,
        game_id int4 NULL,
        player_id int4 NULL,
        club_id int4 NULL,
        player_name varchar(100) NULL,
        "type" varchar(50) NULL,
        "position" varchar(50) NULL,
        "number" varchar(50) NULL,
        team_captain bool NULL,
        CONSTRAINT game_lineups_pkey PRIMARY KEY (game_lineups_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.game_events (
        game_event_id varchar(50) NOT NULL,
        "date" date NULL,
        game_id int4 NULL,
        "minute" int4 NULL,
        "type" varchar(50) NULL,
        club_id int4 NULL,
        player_id int4 NULL,
        description text NULL,
        player_in_id int4 NULL,
        player_assist_id int4 NULL,
        CONSTRAINT game_events_pkey1 PRIMARY KEY (game_event_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS public.club_games (
        game_id int4 NULL,
        club_id int4 NULL,
        own_goals int4 NULL,
        own_position int4 NULL,
        own_manager_name varchar(100) NULL,
        opponent_id int4 NULL,
        opponent_goals int4 NULL,
        opponent_position int4 NULL,
        opponent_manager_name varchar(100) NULL,
        hosting varchar(10) NULL,
        is_win bool NULL
    );
    """
]

def create_database():
    """Создание базы данных, если её нет."""
    conn = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_CONFIG["database"],))
    exists = cur.fetchone()

    if not exists:
        cur.execute(f'CREATE DATABASE "{DB_CONFIG["database"]}";')
        print(f"✅ Database '{DB_CONFIG['database']}' created.")
    else:
        print(f"ℹ️ Database '{DB_CONFIG['database']}' already exists.")

    cur.close()
    conn.close()


def create_tables():
    """Создание всех таблиц."""
    conn = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        dbname=DB_CONFIG["database"]
    )
    cur = conn.cursor()

    for sql in CREATE_TABLES_SQL:
        cur.execute(sql)
    conn.commit()

    print("✅ All tables created successfully.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database()
    create_tables()
