# iOS UUID Extractor

## Overview
The **iOS UUID Extractor** is a GUI-based Python application built with `customtkinter` that allows users to extract UUIDs and metadata identifiers from iOS filesystem ZIP files. This tool is tailored for analyzing app data and app group UUIDs from iOS backups or filesystem images. It offers a clean, modern user interface with options to filter results and export them to a JSON file.

---

## Features
- **File Selection:** Easily select ZIP files containing iOS filesystem data.
- **Results Display:** View extracted UUIDs and metadata in a scrollable text area.
- **Filtering:** Filter results by a keyword for focused analysis.
- **Export Results:** Save the extracted or filtered results as a JSON file.
- **Clear Filter:** Reset the filter to redisplay the complete results.
- **Custom Theme:** Uses a "90s Retro" custom theme for a unique visual style.

---

## Installation

### Prerequisites
- Python 3.7+
- Required Python libraries:
  - `customtkinter`
  - `tkinter` (usually bundled with Python)
  - Standard Python libraries: `zipfile`, `plistlib`, `json`, `os`

### Setup
1. Clone or download the repository.
2. Install the dependencies:
   ```bash
   pip install customtkinter
3. Run the application:
   ``` python
   python ios_uuid_extractor.py
   ```

---

## Usage

### Steps
1. **Select a File:**
    - Click the `Select File` button to choose a ZIP file containing the iOS filesystem.
2. **View Results:**
    - The extracted UUIDs and metadata identifiers will appear in the text area.
3. **Filter Results:**
    - Enter a keyword in the filter field and click `Filter` to narrow down the results.
4. **Export Results:**
    - Click `Save Results` to export the filtered or full results to a JSON file.
5. **Clear Filter:**
    - Click `Clear Filter` to reset the filter and redisplay the full results.

### Example Workflow
- Open a ZIP file containing iOS filesystem data.
- Filter results using keywords like `com.google` or `facebook`.
- Save the filtered results as `filtered_results.json`.
- Clear the filter to start a new analysis.

---

### Custom Theme
The application uses a 90s_retro_theme_full.json custom theme for customtkinter. Replace this theme file or modify it for a personalized look.

To switch to another theme:
- Replace the theme file path in the code:
``` python
ctk.set_default_color_theme("blue")
```

---

### Project Structure
- `ios_uuid_extractor.py`: Main application file.
- `90s_retro_theme_full.json`: Custom theme file.

---

Limitations
- Only processes ZIP files with specific iOS directory structures:
  - `private/var/mobile/Containers/Data/Application`
  - `private/var/mobile/Containers/Shared/AppGroup`
- The file selection is manual (drag-and-drop is not supported).

---

### Contributing
Contributions are welcome! Feel free to submit a pull request or report issues.

---

### License
This project is licensed under the MIT License.

---

### Screenshots
After selecting the file:
![image](https://github.com/user-attachments/assets/f3fb5a1d-e176-4941-a38a-6dd5bd59fcf0)

Filtering for "musically" aka TikTok:
![image](https://github.com/user-attachments/assets/13a83127-24d2-4591-9681-7e2107d7b60d)

Filtering for "life360":
![image](https://github.com/user-attachments/assets/400f9a51-d5e5-4efd-9d76-a1ed84de234c)



---

Enjoy using the iOS UUID Extractor! 🚀
