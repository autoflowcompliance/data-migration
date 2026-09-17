# Install

Three commands, from the repository root:

```bash
pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app_files/interface/web/app.py
```

Then open <http://localhost:8501>.

## Why `python -m streamlit` instead of `streamlit`

On some systems the `streamlit` console script is not on `PATH` even though the
package is installed. `python -m streamlit` always resolves to the interpreter
you installed into, so it is the more reliable invocation.

## Docker

```bash
docker compose up --build
```

The app is at <http://localhost:8501>. `configs/`, `samples/`, and `output/`
are mounted from the host, so dropping a new YAML into `app_files/configs/`
appears in the config selector without a rebuild.

## Optional extras

Everything the test suite needs is in `requirements.txt`. One dependency is
imported lazily and only matters for PDF ingestion:

| Package | Needed for | Install |
| --- | --- | --- |
| `pdfplumber` | Reading bank statement PDFs | already in `requirements.txt` |

If you installed before PDF support was added, `pip install pdfplumber`. The
PDF adapter raises a clear, actionable error rather than an `ImportError`
traceback when it is missing.

## Verifying the install

```bash
python -m pytest -q
```

Expect `223 passed`. The suite covers the frozen core plus every new layer, and
runs in a couple of seconds — there is no reason not to run it before a commit.