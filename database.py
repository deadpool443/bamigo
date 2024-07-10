from ast import Global
import sqlite3
import logging
import os
import datetime
import winreg
import re
import glob
import requests

# Global variables
time_per_credit = None
video_path = None
credit_counter = 0
guitext = None

"""Functions to log game play"""

def log_game_played(app_id, game_name, game_duration):
    """Log the played game to the database."""
    try:
        with get_db_connection("game_logs.db") as conn:
            cursor = conn.cursor()
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO game_logs (app_id, game_name, game_duration, timestamp)
                VALUES (?, ?, ?, ?)
            """, (app_id, game_name, game_duration, current_time))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error during game logging: {e}")
        
def create_game_logs_table():
    """Create the game logs table if it does not already exist."""
    with get_db_connection("game_logs.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT,
                game_name TEXT,
                game_duration REAL,
                timestamp TEXT
            )
        """)
        conn.commit()
        
def retrieve_game_logs():
    """Retrieve all game logs from the database."""
    with get_db_connection("game_logs.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT app_id, game_name, game_duration, timestamp FROM game_logs")
        logs = cursor.fetchall()
        return logs
  
""" Functions for credit management"""


def credit_updater(credits_text):
    global credit_counter
    credit_counter += 1
    update_credits_label(credits_text)
    

def current_credit():
        global credit_counter
        return credit_counter
    

def reset_credit(credit_text):
        global credit_counter
        credit_counter=0
        update_credits_label(credit_text)

def get_game_duration():
         return credit_counter*time_per_credit*60 #to convert minutes into seconds
    
def update_credits_label(credits_text):
    credit = current_credit()
    credits_text.set(f"CREDITS: {int(credit)}")



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


"""Game Database Functions"""

def get_steam_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Valve\\Steam")
        steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
        return steam_path
    except (FileNotFoundError, OSError):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam")
            steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
            return steam_path
        except (FileNotFoundError, OSError):
            return None

def get_library_folders(steam_path):
    library_folders = [steam_path]
    libraryfolders_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    if os.path.exists(libraryfolders_path):
        with open(libraryfolders_path, "r") as file:
            content = file.read()
            matches = re.findall(r'"(\d+)"\s+"(.+)"', content)
            for match in matches:
                library_folders.append(match[1].replace("\\\\", "\\"))
    return library_folders

def find_executable(game_name, game_path):
    if os.path.exists(game_path):
        game_name_words = re.findall(r'\w+', game_name.lower())
        exe_files = []
        for root, dirs, files in os.walk(game_path):
            for file in files:
                if file.lower().endswith(".exe"):
                    exe_files.append((file, os.path.join(root, file)))
        exe_files.sort(key=lambda x: sum(word in x[0].lower() for word in game_name_words), reverse=True)
        if exe_files:
            return exe_files[0][1]
    return None

def get_game_image(app_id):
    image_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{app_id}/header.jpg"
    response = requests.get(image_url)
    if response.status_code == 200:
        image_path = os.path.join("images", f"{app_id}.jpg")
        os.makedirs("images", exist_ok=True)
        with open(image_path, "wb") as file:
            file.write(response.content)
        return image_path
    return None

def get_steam_games():
    steam_path = get_steam_path()
    if not steam_path:
        print("Steam installation not found.")
        return []

    library_folders = get_library_folders(steam_path)
    games = []

    for library_folder in library_folders:
        manifest_files = os.path.join(library_folder, "steamapps", "*.acf")
        for manifest_file in glob.glob(manifest_files):
            with open(manifest_file, "r") as file:
                content = file.read()
                app_id_matches = re.findall(r'"appid"\s+"(\d+)"', content)
                for app_id in app_id_matches:
                    name_match = re.search(r'"name"\s+"(.+)"', content)
                    game_name = name_match.group(1) if name_match else ""
                    game_path = os.path.join(library_folder, "steamapps", "common", game_name)
                    game_executable = find_executable(game_name, game_path)
                    game_image = get_game_image(app_id)
                    games.append((app_id, game_name, game_executable, game_image))

    return games


def get_db_connection(db_file):
    """Utility function to create and return a database connection."""
    return sqlite3.connect(db_file)

def create_database():
    """Create the game database and table if they do not already exist."""
    with get_db_connection("steam_games.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                app_id TEXT PRIMARY KEY,
                name TEXT,
                executable TEXT,
                image TEXT,
                show_game INTEGER
            )
        """)
        conn.commit()
    

def update_game_in_database(app_id, game_name, game_executable, game_image, show_game):
    """Update an existing game's details in the database."""
    try:
        with get_db_connection("steam_games.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE games
                SET name = ?, executable = ?, image = ?, show_game = ?
                WHERE app_id = ?
            """, (game_name, game_executable, game_image, show_game, app_id))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error during game update: {e}")
        
def insert_game_into_database(app_id, game_name, game_executable, game_image):
    """Insert a new game into the database."""
    try:
        with get_db_connection("steam_games.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO games (app_id, name, executable, image, show_game)
                VALUES (?, ?, ?, ?, 1)
            """, (app_id, game_name, game_executable, game_image))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error during game insertion: {e}")

def game_exists_in_database(app_id):
    """Check if a game already exists in the database."""
    with get_db_connection("steam_games.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM games WHERE app_id = ?", (app_id,))
        app_exists = cursor.fetchone()[0]
        return app_exists

def update_database(games):
    """Update the database with new games or skip existing ones."""
    for game in games:
        app_id, game_name, game_executable, game_image = game
        if not game_exists_in_database(app_id):
            insert_game_into_database(app_id, game_name, game_executable, game_image)
            logging.info(f"Added new game: {game_name} (App ID: {app_id})")
        else:
            logging.info(f"Game with App ID {app_id} already exists. Skipping.")

def retrieve_games():
    """Retrieve all games marked to be shown from the database."""
    with get_db_connection("steam_games.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, app_id, executable, image FROM games WHERE show_game=1")
        games = cursor.fetchall()
        return games

# Settings management
def init_settings_db():
    """Initialize the settings database and create the necessary tables."""
    with get_db_connection('settings.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time_per_credit REAL,
                video_path TEXT,
                reset_image_path TEXT,
                restart_image_path TEXT
            )
        ''')
        # Insert default settings if they do not exist
        default_video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'video.mp4')
        default_reset_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reset.jpg')
        default_restart_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restart.jpg')

        cursor.execute('''
            INSERT OR IGNORE INTO settings (time_per_credit, video_path, reset_image_path, restart_image_path)
            VALUES (1.0, ?, ?, ?)
        ''', (default_video_path, default_reset_image_path, default_restart_image_path))
        conn.commit()

    # Ensure games table is created
    create_database()
    get_settings()
    create_game_logs_table()
    games = get_steam_games()
    update_database(games)



    
def get_settings():
    """Retrieve the settings from the database and update global variables."""
    global time_per_credit, video_path, reset_image_path, restart_image_path
    with get_db_connection('settings.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT time_per_credit, video_path, reset_image_path, restart_image_path FROM settings')
        result = cursor.fetchone()
        if result:
            time_per_credit, video_path, reset_image_path, restart_image_path = result
        else:
            logging.error("No settings found in the database.")
        return result


def save_settings(time_per_credit, video_path, reset_image_path, restart_image_path):
    """Save the specified settings to the database."""
    try:
        with get_db_connection('settings.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM settings')
            cursor.execute('INSERT INTO settings (time_per_credit, video_path, reset_image_path, restart_image_path) VALUES (?, ?, ?, ?)', 
                           (time_per_credit, video_path, reset_image_path, restart_image_path))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error during settings save: {e}")

        