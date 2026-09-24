# Quick start

Get the tool running and process a file in about five minutes.

## 1. Install

```bash
pip install -r requirements.txt
```

## 2. Check it works

```bash
python -m pytest -q
```

Expect the whole suite to pass: over 1000 tests in under thirty seconds.

## 3. Run it

```bash
python main.py
```

Open <http://localhost:8080>.

## 4. Process a file

1. Upload `app_files/samples/messy_contacts.csv`.
2. Choose `hubspot` as the target config.
3. Choose an output format — CSV, Excel, JSON or SQL.
4. Select Run migration.
5. Download the clean data, the QA report, the lineage report and the issues CSV.

The sample is deliberately messy, so the run reports real problems rather than
a clean bill of health:

```
7 rows in, 6 out, quality score 66.7%, 1 errors, 1 warnings
```

## Docker instead

```bash
docker compose up --build
```

The app is at <http://localhost:8080>.

## Hosted on Render instead

The repo ships a `render.yaml` Blueprint. Push to GitHub/GitLab, then in the
Render Dashboard choose **New + → Blueprint** and pick the repo. Render builds
the `Dockerfile` and binds the port it injects via `PORT`.

## Next

| Want to | Read |
| --- | --- |
| Install in more detail, or on a server | [docs/INSTALL.md](docs/INSTALL.md) |
| Add your own CRM or bank format | [docs/CONFIGURATION.md](docs/CONFIGURATION.md) |
| Write your own validation rules | [docs/RULES.md](docs/RULES.md) |
| Understand the whole tool | [README.md](README.md) |