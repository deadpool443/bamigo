import os
import customtkinter as ctk
from tkinter import messagebox
import machineid
import requests
import json
import logging

LICENSE_FILE = 'license.txt'

# Configure logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def activate_license(license_key):
    machine_fingerprint = machineid.hashed_id('example-app')
    validation = requests.post(
        "https://api.keygen.sh/v1/accounts/{}/licenses/actions/validate-key".format(os.environ['KEYGEN_ACCOUNT_ID']),
        headers={
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
        },
        data=json.dumps({
            "meta": {
                "scope": {"fingerprint": machine_fingerprint},
                "key": license_key
            }
        })
    ).json()

    if "errors" in validation:
        errs = validation["errors"]
        error_msg = "license validation failed: {}".format(
            ','.join(map(lambda e: "{} - {}".format(e["title"], e["detail"]).lower(), errs))
        )
        logging.error(error_msg)
        return False, error_msg

    if validation["meta"]["valid"]:
        logging.info("License has already been activated on this machine")
        return True, "license has already been activated on this machine"

    validation_code = validation["meta"]["code"]
    activation_is_required = validation_code == 'FINGERPRINT_SCOPE_MISMATCH' or \
                             validation_code == 'NO_MACHINES' or \
                             validation_code == 'NO_MACHINE'

    if not activation_is_required:
        error_msg = "license {}".format(validation["meta"]["detail"])
        logging.error(error_msg)
        return False, error_msg

    activation = requests.post(
        "https://api.keygen.sh/v1/accounts/{}/machines".format(os.environ['KEYGEN_ACCOUNT_ID']),
        headers={
            "Authorization": "License {}".format(license_key),
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json"
        },
        data=json.dumps({
            "data": {
                "type": "machines",
                "attributes": {
                    "fingerprint": machine_fingerprint
                },
                "relationships": {
                    "license": {
                        "data": {"type": "licenses", "id": validation["data"]["id"]}
                    }
                }
            }
        })
    ).json()

    if "errors" in activation:
        errs = activation["errors"]
        error_msg = "license activation failed: {}".format(
            ','.join(map(lambda e: "{} - {}".format(e["title"], e["detail"]).lower(), errs))
        )
        logging.error(error_msg)
        return False, error_msg

    logging.info("License activated successfully")
    return True, "license activated"

def validate_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as file:
            license_key = file.read().strip()
        status, msg = activate_license(license_key)
        if status:
            logging.info("License validation successful")
            return True
        else:
            logging.error("License validation failed: %s", msg)
            os.remove(LICENSE_FILE)  # Remove the license file if validation fails
    
    while True:
        license_key = prompt_license_key()
        status, msg = activate_license(license_key)
        if status:
            with open(LICENSE_FILE, 'w') as file:
                file.write(license_key)
            logging.info("License validation successful")
            return True
        else:
            logging.error("License validation failed: %s", msg)
            if "expired" in msg.lower():
                show_expiration_message()
                return False
            else:
                messagebox.showerror("License Validation Failed", msg)

def prompt_license_key():
    license_key = None

    def submit_license():
        nonlocal license_key
        license_key = entry.get()
        window.destroy()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    window = ctk.CTk()
    window.title("License Key")
    window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(), window.winfo_screenheight()))

    frame = ctk.CTkFrame(window)
    frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

    label = ctk.CTkLabel(frame, text="Enter your license key:", font=("Arial", 24))
    label.pack(pady=10)

    entry = ctk.CTkEntry(frame, width=300, font=("Arial", 18))
    entry.pack(pady=10)

    button = ctk.CTkButton(frame, text="Submit", command=submit_license, font=("Arial", 18))
    button.pack(pady=10)

    window.mainloop()

    return license_key

def show_expiration_message():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    window = ctk.CTk()
    window.title("License Expired")
    window.geometry("{0}x{1}+0+0".format(window.winfo_screenwidth(), window.winfo_screenheight()))

    frame = ctk.CTkFrame(window)
    frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

    label = ctk.CTkLabel(frame, text="License has expired. Please Renew.", font=("Arial", 36))
    label.pack(expand=True, fill=ctk.BOTH)

    window.mainloop()