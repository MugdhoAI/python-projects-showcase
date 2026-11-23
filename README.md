# Python Utility Projects Showcase

This repository contains two working Python utility projects, plus documentation and a video demo for them.

## Project Demo and Overview

### Full Documentation

[Download or view the project PDF guide](./The_Python_Engineering_Schematic.pdf)

Video demo: [The Design Patterns of Pro Python Projects](./The_Design_Patterns_of_Pro_Python_Projects.mp4)

## Projects

### 1. WiFi QR Code Generator

`wifi_qr_generator.py` builds a scannable WiFi QR payload in the ZXing `WIFI:` format, with correct escaping of special characters in the network name and password, validation of the security type and password rules, and an optional PNG export. SSIDs are limited to 32 octets, and WEP keys must be 5 or 13 ASCII characters, or 10 or 26 hex digits.

```bash
python wifi_qr_generator.py HomeNet secret123
# WIFI:T:WPA;S:HomeNet;P:secret123;H:false;;

python wifi_qr_generator.py HomeNet secret123 --output wifi.png   # needs: pip install qrcode
python wifi_qr_generator.py Cafe --security nopass
```

### 2. File Organizer

`file_organizer.py` cleans up a cluttered directory by sorting its files into category folders (Images, Documents, Audio, Video, Archives, Code, Other). It never overwrites an existing file, leaves subdirectories alone, and supports a dry run preview. With `--recursive` it organizes files in subfolders too, moving them up into the top level category folders while leaving files that are already organized where they are. After a run it prints a per-category summary.

```bash
python file_organizer.py ~/Downloads --dry-run   # preview the moves
python file_organizer.py ~/Downloads             # do the sorting
python file_organizer.py ~/Downloads --recursive # include subfolders
```

## Tests

Both projects are covered by pytest tests in `tests/`:

```bash
pip install pytest
python -m pytest tests/ -q
```
