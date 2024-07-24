import threading
import logging
from video_controls import VideoControls
from keypress_handler import handle_keypress
from operator_menu import display_operator_menu
from game_menu import display_game_menu
import time
from database import create_database, update_game_in_database, insert_game_into_database, game_exists_in_database, current_credit, update_credits_label
from database import init_settings_db, get_settings, save_settings
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from license import validate_license
import os
from automation import check_and_launch_applications
import sys


# Global variables
global video_path, operator_menu_flag, game_menu_flag, root, controls, start_video_flag, credits_text
video_path = ""
operator_menu_flag = None
game_menu_flag = None
root = None
controls = None
start_video_flag = False
credits_text = None

# Setting up logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to check the game menu flag and display the game menu if set

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def check_game_menu_flag(root, controls, credits_text):
    if game_menu_flag.is_set():
        game_menu_flag.clear()
        logging.info("Game menu flag is cleared")
        update_credits_label(credits_text)
        logging.info("Credits Updated")
        display_game_menu(root, controls, credits_text)
        logging.info("display game menu function executed")
    root.after(100, check_game_menu_flag, root, controls, credits_text)

# Function to start video playback
def video_playback(controls):
    logging.info("Starting video playback")
    try:
        controls.start_video()
    except Exception as e:
        logging.error(f"Error during video playback: {str(e)}")

# Function to check the operator menu flag and display the operator menu if set
def check_operator_menu_flag(root, controls):
    if operator_menu_flag.is_set():
        operator_menu_flag.clear()
        logging.info("Operator menu flag is cleared")
        controls.stop_video()
        display_operator_menu(root, controls)
    root.after(100, check_operator_menu_flag, root, controls)

# Main function
def main():
    # Set your Keygen account ID
    os.environ['KEYGEN_ACCOUNT_ID'] = '3277a802-64e3-4001-816e-aa4430d6b72d'

    # Validate the license
    if validate_license():
        # License is valid, continue with your application logic
        logging.info("License is valid. Starting the application...")
        # Your application code goes here
        # ...
    else:
        # License validation failed, exit the application
        logging.error("License validation failed. Exiting the application.")
        exit(1)
    
    check_and_launch_applications()
    
    global operator_menu_flag, game_menu_flag, root, controls, start_video_flag
    global credits_text
    
    logging.info("Main function started")
    init_settings_db()

    # Create threading events for game menu and operator menu
    game_menu_flag = threading.Event()
    operator_menu_flag = threading.Event()
    
    # Create the main window
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
    root.configure(background="black")
    root.overrideredirect(True)
    
    # Create the credits frame and label
    credits_frame = ctk.CTkFrame(root, fg_color="blue", height=int(root.winfo_screenheight() * 0.05))
    credits_frame.pack(fill="both", expand=True)

    credits_text = ctk.StringVar()
    credits_label = ctk.CTkLabel(credits_frame, textvariable=credits_text, font=("Arial", 100, "bold"), text_color="white")
    credits_label.pack(pady=10)
    update_credits_label(credits_text)
    
    # Retrieve settings from the database
    settings = get_settings()

    if not settings:
        logging.error("Failed to retrieve settings.")
        return
    video_path = r'C:\Users\Bamigos\Desktop\metacade try\video.mp4'
    reset_image_path = r'C:\Users\Bamigos\Desktop\metacade try\resetheadset.png'
    restart_image_path = r'C:\Users\Bamigos\Desktop\metacade try\restartsteamvr.png'

    logging.info(f"Video path set to: {video_path}")
    logging.info(f"Reset headset image path set to: {reset_image_path}")
    logging.info(f"Restart SteamVR image path set to: {restart_image_path}")
    plugin_path = resource_path('C:\\Program Files\\VideoLAN\\VLC\\plugins')
    logging.info(f"VLC plugin path set to: {plugin_path}")

    try:
        controls = VideoControls(video_path, loop=True,plugin_path=plugin_path)
    except Exception as e:
        logging.error(f"Error initializing VideoControls: {e}")
        logging.exception("Exception details:")
        sys.exit(1)


    time_per_credit, video_path, reset_image_path, restart_image_path = settings
    logging.info(f"Video path set to: {video_path}")
    logging.info(f"Reset headset image path set to: {reset_image_path}")
    logging.info(f"Restart SteamVR image path set to: {restart_image_path}")
    logging.info(f"VLC plugin path set to: {plugin_path}")
    # Create video controls
    controls = VideoControls(video_path, loop=True,plugin_path=plugin_path)

    # Start video playback in a separate thread
    video_thread = threading.Thread(target=controls.start_video)
    video_thread.daemon = True
    video_thread.start()
    logging.info("Video playback thread started")

    # Start keypress handling in a separate thread
    keypress_thread = threading.Thread(target=handle_keypress, args=(root, controls, game_menu_flag, operator_menu_flag, credits_text))
    keypress_thread.daemon = True
    keypress_thread.start()

    try:
        # Schedule checking of game menu flag and updating credits label
        root.after(100, check_game_menu_flag, root, controls, credits_text)
        root.after(100, update_credits_label, credits_text)
        root.after(100, check_operator_menu_flag, root, controls)
        root.mainloop()
    except KeyboardInterrupt:
        logging.info("Program interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
    finally:
        controls.stop_video()
        logging.info("Main loop ended")


if __name__ == "__main__":
    main()
    sys.exit()