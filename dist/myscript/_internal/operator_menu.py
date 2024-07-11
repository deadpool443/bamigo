import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import logging
from database import init_settings_db, get_settings, save_settings, retrieve_game_logs

logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def display_game_logs(root):
    try:
        logs_window = tk.Toplevel(root)
        logs_window.title("Game Logs")
        logs_window.grab_set()
        
        tree = ttk.Treeview(logs_window, columns=("App ID", "Game Name", "Duration", "Timestamp"), show="headings")
        tree.pack(fill="both", expand=True)
        
        tree.heading("App ID", text="App ID")
        tree.heading("Game Name", text="Game Name")
        tree.heading("Duration", text="Duration")
        tree.heading("Timestamp", text="Timestamp")
        
        logs = retrieve_game_logs()
        
        for log in logs:
            app_id, game_name, game_duration, timestamp = log
            tree.insert("", "end", values=(app_id, game_name, game_duration, timestamp))
    except Exception as e:
        logging.error(f"Error while displaying game logs: {str(e)}")

def browse_file(entry, title, filetypes):
    try:
        file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)
    except Exception as e:
        logging.error(f"Error while browsing file: {str(e)}")

def handle_operator_menu(root, controls):
    global video_path, start_video_flag
    
    settings = get_settings()
    video_path = settings[1]
    start_video_flag = False
    
    operator_window = tk.Toplevel(root)
    operator_window.title("Operator Menu")
    operator_window.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
    
    frame = tk.Frame(operator_window)
    frame.pack(expand=True, fill="both", padx=20, pady=20)
    
    tk.Label(frame, text='Time Per Credit:').pack(pady=(10, 0))
    time_per_credit_entry = tk.Entry(frame)
    time_per_credit_entry.pack()
    time_per_credit_entry.insert(0, str(settings[0]))
    
    video_path_entry = tk.Entry(frame)
    tk.Label(frame, text='Video Path:').pack(pady=(10, 0))
    video_path_entry.pack()
    video_path_entry.insert(0, video_path)
    
    tk.Button(frame, text='Browse', command=lambda: browse_file(video_path_entry, "Select Video File", [("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("MKV files", "*.mkv"), ("All files", "*.*")])).pack(pady=(10, 0))
    
    reset_image_path_entry = tk.Entry(frame)
    tk.Label(frame, text='Reset Headset Image Path:').pack(pady=(10, 0))
    reset_image_path_entry.pack()
    reset_image_path_entry.insert(0, str(settings[2]))
    
    tk.Button(frame, text='Browse', command=lambda: browse_file(reset_image_path_entry, "Select Reset Headset Image", [("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*")])).pack(pady=(10, 0))
    
    restart_image_path_entry = tk.Entry(frame)
    tk.Label(frame, text='Restart SteamVR Image Path:').pack(pady=(10, 0))
    restart_image_path_entry.pack()
    restart_image_path_entry.insert(0, str(settings[3]))
    
    tk.Button(frame, text='Browse', command=lambda: browse_file(restart_image_path_entry, "Select Restart SteamVR Image", [("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*")])).pack(pady=(10, 0))
    
    def open_game_settings():
        game_window = tk.Toplevel(operator_window)
        game_window.title("Game Settings")
        import game_setting_gui
        game_setting_gui.show_games(game_window)
    
    def save_and_exit():
        global video_path, start_video_flag
        video_path = video_path_entry.get()
        save_settings(float(time_per_credit_entry.get()), video_path, reset_image_path_entry.get(), restart_image_path_entry.get())
        
        operator_window.destroy()
        root.deiconify()
        controls.set_video_path(video_path)
        controls.start_video()
        
        logging.info("Settings saved and video path set. Start video flag set to True.")
    
    def exit_without_saving():
        operator_window.destroy()
        root.deiconify()
        controls.start_video()
        logging.info("Exited without saving and set start video flag to True.")
    
    tk.Button(frame, text='Game Settings', command=open_game_settings).pack(pady=(10, 0))
    tk.Button(frame, text='Check Logs', command=lambda: display_game_logs(operator_window)).pack(pady=(10, 0))
    tk.Button(frame, text='Save and Exit', command=save_and_exit).pack(pady=(10, 0))
    tk.Button(frame, text='Exit Without Saving', command=exit_without_saving).pack(pady=(10, 0))
    
    operator_window.focus_force()
    root.withdraw()
    #operator_window.mainloop()

def display_operator_menu(root, controls):
    try:
        handle_operator_menu(root, controls)
    except Exception as e:
        logging.error(f"Error while displaying operator menu: {str(e)}")
