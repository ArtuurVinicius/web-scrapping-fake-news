# Boatos.org health scraper

This project scrapes health-related articles from boatos.org and stores them in JSONL format for building a training corpus.

Setup (Windows):

1. Create and activate the virtual environment (cmd):

```powershell
python -m venv venv
venv\Scripts\activate.bat
```

Or (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

2. Install dependencies and Playwright browsers:

```powershell
pip install -r requirements.txt
python -m playwright install
```

3. Run the scraper (writes to `corpus.jsonl`):

```powershell
python main.py
```

Options: edit `scraper.py` to change `max_articles` or the output filename.
