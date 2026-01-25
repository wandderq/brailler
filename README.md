# Brailler — Braille Art Generator

**Brailler** is a command-line utility written in Python that converts any image into artistic text-based representations using Braille Unicode characters instead of traditional ASCII symbols.

Each Braille character contains up to 8 dots, allowing for a higher "resolution" compared to standard ASCII art. This makes Brailler ideal for creating detailed and accessible text-based graphics directly in your terminal or in a file.

---

## Features

- Converts PNG/JPG images into Braille-based art
- Adjustable output size (width × height)
- Configurable binarization threshold for better contrast
- Option to print the result directly to the console
- Save output to a text file
- Verbose mode for processing details

---

## Installation

### From GitHub (using pip/pipx)
```bash
pipx install git+https://github.com/wandderq/brailer@main
```

### From source
```bash
git clone https://github.com/wandderq/brailer
cd brailer
pip install .
```

## Usage

### Basic example
```bash
brailler image.png --print
```

### Specify output size
```bash
brailler image.png --size 256x256 --print
```

### Save to a file
```bash
# derived from input filename
brailler image.png --output '[input]' # image.png.txt

# another name
brailler image.png --output art.txt
```

### Adjust binarization threshold
```bash
brailler image.png --threshold 200 --print
```

## Command-line arguments
| Argument          | Description                                                                             |
|-------------------|-----------------------------------------------------------------------------------------|
| `input`           | Input image file (PNG/JPG)                                                              |
| `-o, --output`    | Output text file (default: None) (can be derived from input filename using `'[input]'`) |
| `-s, --size`      | Output dimensions in WIDTHxHEIGHT format (default: 128x64)                              |
| `-t, --threshold` | Binarization threshold (0-255) (default: 160)                                           |
| `-p, --print`     | Print the result to the console                                                         |
| `-v, --verbose`   | Show detailed processing information                                                    |

## Requirements
- Python 3.7+
- Pillow
- numpy

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details

