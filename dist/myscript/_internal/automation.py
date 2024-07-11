import time
import pyautogui
import pygetwindow as gw
from database import get_settings
import openvr
import logging
from tkinter import Tk, Label, Frame
import webbrowser
from queue import Queue
import threading
import psutil
import subprocess

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def reboot_steamvr():
    # Reboot SteamVR using vrmonitor command
    webbrowser.open("vrmonitor://reboothmd")

    # Wait for SteamVR to restart (adjust the delay as needed)
    time.sleep(20)

def is_virtual_desktop_connected():
    # Check if Virtual Desktop is connected using Python
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'VirtualDesktop.Server.exe':
            return True
    return False

def is_steamvr_connected():
    try:
        vr_system = openvr.init(openvr.VRApplication_Background)
        is_connected = vr_system.isTrackedDeviceConnected(openvr.k_unTrackedDeviceIndex_Hmd)
        openvr.shutdown()
        return is_connected
    except openvr.OpenVRError:
        return False

def detect_virtual_desktop(queue):
    max_attempts = 100
    attempt_count = 0

    while attempt_count < max_attempts:
        if is_virtual_desktop_connected():
            logger.info("Headset is connected.")
            queue.put("connected")
            break

        logger.info("Headset is not connected. Waiting...")
        queue.put("not_connected")
        time.sleep(5)  # Wait for a short interval before checking again
        attempt_count += 1

    if attempt_count == max_attempts:
        logger.warning("Headset not detected after maximum attempts.")
        queue.put("not_connected")

def update_dialog(label, message):
    label.config(text=message)
    label.update()

def handle_headset_not_detected():
    queue = Queue()

    window = Tk()
    window.title("Virtual Desktop Connection Status")

    # Set the window to full-screen mode
    window.attributes('-fullscreen', True)

    # Create a frame to center the label
    frame = Frame(window)
    frame.pack(expand=True)

    # Create a label to display the message
    label = Label(frame, text="Checking Virtual Desktop Connection...", font=("Arial", 24))
    label.pack(pady=20)

    window.update()

    # Start the Virtual Desktop detection thread
    detection_thread = threading.Thread(target=detect_virtual_desktop, args=(queue,))
    detection_thread.start()

    while True:
        if not queue.empty():
            status = queue.get()
            if status == "connected":
                update_dialog(label, "Virtual Desktop Connected. Checking SteamVR Connection...")
                
                if not is_steamvr_connected():
                    update_dialog(label, "SteamVR Not Connected. Rebooting SteamVR...")
                    time.sleep(3)  # Delay before rebooting SteamVR
                    reboot_steamvr()
                
                window.destroy()
                break
            else:
                update_dialog(label, "Virtual Desktop Not Connected. Please Check Connection.")

        window.update()
        time.sleep(0.1)  # Small delay to avoid high CPU usage

    # Wait for the detection thread to complete
    detection_thread.join()

    return status

def check_and_launch_applications():
    def is_process_running(process_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False

    def launch_application(application_path):
        subprocess.Popen(application_path)
        time.sleep(10)  # Wait for the application to launch (adjust the delay as needed)

    steam_path = r"C:\Program Files (x86)\Steam\steam.exe"  # Update with the correct path to Steam executable
    virtual_desktop_path = r"C:\Program Files\Virtual Desktop Streamer\VirtualDesktop.Streamer.exe"  # Update with the correct path to Virtual Desktop executable

    if not is_process_running("steam.exe"):
        logger.info("Steam is not running. Launching Steam...")
        launch_application(steam_path)
    else:
        logger.info("Steam is already running.")

    if not is_process_running("VirtualDesktop.Streamer.exe"):
        logger.info("Virtual Desktop is not running. Launching Virtual Desktop...")
        launch_application(virtual_desktop_path)
    else:
        logger.info("Virtual Desktop is already running.")

def restart_steamvr():
    # Retrieve image paths from settings
    settings = get_settings()
    restart_image_path = settings[3]  # Assuming get_settings()[3] returns the restart image path
    
    start_time = time.time()
    while time.time() - start_time < 30:  # Run for 30 seconds
        try:
            # Use pyautogui to locate the "Restart SteamVR" image on the screen and click it
            restart_location = pyautogui.locateOnScreen(restart_image_path, confidence=0.8)
            if restart_location:
                pyautogui.click(restart_location)
                print("Clicked the 'Restart SteamVR' using the image.")
                break  # Exit the loop if the button is clicked
            else:
                print("'Restart SteamVR' image not found on screen.")
        except Exception as e:
            print(f"Error clicking the 'Restart SteamVR' button: {e}")

        time.sleep(1)  # Wait for 1 second before retrying
    print("Finished attempting to restart SteamVR")

def toggle_vr_mode():
    # Find the Virtual Desktop window
    windows = gw.getWindowsWithTitle('Virtual Desktop')
    if not windows:
        print("Virtual Desktop window not found.")
        return
    
    # Activate the Virtual Desktop window
    virtual_desktop_window = windows[0]
    virtual_desktop_window.activate()
    time.sleep(1)  # Give some time for the window to be activated
    
    # Send the Alt+V keystroke to toggle VR mode
    pyautogui.hotkey('shift', 'win', 'd')
    print("Alt+V sent to Virtual Desktop.")
    
    # Minimize the Virtual Desktop window
    virtual_desktop_window.minimize()
    print("Virtual Desktop window minimized.")

if __name__ == "__main__":
    # Call each function independently as needed
    toggle_vr_mode()
    handle_headset_not_detected()
    restart_steamvr()
