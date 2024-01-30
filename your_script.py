import tkinter as tk
from tkinter import messagebox
import requests
import zipfile
import os
import subprocess
import sys

# Replace these variables with your GitHub repository information
repo_owner = 'Wise-Ass'
repo_name = 'start-journey'
current_version = 'v1.0'

window = None  # Declare window as a global variable

def check_for_updates(current_version):
    releases_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest'

    try:
        response = requests.get(releases_url)
        latest_version = response.json()['tag_name']
        download_url = response.json()['assets'][0]['browser_download_url']  # Assuming there's one asset per release

        if latest_version != current_version:
            return latest_version, download_url
        else:
            return None, None
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return None, None

def download_and_apply_update(download_url):
    try:
        # Download the latest version zip file
        response = requests.get(download_url)
        with open('latest_version.zip', 'wb') as zip_file:
            zip_file.write(response.content)

        # Extract the contents to the specified path
        with zipfile.ZipFile('latest_version.zip', 'r') as zip_ref:
            zip_ref.extractall('.')

        # Clean up
        os.remove('latest_version.zip')

        return True
    except Exception as e:
        print(f"Error updating: {e}")
        return False

def on_close():
    # Check for updates when closing the application
    latest_version, download_url = check_for_updates(current_version)
    
    if latest_version:
        # Prompt the user to download and install the update
        response = messagebox.askyesno("Update Available", f"A new version ({latest_version}) is available. Do you want to download and install it?")
        
        if response:
            update_success = download_and_apply_update(download_url)

            if update_success:
                messagebox.showinfo("Update Success", "Update applied successfully! Please restart the application.")
            else:
                messagebox.showerror("Update Failed", "Failed to apply the update.")
        
    window.destroy()

def main():
    global window  # Declare window as a global variable

    # Create the main window
    window = tk.Tk()

    # Set window size
    window.geometry("200x200")

    # Set window title
    window.title("Green GUI")

    # Set background color to green
    window.configure(bg="green")

    # Run the GUI
    window.protocol("WM_DELETE_WINDOW", on_close)  # Bind the close event to on_close function
    window.mainloop()

if __name__ == "__main__":
    main()
