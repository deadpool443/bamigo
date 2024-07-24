import webbrowser
import time
import tkinter as tk
import psutil
from tkinter import messagebox
import difflib
from database import get_game_duration, reset_credit, log_game_played
from automation import restart_steamvr, toggle_vr_mode, handle_headset_not_detected, check_and_launch_applications
import threading

# Define a global flag for stopping threads
stop_threads = threading.Event()

def game_duration():
    game_duration = get_game_duration()
    return game_duration

def close_game_process(game_name):
    print(f"Closing game process with name: {game_name}")
    max_ratio = 0
    max_ratio_proc = None

    for proc in psutil.process_iter(['name']):
        try:
            proc_name = proc.info['name']
            ratio = difflib.SequenceMatcher(None, game_name.lower(), proc_name.lower()).ratio()
            print(f"Process: {proc_name}, Ratio: {ratio}")
            if ratio > max_ratio:
                max_ratio = ratio
                max_ratio_proc = proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if max_ratio_proc:
        print(f"Found process: {max_ratio_proc.info}")
        print(f"Process name: {max_ratio_proc.info['name']}")
        
        # Terminate the main process and its subprocesses
        process = psutil.Process(max_ratio_proc.pid)
        print(f"Terminating process with PID: {process.pid}")
        subprocesses = process.children(recursive=True)
        for subprocess in subprocesses:
            print(f"Terminating subprocess with PID: {subprocess.pid}")
            subprocess.terminate()
        process.terminate()
        
        print("Process and its subprocesses terminated")
    else:
        print("Process not found")

def handle_headset_not_detected_thread():
    #while not stop_threads.is_set():
        handle_headset_not_detected()
        time.sleep(5)  # Adjust the sleep time as needed

def restart_steamvr_thread():
    #while not stop_threads.is_set():
        restart_steamvr()
        time.sleep(5)  # Adjust the sleep time as needed

def run_game(game_name, app_id, credit_text, controls, window):
    # def show_countdown(game_duration):
    #    countdown_window = tk.Toplevel(window)
    #    countdown_window.title("game  timer")
    #    countdown_label=tk.Label(countdown_window,font=("Arial",30))
    
    #    countdown_label.pack(padx=20,pady=20)

    #    def update_countdown():
    #        nonlocal game_duration
    #        while game_duration>0 and countdown_window.winfo_exists():
    #            minutes,seconds=divmod(game_duration,60)
    #            countdown_label.config(text=f"{minutes:02}:{seconds:02}")
    #            countdown_window.update()
    #            time.sleep(1)
    #            game_duration=-1
    #        if countdown_window.winfo_exists():
    #             countdown_window.destroy()
    #    countdown_thread= threading.Thread(target=update_countdown)
    #    countdown_thread.start()
        
               
    check_and_launch_applications()
    controls.stop_video()
    game_duration = get_game_duration()
    print(f" Game Duration : {game_duration}")
    
    log_game_played(app_id, game_name, game_duration)
    print(f"Game Play Logged")
    handle_headset_not_detected()
    

    # Start the handle_headset_not_detected and restart_steamvr functions in separate threads
    headset_thread = threading.Thread(target=handle_headset_not_detected_thread)
    steamvr_thread = threading.Thread(target=restart_steamvr_thread)

    headset_thread.start()
    # steamvr_thread.start()
    # Call toggle_vr_mode to send Alt+V keystroke
    toggle_vr_mode()
    time.sleep(1)
    reset_credit(credit_text)
    # Launch the game using the Steam browser protocol
    print(f"Running game: {game_name}")
    webbrowser.open(f"steam://rungameid/{app_id} --fullscreen")
    show_countdown(game_duration)
    # Wait for the specified duration
    time.sleep(game_duration)
    print("Game duration completed")
    """
    # Wait for 1 second before closing the game
    time.sleep(1)

    # Add a short delay before closing the game process
    time.sleep(2)
    """
    
    print("Calling close_game_process()")
    # Close the game process
    close_game_process(game_name)
    print("Finished running game")
    toggle_vr_mode()
    
    window.destroy()
    controls.start_video()
    print("Exiting loop")

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
