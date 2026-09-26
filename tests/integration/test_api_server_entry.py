"""The API the server actually serves, not just the app the tests build.

``register_extra_routes(create_app())`` was the only way to reach ``/map``,
``/mask``, ``/metrics`` and the probes, and no entry point did it. ``build_app``
is that entry point. The second half pins the ``__main__`` duplicate-module
trap: running ``api.py`` as a module makes ``api_extras`` import a second copy
of ``api`` and a second ``BadRequest``, so a client error degraded to a 500.
"""

from __future__ import annotations

import importlib.util
import sys

import pytest
from starlette.testclient import TestClient

from app_files.distribution.api import build_app, create_app

CORE = {"/health", "/validate", "/clean", "/profile", "/reconcile"}
EXTRAS = {"/map", "/mask", "/lineage", "/audit", "/schedule", "/metrics", "/ready", "/live"}


def test_build_app_serves_the_documented_routes():
    paths = {getattr(route, "path", None) for route in build_app().routes}
    assert CORE <= paths
    assert EXTRAS <= paths


def test_core_only_keeps_the_original_five():
    paths = {getattr(route, "path", None) for route in build_app(include_extras=False).routes}
    assert CORE <= paths
    assert not (EXTRAS & paths)


def test_probes_and_metrics_answer(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    client = TestClient(build_app())
    assert client.get("/live").status_code == 200
    assert client.get("/ready").status_code in (200, 503)
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "dataflow_runs_total" in metrics.text


def test_a_bad_get_request_is_400_not_500(tmp_path, monkeypatch):
    """The extras raise ``BadRequest``; that must map to 400 over HTTP."""
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    client = TestClient(build_app(), raise_server_exceptions=False)
    response = client.get("/schedule")
    assert response.status_code == 400
    assert response.json()["status"] == "error"


def test_running_api_as_main_keeps_client_errors_400(tmp_path, monkeypatch):
    """``python -m app_files.distribution.api`` must not split the class.

    Executing the module as ``__main__`` gives ``api_extras`` a *different*
    ``BadRequest`` than the one ``create_app`` registered, so the specific
    handler misses and the generic 500 handler answers instead.
    """
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    import uvicorn

    spec = importlib.util.spec_from_file_location(
        "__main__", "app_files/distribution/api.py"
    )
    main_mod = importlib.util.module_from_spec(spec)
    saved_argv, saved_main = sys.argv, sys.modules.get("__main__")
    sys.modules["__main__"] = main_mod
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: None)
    try:
        spec.loader.exec_module(main_mod)
    except SystemExit:
        pass
    finally:
        sys.argv = saved_argv

    app = main_mod.build_app()
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/schedule")

    assert response.status_code == 400, (
        "BadRequest from api_extras fell through to the generic handler; "
        "the __main__ alias is missing from exception_handlers"
    )
    if saved_main is not None:
        sys.modules["__main__"] = saved_main


@pytest.mark.parametrize("path", sorted(EXTRAS - {"/ready", "/live"}))
def test_extra_routes_do_not_500_on_a_bare_get(path, tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOFLOW_HOME", str(tmp_path))
    client = TestClient(build_app(), raise_server_exceptions=False)
    response = client.get(path)
    assert response.status_code != 500
