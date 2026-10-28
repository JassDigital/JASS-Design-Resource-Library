# JASS Design Resource Library v0.1.0

A Windows desktop catalogue for saving, searching, filtering, and reviewing design resources. Built with Python, PySide6, and SQLite.

## Features
- Search by name, category, description, URL, tags, and notes.
- Filter by category, platform, pricing, and review status.
- Add, edit, delete, and favourite resource entries.
- Open resource websites in your default browser.
- Record licence reminders and personal notes.
- Export the catalogue to CSV.
- Starter catalogue with fonts, icons, UI libraries, templates, illustrations, inspiration, and design tools.
- SQLite database stored separately from the source code.

## Requirements
Windows 10/11 and Python 3.11+. No virtual environment required.

## Run
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

## Tests
```powershell
python -m pytest
```

## Data location
`%LOCALAPPDATA%\JASS\DesignResourceLibrary\resources.sqlite3`

This is a starter catalogue, not a live mirror of any repository. Resource availability, pricing, and licences can change. Verify the provider's current terms before commercial use.
