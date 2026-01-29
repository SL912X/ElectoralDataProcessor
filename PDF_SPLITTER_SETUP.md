# PDF Splitter - Developer Setup Guide

## Overview
The PDF Splitter is a Python utility that automatically splits PDF files into two parts:
- **Part 1**: Contains pages 1, 2, and the last page
- **Part 2**: Contains pages 3 through the second-to-last page

The program supports both single-file and batch processing modes.

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 2 GB minimum (4 GB recommended)
- **Disk Space**: 500 MB minimum for installation and dependencies
- **Python Version**: Python 3.7 or higher

### Supported Platforms
- Windows 7 SP1 and later
- macOS 10.12 and later
- Linux (Ubuntu 14.04 LTS and later, or equivalent)

---

## Pre-Installation Setup

### 1. Verify Python Installation

Check if Python is already installed on your system:

**On Windows (PowerShell):**
```powershell
python --version
python -c "import sys; print(sys.executable)"
```

**On macOS/Linux (Terminal):**
```bash
python3 --version
which python3
```

**Expected Output:**
```
Python 3.7.0
(or higher version)
```

### 2. Install Python (if not already installed)

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"

**macOS:**
```bash
# Using Homebrew (install Homebrew first if needed)
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

## Installation Steps

### Step 1: Clone or Download the Project

```powershell
# Navigate to your desired directory
cd C:\Users\<YourUsername>\Downloads

# Clone the repository (if using Git)
git clone <repository-url>
cd electoral-roll-extractor-main
```

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment isolates project dependencies from system Python.

**On Windows (PowerShell):**
```powershell
# Navigate to project directory
cd C:\Users\<YourUsername>\Downloads\electoral-roll-extractor-main

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then activate again
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
# Navigate to project directory
cd ~/Downloads/electoral-roll-extractor-main

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Verify Virtual Environment is Active:**
You should see `(venv)` prefix in your terminal prompt:
```
(venv) C:\Users\divya\Downloads\electoral-roll-extractor-main>
```

### Step 3: Install Required Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed PyPDF2-3.x.x opencv-python-x.x.x ...
```

### Step 4: Verify Installation

```powershell
# Test PyPDF2 installation
python -c "from PyPDF2 import PdfReader, PdfWriter; print('PyPDF2 installed successfully!')"
```

---

## Project Structure

```
electoral-roll-extractor-main/
├── pdf_splitter.py                 # Main PDF splitter program
├── requirements.txt                # Python dependencies
├── PDF_SPLITTER_SETUP.md          # This setup guide
├── data/
│   ├── input/                     # Place input PDFs here
│   ├── output/                    # Output files generated here
│   ├── splitpdfs/                 # Input folder for batch processing
│   └── pdf2split/                 # Output folder for batch processing
└── venv/                          # Virtual environment (created in Step 2)
```

---

## Usage

### Mode 1: Single PDF File Processing

Process a single PDF file:

```powershell
python pdf_splitter.py <input_pdf_file> [output_directory]
```

**Examples:**

```powershell
# Default output to data/output2
python pdf_splitter.py "C:\Users\divya\Downloads\sample.pdf"

# Custom output directory
python pdf_splitter.py "C:\Users\divya\Downloads\sample.pdf" "C:\Users\divya\Downloads\output_folder"

# Using relative paths
python pdf_splitter.py data/input/document.pdf data/output
```

**Expected Output:**
```
Total pages in PDF: 150
✓ Created: C:\Users\divya\Downloads\output_folder\sample_part1.pdf
  Contains: Page 1, Page 2, Page 150
✓ Created: C:\Users\divya\Downloads\output_folder\sample_part2.pdf
  Contains: Pages 3 to 149

✓ PDF splitting completed successfully!
```

### Mode 2: Batch Processing (Multiple PDFs)

Process all PDF files in a folder:

```powershell
python pdf_splitter.py --batch <input_folder> <output_folder>
```

**Examples:**

```powershell
# Process all PDFs from input folder to output folder
python pdf_splitter.py --batch "C:\Users\divya\Downloads\pdfs_to_split" "C:\Users\divya\Downloads\split_output"

# Using relative paths
python pdf_splitter.py --batch data/splitpdfs data/pdf2split
```

**Expected Output:**
```
Found 5 PDF file(s) to process

