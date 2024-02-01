import tkinter as tk
from tkinter import ttk, messagebox
import requests
import zipfile
import os
import io
import re
import shutil

# Replace these variables with your GitHub repository information
repo_owner = 'Wise-Ass'
repo_name = 'start-journey'
current_version = 'v1.0.2'

def update_application():
    global current_version
    global window

    releases_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases'

    try:
        response = requests.get(releases_url)

        if response.status_code == 200:
            releases = response.json()

            if releases:
                latest_release = releases[0]
                latest_version = latest_release.get('tag_name').lstrip('v')

                download_url = latest_release.get('zipball_url')

                if latest_version and download_url:
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

                            # Display an error message to the user
                            messagebox.showerror("Update Error", "Failed to check for updates. Please try again later.")
                            return

                        finally:
                            # Clean up
                            os.remove('latest_version.zip')
                            try:
                                shutil.rmtree(temp_folder)
                            except Exception as e:
                                print(f"Error removing temporary folder: {e}")

                        update_success = True
                        if update_success:
                            print("Update applied successfully! Please restart the application.")
                            status_var.set("Update applied successfully! Please restart the application.")
                            # Update current_version to the latest version
                            current_version = latest_version
                        else:
                            print("Failed to apply the update.")
                            status_var.set("Failed to apply the update.")
                            # You may choose to continue with the application even if the update fails

                        # Remove the status bar label after completion
                        status_label.destroy()

    except Exception as e:
        print(f"Error checking for updates: {e}")

def main():
    global window
    #global current_version  # Add this line to declare current_version as a global variable

    # Create the main window
    window = tk.Tk()
    window.geometry("300x150")
    window.title("Green GUI")
    window.configure(bg="blue")

    update_application()

    # Run the GUI
    print("Running the GUI...")
    window.mainloop()

if __name__ == "__main__":
    main()
