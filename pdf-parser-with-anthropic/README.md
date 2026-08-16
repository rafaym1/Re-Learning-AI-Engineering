## PDF Parser with Anthropic

**Problem:** Extract structured metadata (title, authors, key claim, limitations) from a PDF paper using Claude, with streaming output, tool/structured JSON output, retry-on-failure, and per-call cost tracking.
**Stack:** Python, pdfplumber, Anthropic API (Claude), tenacity.

### Run it
```bash
pip install -r requirements.txt
cp .env.example .env   # add your Anthropic API key
python step1.py
```

Set `pdf_path` in `step1.py` to a PDF in this folder before running.