[1/5] Processing: document1.pdf
Total pages in PDF: 200
✓ Created: C:\...\split_output\document1_part1.pdf
✓ Created: C:\...\split_output\document1_part2.pdf

[2/5] Processing: document2.pdf
...

============================================================
Processing Summary:
  Total files:     5
  Successful:      5
  Failed:          0
  Output folder:   C:\Users\divya\Downloads\split_output
============================================================
```

---

## Output Files

When a PDF is split, two files are generated:

| File | Content | Example |
|------|---------|---------|
| `{filename}_part1.pdf` | Pages 1, 2, and Last Page | `input_part1.pdf` |
| `{filename}_part2.pdf` | Pages 3 to (Last-1) | `input_part2.pdf` |

**Example with 150-page PDF:**
- `input_part1.pdf`: 3 pages (1, 2, 150)
- `input_part2.pdf`: 147 pages (3-149)

---

## Troubleshooting

### Issue 1: "Python is not recognized as an internal or external command"

**Solution:**
```powershell
# Check Python installation
python --version

# If not found, Python is not in PATH. Add it:
# 1. Control Panel → System → Advanced system settings
# 2. Click "Environment Variables"
# 3. Add Python installation directory to PATH
# 4. Restart terminal
```

### Issue 2: "No module named 'PyPDF2'"

**Solution:**
```powershell
# Ensure virtual environment is activated (you should see (venv) prefix)
# Then reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Or install PyPDF2 directly
pip install PyPDF2
```

### Issue 3: "Input file not found"

**Solution:**
```powershell
# Use absolute paths or verify relative path is correct
# Check if file exists
Test-Path "C:\path\to\file.pdf"

# For batch mode, check folder contents
Get-ChildItem "C:\path\to\input_folder" -Filter "*.pdf"
```

### Issue 4: "PDF must have at least 3 pages"

**Cause:** Input PDF has fewer than 3 pages
- Part 1 requires pages 1, 2, and last page
- Minimum 3 pages needed

**Solution:** Use a PDF with at least 3 pages

### Issue 5: Virtual Environment Activation Error (Windows)

**Error:** "cannot be loaded because running scripts is disabled"

**Solution:**
```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Issue 6: Permission Denied Error

**Cause:** Insufficient file permissions or folder is read-only

**Solution:**
```powershell
# Check folder permissions
Get-Acl "C:\path\to\output_folder"

# For batch processing, ensure output folder is writable
# Run PowerShell as Administrator if needed
```

---

## Development Setup (Optional)

### Install Development Tools

For code formatting and linting:

```powershell
pip install pylint black
```

### Run Code Quality Checks

```powershell
# Format code
black pdf_splitter.py

# Check code quality
pylint pdf_splitter.py
```

---

## Deactivating Virtual Environment

When you're done working:

```powershell
# On Windows
deactivate

# On macOS/Linux
deactivate
```

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Activate virtual environment (Windows) | `.\venv\Scripts\Activate.ps1` |
| Activate virtual environment (Mac/Linux) | `source venv/bin/activate` |
| Deactivate virtual environment | `deactivate` |
| Install dependencies | `pip install -r requirements.txt` |
| Process single file | `python pdf_splitter.py input.pdf` |
| Batch process folder | `python pdf_splitter.py --batch input_folder output_folder` |
| Check Python version | `python --version` |
| Upgrade pip | `python -m pip install --upgrade pip` |

---

## System Information

For support or troubleshooting, collect the following information:

```powershell
# Check Python version and path
python --version
python -c "import sys; print(sys.executable)"

# Check PyPDF2 version
pip show PyPDF2

# Check OS information
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```

---

## Support and Documentation

- **PyPDF2 Documentation**: https://pypdf2.readthedocs.io/
- **Python Official Guide**: https://python.org/
- **Virtual Environments**: https://docs.python.org/3/tutorial/venv.html

---

## Checklist for New Developers

- [ ] Python 3.7+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed from requirements.txt
- [ ] PyPDF2 installation verified
- [ ] Sample PDF processed successfully
- [ ] Batch mode tested with multiple PDFs
- [ ] Output files verified in output folder

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-01-25 | Initial release with single and batch processing modes |

---

**Last Updated**: January 25, 2026

For issues or questions, please contact the development team or check the project repository.
