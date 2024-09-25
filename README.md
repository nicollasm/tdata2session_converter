
# TData to Telethon Session Converter

A Python application that converts Telegram Desktop `tdata` folders into Telethon session files. This tool is useful for migrating sessions from Telegram Desktop to Telethon-based applications without the need to log in again.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
  - [Examples](#examples)
- [How It Works](#how-it-works)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Features

- Converts single or multiple `tdata` folders into Telethon session files.
- Supports bulk processing of accounts.
- Handles errors gracefully with informative logging.
- Skips invalid or corrupted `tdata` folders to ensure continuous processing.

## Prerequisites

- **Python 3.7 or higher**
- **Telegram Desktop installed** (for obtaining `tdata` folders)
- The following Python packages:
  - `opentele`
  - `telethon`

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/tdata2session_converter.git
   cd tdata2session_converter
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix or MacOS:
   source .venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   If you don't have a `requirements.txt`, install the packages directly:

   ```bash
   pip install opentele telethon
   ```

## Usage

```bash
python main.py <directory> [--output <output_directory>]
```

- `<directory>`: The path to the directory containing one or multiple `tdata` folders.
- `--output`: (Optional) The directory where the Telethon session files will be saved. Defaults to `output`.

### Command-Line Arguments

- `directory`: Required. The directory containing `tdata` folders.
- `--output`: Optional. Specify a custom output directory.

### Examples

**Process a Single `tdata` Folder**

```bash
python main.py "/path/to/telegram/desktop/folder"
```

**Process Multiple `tdata` Folders**

```bash
python main.py "/path/to/directory/with/tdata_folders"
```

**Specify a Custom Output Directory**

```bash
python main.py "/path/to/tdata_folders" --output "/path/to/save/sessions"
```

## How It Works

1. **Directory Traversal**
   - The script checks if the provided directory is a single `tdata` folder or contains multiple `tdata` folders.
   - It processes only immediate subdirectories to avoid unwanted directories.

2. **Session Conversion**
   - For each valid `tdata` folder, it uses `opentele` to load the Telegram Desktop session.
   - Converts the session into a Telethon session file using the current session flag.

3. **Error Handling**
   - Skips folders that are invalid, incomplete, or already processed.
   - Provides informative logs for each step, including success and error messages.

## Error Handling

1. **Session File Already Exists**
   - If a session file with the same name already exists in the output directory, the script will skip processing that `tdata` folder.
   - **Solution**: Remove or rename the existing session file if you want to reprocess the `tdata` folder.

2. **No Accounts Loaded**
   - If a `tdata` folder does not contain any accounts, the script logs an error and moves on.
   - **Solution**: Verify the `tdata` folder contains all necessary files and is not corrupted.

3. **Missing or Corrupted Files**
   - The script handles exceptions where essential files like `key_data` are missing.
   - **Solution**: Ensure the `tdata` folders are complete and not corrupted.

4. **Two-Factor Authentication Enabled**
   - If the account has 2FA enabled, the script cannot convert the session.
   - **Solution**: Disable 2FA on the account before converting.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**

   Click the "Fork" button at the top right of the repository page to create a copy in your GitHub account.

2. **Create a New Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes**

   Implement your feature or fix the bug.

4. **Commit Your Changes**

   ```bash
   git commit -m 'Add some feature'
   ```

5. **Push to the Branch**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**

   Go to your forked repository on GitHub and click the "New Pull Request" button.

Please make sure your code adheres to the existing style conventions and passes all tests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
