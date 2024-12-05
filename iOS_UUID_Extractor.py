### Version 1.0

import customtkinter as ctk
from tkinter import filedialog
import zipfile
import plistlib
import json
import os

# Set up the appearance mode and theme
ctk.set_appearance_mode("dark")  # Dark mode appearance
ctk.set_default_color_theme("90s_retro_theme.json")  # Custom theme
# ctk.set_default_color_theme("blue")  # Additional Theme color

# Function to extract metadata identifier from plist data
def get_metadata_identifier(plist_data):
    """Extract the 'MCMMetadataIdentifier' key from the plist data."""
    try:
        plist = plistlib.loads(plist_data)
        return plist.get('MCMMetadataIdentifier')
    except Exception as e:
        print(f"Error reading plist data: {e}")
        return None

# Function to process files within a base path and find UUIDs and app IDs
def find_uuids_and_app_id(zip_ref, base_path):
    """
    Look for UUIDs and associated app identifiers in the specified base path.

    :param zip_ref: Opened ZipFile reference
    :param base_path: Base directory path to search in the ZIP
    :return: Dictionary of app data
    """
    app_data = {}

    for file_name in zip_ref.namelist():
        if base_path in file_name and file_name.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            try:
                # Extract folder name from the path
                folder_name = file_name.split('/')[-2]

                # Check if the folder name is a valid UUID
                if len(folder_name) == 36 and folder_name.count("-") == 4:
                    # Read the metadata plist file
                    with zip_ref.open(file_name) as plist_file:
                        plist_data = plist_file.read()
                        app_id = get_metadata_identifier(plist_data)

                        # Strip "group" prefix if present
                        if app_id and app_id.startswith("group"):
                            app_id = app_id[6:]

                        if app_id:
                            # Initialize the app entry if not already present
                            if app_id not in app_data:
                                app_data[app_id] = {
                                    'data_uuid': [],
                                    'data_filepath': [],
                                    'app_group_uuid': [],
                                    'app_group_filepath': []
                                }

                            # Categorize UUID based on the file path type
                            if 'Data/Application' in file_name:
                                app_data[app_id]['data_filepath'].append(file_name)
                                app_data[app_id]['data_uuid'].append(folder_name)
                            elif 'Shared/AppGroup' in file_name:
                                app_data[app_id]['app_group_filepath'].append(file_name)
                                app_data[app_id]['app_group_uuid'].append(folder_name)
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

    return app_data

# Function to extract app data from both application and app group directories
def list_apps_and_uuids(zip_path):
    """
    Extract all iOS applications and their GUIDs and UUIDs from the iOS filesystem ZIP file.

    :param zip_path: Path to the ZIP file
    :return: Combined app data from both application and app group directories
    """
    combined_app_data = {}

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract data from both directories
        data_app_data = find_uuids_and_app_id(zip_ref, 'private/var/mobile/Containers/Data/Application')
        app_group_data = find_uuids_and_app_id(zip_ref, 'private/var/mobile/Containers/Shared/AppGroup')

        # Merge the results
        for app_id, data in data_app_data.items():
            if app_id not in combined_app_data:
                combined_app_data[app_id] = data
            else:
                combined_app_data[app_id]['data_uuid'].extend(data['data_uuid'])
                combined_app_data[app_id]['data_filepath'].extend(data['data_filepath'])

        for app_id, data in app_group_data.items():
            if app_id not in combined_app_data:
                combined_app_data[app_id] = data
            else:
                combined_app_data[app_id]['app_group_uuid'].extend(data['app_group_uuid'])
                combined_app_data[app_id]['app_group_filepath'].extend(data['app_group_filepath'])

    return combined_app_data

# Function to handle file selection from the GUI
def select_file():
    """Open a file dialog to select a ZIP file and process it."""
    file_path = filedialog.askopenfilename(title="Select a ZIP File", filetypes=[("ZIP files", "*.zip")])
    if file_path:
        process_file(file_path)

# Function to process the selected ZIP file
def process_file(file_path):
    """Process the selected ZIP file and display the extracted data."""
    try:
        app_data = list_apps_and_uuids(file_path)
        response_text = json.dumps(app_data, indent=4)
        response_textbox.delete("1.0", ctk.END)
        response_textbox.insert(ctk.END, response_text)

        # Store the current and filtered response globally
        global current_response, filtered_response
        current_response = app_data
        filtered_response = None
    except Exception as e:
        response_textbox.delete("1.0", ctk.END)
        response_textbox.insert(ctk.END, f"Error processing file: {e}")

# Function to save results to a JSON file
def save_results():
    """Save the filtered or full results to a JSON file."""
    output_data = filtered_response if filtered_response else current_response
    if output_data:
        output_path = filedialog.asksaveasfilename(title="Save JSON File", defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if output_path:
            with open(output_path, 'w') as output_file:
                json.dump(output_data, output_file, indent=4)
            response_textbox.insert(ctk.END, f"\nResults saved to {output_path}")
            clear_filter()

# Function to filter results based on a keyword
def filter_results():
    """Filter the results by the provided keyword."""
    keyword = filter_entry.get()
    if keyword and current_response:
        global filtered_response
        filtered_response = {k: v for k, v in current_response.items() if keyword.lower() in k.lower()}
        response_textbox.delete("1.0", ctk.END)
        response_textbox.insert(ctk.END, json.dumps(filtered_response, indent=4))

# Function to clear the filter and reset the results
def clear_filter():
    """Clear the filter and restore the original results."""
    global filtered_response
    filtered_response = None
    if current_response:
        response_textbox.delete("1.0", ctk.END)
        response_textbox.insert(ctk.END, json.dumps(current_response, indent=4))
        filter_entry.delete(0, ctk.END)

# Main GUI setup
app = ctk.CTk()
app.title("iOS UUID Extractor")
app.geometry("1000x600")

# File selection button
file_button = ctk.CTkButton(app, text="Select File", command=select_file)
file_button.pack(pady=10)

# Filter area
filter_frame = ctk.CTkFrame(app)
filter_frame.pack(fill="x", padx=10, pady=5)
ctk.CTkLabel(filter_frame, text="Filter Keyword:").pack(side="left", padx=5)
filter_entry = ctk.CTkEntry(filter_frame)
filter_entry.pack(side="left", fill="x", expand=True, padx=5)
filter_button = ctk.CTkButton(filter_frame, text="Filter", command=filter_results)
filter_button.pack(side="right", padx=5)

# Results display
response_textbox = ctk.CTkTextbox(app, wrap="word")
response_textbox.pack(fill="both", expand=True, padx=10, pady=10)

# Save and clear filter buttons
button_frame = ctk.CTkFrame(app)
button_frame.pack(fill="x", padx=10, pady=5)
save_button = ctk.CTkButton(button_frame, text="Save Results", command=save_results)
save_button.pack(side="left", padx=5)
clear_filter_button = ctk.CTkButton(button_frame, text="Clear Filter", command=clear_filter)
clear_filter_button.pack(side="right", padx=5)

# Run the application
app.mainloop()
