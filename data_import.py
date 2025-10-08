import psycopg2
import os

# --- Настройки подключения к базе ---
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",   # your user
    "password": "1234",   # your password
    "dbname": "football_db"
}

# 📁 Путь к папке с CSV файлами
DATA_DIR = r"your directory to file"   # 👈 сюда укажи путь к папке, где лежат все CSV

# --- Список файлов и таблиц ---
IMPORT_CONFIG = [
    ("appearances", "appearances.csv", 
     "(appearance_id, game_id, player_id, player_club_id, player_current_club_id, date, player_name, competition_id, yellow_cards, red_cards, goals, assists, minutes_played)"),
    
    ("player_valuations", "player_valuations.csv", 
     "(player_id, date, market_value_in_eur, current_club_id, player_club_domestic_competition_id)"),
    
    ("players", "players.csv", 
     "(player_id, first_name, last_name, name, last_season, current_club_id, player_code, country_of_birth, city_of_birth, country_of_citizenship, date_of_birth, sub_position, position, foot, height_in_cm, contract_expiration_date, agent_name, image_url, url, current_club_domestic_competition_id, current_club_name, market_value_in_eur, highest_market_value_in_eur)"),
    
    ("transfers", "transfers.csv", 
     "(player_id, transfer_date, transfer_season, from_club_id, to_club_id, from_club_name, to_club_name, transfer_fee, market_value_in_eur, player_name)"),
    
    ("clubs", "clubs.csv", 
     "(club_id, club_code, name, domestic_competition_id, total_market_value, squad_size, average_age, foreigners_number, foreigners_percentage, national_team_players, stadium_name, stadium_seats, net_transfer_record, coach_name, last_season, filename, url)"),
    
    ("games", "games.csv",
     "(game_id, competition_id, season, round, date, home_club_id, away_club_id, home_club_goals, away_club_goals, home_club_position, away_club_position, home_club_manager_name, away_club_manager_name, stadium, attendance, referee, url, home_club_formation, away_club_formation, home_club_name, away_club_name, aggregate, competition_type)"),
    
    ("club_games", "club_games.csv",
     "(game_id, club_id, own_goals, own_position, own_manager_name, opponent_id, opponent_goals, opponent_position, opponent_manager_name, hosting, is_win)"),
    
    ("game_events", "game_events.csv",
     "(game_event_id, date, game_id, minute, type, club_id, player_id, description, player_in_id, player_assist_id)"),
    
    ("game_lineups", "game_lineups.csv",
     "(game_lineups_id, date, game_id, player_id, club_id, player_name, type, position, number, team_captain)")
]

def import_csv_to_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for table, filename, columns in IMPORT_CONFIG:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"⚠️  Файл не найден: {filepath}")
            continue

        sql = f"""
            COPY {table} {columns}
            FROM STDIN
            DELIMITER ','
            CSV HEADER
            NULL '';
        """
        print(f"⏳ Импортирую {filename} в таблицу {table} ...")
        with open(filepath, "r", encoding="utf-8") as f:
            cur.copy_expert(sql, f)
        print(f"✅ {filename} успешно импортирован в {table}")

    conn.commit()
    cur.close()
    conn.close()
    print("\n🎉 Все данные успешно импортированы!")

if __name__ == "__main__":
    import_csv_to_db()
