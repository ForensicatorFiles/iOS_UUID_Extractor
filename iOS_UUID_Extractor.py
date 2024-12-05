### Version 1.0

import customtkinter as ctk
from tkinter import filedialog
import zipfile
import plistlib
import json
import os

# Custom 90s Retro Theme
ctk.set_appearance_mode("dark")  # Default: Follows system settings
ctk.set_default_color_theme("90s_retro_theme.json")  # 90's Theme color
# ctk.set_default_color_theme("blue")  # Theme color

# Function to extract metadata identifier
def get_metadata_identifier(plist_data):
    try:
        plist = plistlib.loads(plist_data)
        return plist.get('MCMMetadataIdentifier')
    except Exception as e:
        print(f"Error reading plist data: {e}")
        return None

# Function to find UUIDs and App IDs
def find_uuids_and_app_id(zip_ref, base_path):
    """
    Look for UUIDs and associated app identifiers in the specified base path.
    """
    app_data = {}

    for file_name in zip_ref.namelist():
        if base_path in file_name and file_name.endswith('.com.apple.mobile_container_manager.metadata.plist'):
            try:
                # Extract folder name
                folder_name = file_name.split('/')[-2]
                # Check if folder name looks like a UUID
                if len(folder_name) == 36 and folder_name.count("-") == 4:
                    # Read the metadata plist file
                    with zip_ref.open(file_name) as plist_file:
                        plist_data = plist_file.read()
                        app_id = get_metadata_identifier(plist_data)
                        if app_id and app_id.startswith("group"):
                            app_id = app_id[6:]  # Remove "group" prefix
                        if app_id:
                            # Collect data for this app_id
                            if app_id not in app_data:
                                app_data[app_id] = {
                                    'data_uuid': [],
                                    'data_filepath': [],
                                    'app_group_uuid': [],
                                    'app_group_filepath': []
                                }
                            # Categorize UUID based on path type
                            if 'Data/Application' in file_name:
                                app_data[app_id]['data_filepath'].append(file_name)
                                app_data[app_id]['data_uuid'].append(folder_name)
                            elif 'Shared/AppGroup' in file_name:
                                app_data[app_id]['app_group_filepath'].append(file_name)
                                app_data[app_id]['app_group_uuid'].append(folder_name)
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

    return app_data

# Combine data sources
def list_apps_and_uuids(zip_path):
    """
    List all iOS applications and their GUIDs and UUIDs from the iOS filesystem zip file.
    """
    combined_app_data = {}

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Process Data/Application
        data_app_data = find_uuids_and_app_id(zip_ref, 'private/var/mobile/Containers/Data/Application')
        # Process Shared/AppGroup
        app_group_data = find_uuids_and_app_id(zip_ref, 'private/var/mobile/Containers/Shared/AppGroup')

        # Combine both data sources
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

# GUI Application
def select_file():
    file_path = filedialog.askopenfilename(title="Select a ZIP File", filetypes=[("ZIP files", "*.zip")])
    if file_path:
        process_file(file_path)

def process_file(file_path):
    try:
        app_data = list_apps_and_uuids(file_path)
        response_text = json.dumps(app_data, indent=4)
        response_textbox.delete("1.0", ctk.END)
        response_textbox.insert(ctk.END, response_text)
        global current_response, filtered_response
        current_response = app_data
        filtered_response = None
    except Exception as e:
        response_textbox.delete("1.0", ctk.END)
        response_textbox.insert(ctk.END, f"Error processing file: {e}")

def save_results():
    output_data = filtered_response if filtered_response else current_response
    if output_data:
        output_path = filedialog.asksaveasfilename(title="Save JSON File", defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if output_path:
            with open(output_path, 'w') as output_file:
                json.dump(output_data, output_file, indent=4)
            response_textbox.insert(ctk.END, f"\nResults saved to {output_path}")
            clear_filter()

def filter_results():
    keyword = filter_entry.get()
    if keyword and current_response:
        global filtered_response
        filtered_response = {k: v for k, v in current_response.items() if keyword.lower() in k.lower()}
        response_textbox.delete("1.0", ctk.END)
        response_textbox.insert(ctk.END, json.dumps(filtered_response, indent=4))

def clear_filter():
    global filtered_response
    filtered_response = None
    if current_response:
        response_textbox.delete("1.0", ctk.END)
        response_textbox.insert(ctk.END, json.dumps(current_response, indent=4))
        filter_entry.delete(0, ctk.END)

# Main Window Setup
current_response = None
filtered_response = None
app = ctk.CTk()
app.title("iOS UUID Extractor v.1.0")
app.geometry("1000x600")

# File Selection
file_button = ctk.CTkButton(app, text="Select File", command=select_file)
file_button.pack(pady=10)

# Filter Area
filter_frame = ctk.CTkFrame(app)
filter_frame.pack(fill="x", padx=10, pady=5)
ctk.CTkLabel(filter_frame, text="Filter Keyword:").pack(side="left", padx=5)
filter_entry = ctk.CTkEntry(filter_frame)
filter_entry.pack(side="left", fill="x", expand=True, padx=5)
filter_button = ctk.CTkButton(filter_frame, text="Filter", command=filter_results)
filter_button.pack(side="right", padx=5)

# Results Display
response_textbox = ctk.CTkTextbox(app, wrap="word")
response_textbox.pack(fill="both", expand=True, padx=10, pady=10)

# Save and Clear Filter Buttons
button_frame = ctk.CTkFrame(app)
button_frame.pack(fill="x", padx=10, pady=5)
save_button = ctk.CTkButton(button_frame, text="Save Results", command=save_results)
save_button.pack(side="left", padx=5)
clear_filter_button = ctk.CTkButton(button_frame, text="Clear Filter", command=clear_filter)
clear_filter_button.pack(side="right", padx=5)

# Run the App
app.mainloop()
