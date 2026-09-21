# Install

Three commands, from the repository root:

```bash
pip install -r requirements.txt
python -m pytest -q
python main.py
```

Then open <http://localhost:8080>.

## Docker

```bash
docker compose up --build
```

The app is at <http://localhost:8080>. `configs/`, `samples/`, and `output/`
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

## Render

The repo ships a `render.yaml` Blueprint that deploys the NiceGUI app as a
Docker web service.

1. Push the repo to GitHub or GitLab.
2. In the Render Dashboard: **New + → Blueprint**, then pick the repo.
3. Render reads `render.yaml`, builds the `Dockerfile`, and starts `main.py`.

Two things are worth knowing about how it binds:

- **The port comes from `PORT`, not `DATAREADY_PORT`.** Render injects `PORT`
  (default `10000`) and routes traffic only to that port. `resolve_port()` in
  `app_files/settings.py` gives `PORT` precedence for exactly this reason;
  binding anywhere else fails the deploy with *no open ports detected*.
- **`AUTOFLOW_HOME` and `DATAREADY_HOME` are both set to `/app/run_config`.**
  Two different state layers read those two names, so setting only one leaves
  the other writing into the repo. Render's filesystem is ephemeral, so that
  state resets on each deploy — attach a persistent disk mounted at that path
  if a licence, branding, or audit history must survive a redeploy.

The deployed app is unlicensed by default and runs under the demo limits in
`app_files/licensing/limits.py` (500 rows, 5 MB, CSV only, watermarked). Add a
licence through `DATAREADY_HOME` for the full tool.

## Verifying the install

```bash
python -m pytest -q
```

Expect `465 passed`. The suite covers the frozen core plus every new layer, and
runs in a few seconds — there is no reason not to run it before a commit.