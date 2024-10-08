### Markdown Documentation for the Script

---

# Type Stuff Fast!
#### Author: Craig S. Blackie, 2024

## Overview

**Type Stuff Fast!** is a command-line Python tool that automates typing data from a file (either binary or text) to a text editor. It can be used for tasks such as exfiltrating data via keystrokes or sending text-based payloads to systems where direct file transfer is not possible.

### Key Features

- Supports both text and binary files.
- Can split files into multiple parts for easier handling.
- Option to compress files into zip archives.
- Displays progress bar for typing completion.
- Includes hash verification to ensure file integrity.

### Requirements

- **Python 3.x**
- **pynput** module for controlling the keyboard.
- Other modules used (should be included in the Python Standard Library):
  - `argparse`, `base64`, `codecs`, `hashlib`, `os`, `time`, `zipfile`, `signal`, `sys`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/craigsblackie/tsf.git
   cd typestufffast
   ```
2. Install the `pynput` library:
   ```bash
   pip install pynput
   ```

### Usage

Run the script using the following command line arguments:

```bash
python typestufffast.py -i [FILE] [-d DELAY] [-s SPLIT] [-t] [-z]
```

### Arguments

- **`-i, --input FILE`**  
  Specifies the input file to be encoded and typed.  
  *Example*: `-i example.txt`

- **`-d, --delay int`**  
  Sets the delay in seconds before typing starts.  
  *Default*: `5` seconds  
  *Example*: `-d 10`

- **`-s, --split int`**  
  Number of parts to split the file into. If not provided, defaults to 1 (no splitting).  
  *Example*: `-s 3`

- **`-t, --text`**  
  Indicates that the input file is text and not binary. The file will not be base64 encoded before typing.  
  *Example*: `-t`

- **`-z, --zip`**  
  Compresses the input file into a zip archive before typing.  
  *Example*: `-z`

### Examples

1. **Typing a text file**:
   ```bash
   python typestufffast.py -i textfile.txt -d 5
   ```
   This command will read `textfile.txt` and type its content to the active window after a 5-second delay.

2. **Typing a binary file**:
   ```bash
   python typestufffast.py -i binaryfile.bin -d 10 -s 3 -z
   ```
   This command will compress `binaryfile.bin` into a zip archive, split it into 3 parts, and type it to the active window after a 10-second delay.

3. **Typing a text file with multiple parts**:
   ```bash
   python typestufffast.py -i long_text.txt -d 5 -s 4 -t
   ```
   This command will type `long_text.txt` as text (not binary), split into 4 parts.

### Example Output

```
example.txt  SHA256: abc123def456...
Typing will start in 5 seconds after enter is pressed, ensure a text editor on the remote host is the window in focus.
[PRESS ENTER]
Typing: |███████████████---------| 50.0% Complete [Remaining: 500]
```

### Handling Interrupts

If you need to stop the typing process, you can press `CTRL-C` to gracefully terminate the script. The script will clean up any temporary files created during the session.

### Contributions

Feel free to fork and submit pull requests for improvements or bug fixes.

### License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

--- 

This documentation outlines the script's purpose, usage, and options, making it easier to understand and implement for anyone using the tool.
