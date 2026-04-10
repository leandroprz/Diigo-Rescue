# Diigo Rescue - Convert Diigo HTML bookmarks to CSV

Rescue your Diigo bookmarks and convert them to CSV format when their [export tool](https://www.diigo.com/tools/export) fails.

This way you'll be able to import your bookmarks into any other platform and migrate them, for example Raindrop.

[![Latest version](https://img.shields.io/github/v/release/leandroprz/Diigo-Rescue?color=998f68&label=Latest%20version&style=for-the-badge)](https://github.com/leandroprz/Diigo-Rescue/releases/latest) ![Platform](https://img.shields.io/badge/Platform-Windows%20,%20macOS%20&amp;%20Linux-787878?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-v3.6+-687d99?style=for-the-badge) ![License](https://img.shields.io/badge/License-MIT-628a6f?style=for-the-badge)

## Features

- Extracts bookmarks from Diigo HTML manual exports
- Converts to clean CSV format (url, title, note, tags, date created)
- Detects and handles duplicate URLs
- Automatically splits large files (10MB chunks)
- Validates exported data
- Cross-platform (Windows, macOS, Linux)

## Getting your bookmarks from Diigo

Since [Diigo's export tool](https://www.diigo.com/tools/export) may not be working properly, you'll need to manually save your bookmark pages as HTML files first:

1. **Install SingleFile** browser extension: [https://www.getsinglefile.com/#download](https://www.getsinglefile.com/#download)
   - Available for Chrome, Firefox, Edge, and Safari
   - Saves complete web pages as a single HTML file including all its resources

2. **Save each Diigo bookmark page**:
   - Go to your Diigo library (diigo.com/user/yourusername)
   - Navigate through your bookmark pages (pagination is at the bottom)
   - Wait until each page is fully loaded, then use SingleFile to save each page (click on the extension icon, then "Save page with SingleFile")
   - Save all HTML files to a single folder

Once you have all the HTML files in a folder, you're ready to use this converter.

## Requirements

- Python 3.6 or higher
- BeautifulSoup4 Python module

## Installation

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/)

2. Clone or download this repository

3. Open Command Prompt or PowerShell and navigate to the folder:
```cmd
cd C:\path\to\diigo-rescue
```

4. Install dependencies:
```cmd
pip install -r requirements.txt
```

### macOS

1. Python 3 is usually pre-installed. Check by opening Terminal and running:
```bash
python3 --version
```

2. Clone or download this repository

3. Navigate to the folder:
```bash
cd /path/to/diigo-rescue
```

4. Install dependencies:
```bash
pip3 install -r requirements.txt
```

### Linux

1. Install Python 3 and pip (if not already installed):
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

2. Clone or download this repository

3. Navigate to the folder:
```bash
cd /path/to/diigo-rescue
```

4. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

### Windows (Command Prompt)
```cmd
python diigo_rescue.py C:\path\to\your\saved\html\bookmarks
```

### Windows (PowerShell)
```powershell
python diigo_rescue.py C:\path\to\your\saved\html\bookmarks
```

### macOS
```bash
python3 diigo_rescue.py /path/to/your/saved/bookmarks
```

### Linux
```bash
python3 diigo_rescue.py /path/to/your/saved/bookmarks
```

## How it works

The script will:
1. Find all HTML files in the specified folder
2. Extract bookmark data from each file
3. Check for duplicate URLs and ask if you want to remove them
4. Create CSV files in a `CSV_Export/` subfolder
5. Validate the exported data
6. Show a detailed summary of results

## CSV output format

- **Comma-delimited**
- **Columns**: `url`, `title`, `note`, `tags`, `created`
- **tags** are combined as "tag1, tag2" when multiple
- **created** timestamp is in Unix format

## Example

**Input folder structure:**
```
my_bookmarks/
├── page1.html
├── page2.html
└── page3.html
```

**After running:**
```
my_bookmarks/
├── page1.html
├── page2.html
├── page3.html
└── CSV_Export/
    ├── bookmarks_01.csv
    └── bookmarks_02.csv
```

## License

MIT License - See LICENSE file for details
