import tkinter as tk
from tkinter import ttk, messagebox
import requests
import zipfile
import os
import io
import shutil

# Replace these variables with your GitHub repository information
repo_owner = 'Wise-Ass'
repo_name = 'start-journey'
current_version = 'v1.0'

window = None  # Declare window as a global variable

def check_for_updates(current_version):
    releases_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases'

    try:
        response = requests.get(releases_url)

        if response.status_code == 200:
            releases = response.json()

            if releases:
                latest_release = releases[0]
                latest_version = latest_release.get('tag_name')
                download_url = latest_release.get('zipball_url')

                if latest_version and download_url:
                    return latest_version, download_url
                else:
                    print(f"Failed to get the latest version and download URL. Latest Version: {latest_version}, Download URL: {download_url}")
                    return None, None

        print(f"Failed to get the latest version and download URL. API response: {response.text}")
        return None, None

    except Exception as e:
        print(f"Error checking for updates: {e}")
        return None, None


def download_and_apply_update(download_url, progress_callback=None):
    try:
        # Download the latest version zip file
        response = requests.get(download_url, stream=True)

        # Create a temporary zip file
        with open('latest_version.zip', 'wb') as zip_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    zip_file.write(chunk)

        # Extract the contents to the specified path
        with zipfile.ZipFile('latest_version.zip', 'r') as zip_ref:
            # Extract all contents into a temporary folder
            temp_folder = 'temp_update_folder'
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)

            zip_ref.extractall(temp_folder)

            # Check if a .py file is present
            py_file = f"{repo_name}.py"
            # Function to recursively search for the .py file
            def search_py_file(directory):
                for root, dirs, files in os.walk(directory):
                    if py_file in files:
                        return os.path.join(root, py_file)
                return None

            # Search for the .py file in the extracted contents
            py_file_path = search_py_file(temp_folder)

            if py_file_path:
                print(f".py file found in the update at: {py_file_path}. Proceeding with the update...")
            else:
                print(f"No .py file found in the update. Skipping the update.")
            
        # Clean up
        os.remove('latest_version.zip')
        try:
            shutil.rmtree(temp_folder)
        except Exception as e:
            print(f"Error removing temporary folder: {e}")

        return True
    except Exception as e:
        error_message = f"Error checking for updates: {e}"
        print(error_message)

        # Log the error to a file for better troubleshooting
        with open('update_error_log.txt', 'a') as log_file:
            log_file.write(error_message + '\n')

        # Print the API response for further investigation
        if response.status_code != 200:
            print(f"API request failed with status code: {response.status_code}")
            print(f"API response: {response.text}")

        return False


def on_close():
    window.destroy()

def main():
    global window

    # Create the main window
    window = tk.Tk()
    window.geometry("300x150")
    window.title("Green GUI")
    window.configure(bg="red")

    print("Checking for updates...")
    latest_version, download_url = check_for_updates(current_version)
    print(f"Latest Version: {latest_version}")
    print(f"Download URL: {download_url}")

    response = messagebox.askyesno("Update Check", f"Check for updates?\n\nLatest Version: {latest_version}\nCurrent Version: {current_version}")

    if response and latest_version:
        if download_url is None:
            print("No download URL available. Skipping update.")
            window.mainloop()  # Make sure to call mainloop even if there's no update
            return

        response = messagebox.askyesno("Update Available", f"A new version ({latest_version}) is available. Do you want to download and install it?")

        if response:
            print("Downloading and applying update...")
            # Create a status bar label
            status_var = tk.StringVar()
            status_label = ttk.Label(window, textvariable=status_var, background='green', font=('Arial', 10))
            status_label.pack(pady=10)

            # Function to update the status bar
            def update_status_bar(current_size, total_size):
                percent = (current_size / total_size) * 100
                status_var.set(f"Downloading... {percent:.2f}%")
                window.update_idletasks()

            update_success = download_and_apply_update(download_url, progress_callback=update_status_bar)

            if update_success:
                print("Update applied successfully! Please restart the application.")
                status_var.set("Update applied successfully! Please restart the application.")
            else:
                print("Failed to apply the update.")
                status_var.set("Failed to apply the update.")
                # You may choose to continue with the application even if the update fails

            # Remove the status bar label after completion
            status_label.destroy()

    # Run the GUI
    print("Running the GUI...")
    window.mainloop()

if __name__ == "__main__":
    main()

