# PaperLens MD

Evidence-first Molecular Dynamics Methods scanner.

Upload a scientific PDF to extract **candidate** MD methods parameters (MD engine, force field, timestep, duration, water model, thermostats, etc.), view the supporting PDF page and nearby text, and export results as CSV/JSON. The reproducibility checklist is for manual review and is **not** a claim that missing values were omitted by the authors.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501 **only while the server is running**.

## Deploy

Go to https://share.streamlit.io/ and create an app from the public GitHub repo `strawberryHunter/paperlens-md`, branch `main`, main file `app.py`.

## Limits

Rule-based prototype, not an LLM or scientific reviewer. False positives (including References) and missed values are possible. PDF page numbers refer to PDF pages. Scanned PDFs and supplementary files may need separate processing. Do not upload confidential manuscripts without checking service policies.

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

## References

- https://doi.org/10.1021/acs.jcim.3c00599
- https://doi.org/10.1038/s42003-023-04653-0
