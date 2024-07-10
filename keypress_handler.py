from codecs import CodecInfo
import keyboard
import logging
from video_controls import VideoControls
import time
import threading
from database import credit_updater, current_credit
import sys


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    
def handle_keypress(parent, controls, game_menu_flag, operator_menu_flag, credits_text):
    logging.info("Key press handler is active")

    def on_c_press():
        if current_credit() == 0:
            controls.stop_video()
            credit_updater(credits_text)
            game_menu_flag.set()
            logging.info("Game menu flag is set")
        else:
            credit_updater(credits_text)

    def on_o_press():
        logging.info("'o' key pressed - opening operator menu.")
        operator_menu_flag.set()
        logging.info("Operator menu flag is set")

    def on_q_press():
        logging.info("'q' key pressed - stopping video and quitting.")
        controls.stop_video()  # Stop the video playback
        keyboard.unhook_all()  # Unhook all keys to clean up
        parent.quit()  # Quit the main application loop
        sys.exit()

    # Setup hotkeys
    keyboard.add_hotkey('c', on_c_press)
    keyboard.add_hotkey('o', on_o_press)
    keyboard.add_hotkey('q', on_q_press)

    # Wait for the 'q' key to be pressed
    while True:
        if keyboard.is_pressed('q'):
            on_q_press()
            break
        time.sleep(0.1)