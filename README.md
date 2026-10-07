# AGH Timetable Converter

## Project Overview

AGH Timetable Converter is a Python command-line application that automates the extraction, cleaning, transformation, and export of university timetable data from **USOS** and **UniTime**.

The tool converts timetable exports containing recurring date ranges and semi-structured scheduling fields into accessible, integration-ready **CSV** and **XLSX** files. Its output is designed for practical use with calendar applications, Notion databases, Excel, and other productivity tools.

## The Problem Solved

University timetable systems commonly export classes in formats that are difficult to reuse. In particular, UniTime represents recurring classes as date ranges and weekday patterns rather than individual calendar events, while USOS exports may use different column names, delimiters, and data conventions.

This application automates that conversion process by:

- Expanding recurring timetable ranges into one row per class occurrence.
- Supporting timetable imports from both **UniTime** and **USOS**.
- Cleaning inconsistent text, room names, course titles, and activity types.
- Converting date and time fields into standard or integrated calendar-friendly formats.
- Filtering courses and activity types interactively.
- Exporting structured results to CSV, XLSX, or both formats.
- Preventing accidental overwriting of existing output files.

The result is a more accessible timetable that can be imported into Notion, spreadsheets, calendars, and other systems that require one record per scheduled event.

## Tech Stack

- **Language:** Python 3.x
- **Runtime:** Command-line interface
- **Primary data-processing library:** `pandas`
- **File and data handling:** `csv`, `json`, `os`, `datetime`, `re`, `io`
- **Spreadsheet export:** `openpyxl` through `pandas.DataFrame.to_excel()`
- **Application packaging:** PyInstaller
- **Supported output formats:** CSV and XLSX

## Technical Highlights

- **Robust Data Parsing:** Utilizes `pandas` and `StringIO` with dynamic delimiter detection and fallback encoding to reliably ingest messy, semi-structured CSV exports from USOS and UniTime.
- **Complex Time Transformations:** Expands single-row recurring date ranges (e.g., a semester-long class) into individual, calendar-ready events using `datetime` calculations and regular expressions.
- **Automated Data Cleaning:** Normalizes university data by removing duplicates, standardizing room names, and mapping activity types (like W, CWA, CWP) to consistent codes for downstream use.
- **Interactive CLI & State Management:** Features a modular command-line interface that allows users to interactively filter courses and persists their configurations via a JSON-based settings system.
- **Safe File I/O & Export:** Safely writes the normalized datasets to UTF-8 CSVs and Excel workbooks (via the `openpyxl` engine), implementing automated filename generation to prevent accidental data overwriting.  
## Quick Start (Installation & Usage)

### 1. Clone the repository

```bash
git clone https://github.com/Brozi/timetable-converter.git
cd timetable-converter
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the converter

```bash
python main.py
```

### 5. Use the interactive workflow

From the command-line menu, choose one of the available options:

1. Load a timetable file.
2. Select the source format:
   - **UniTime**
   - **USOS**
3. Apply optional course or activity-type filters.
4. Select an operating mode:
   - **Quick:** Uses saved configuration settings.
   - **Custom:** Provides full control over transformations and output columns.
   - **Debug:** Produces an Excel file with minimally transformed data.
5. Choose the output format:
   - CSV
   - XLSX
   - Both

The application automatically creates `settings.json` for persisted preferences and generates a unique output filename when a file with the requested name already exists.
