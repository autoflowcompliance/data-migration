"""A thin client wrapping the REST API.

    import dataflow

    client = dataflow.connect("http://localhost:8600")
    result = client.clean(open("contacts.csv", "rb").read(), filename="contacts.csv")

Every method is a few lines over the HTTP API; there is no second
implementation of the pipeline here. The session is injectable so a test can
drive a fake or a ``TestClient`` without a socket.
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Any, Protocol


class Session(Protocol):
    def post(self, path: str, **kwargs: Any) -> Any: ...
    def get(self, path: str, **kwargs: Any) -> Any: ...


@dataclass
class Response:
    """A parsed API reply."""

    status_code: int
    data: dict[str, Any]

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300 and self.data.get("status") != "error"


class _UrllibSession:
    """The default transport: stdlib only, so the SDK has no dependencies."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _send(self, request: urllib.request.Request) -> Response:
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                return Response(
                    int(response.status),
                    json.loads(body) if body else {},
                )
        except urllib.error.HTTPError as exc:
            body = exc.read()
            return Response(int(exc.code), json.loads(body) if body else {})

    def post(self, path: str, **kwargs: Any) -> Response:
        body = kwargs.get("body")
        headers = kwargs.get("headers", {})
        request = urllib.request.Request(
            f"{self.base_url}{path}", data=body, headers=headers, method="POST"
        )
        return self._send(request)

    def get(self, path: str, **kwargs: Any) -> Response:
        request = urllib.request.Request(f"{self.base_url}{path}", method="GET")
        return self._send(request)


def _multipart(data: bytes, filename: str, fields: dict[str, str]) -> tuple[bytes, dict[str, str]]:
    """Build a multipart body by hand; the SDK stays dependency-free."""
    boundary = "----DataFlowSDKBoundary"
    parts: list[bytes] = []
    for key, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{value}\r\n".encode()
        )
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
        f'filename="{filename}"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()
    )
    parts.append(data)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    return b"".join(parts), headers


class DataFlowClient:
    """The SDK. One method per endpoint the API exposes."""

    def __init__(self, base_url: str = "http://127.0.0.1:8600", session: Session | None = None):
        self.base_url = base_url.rstrip("/")
        self.session: Session = session or _UrllibSession(self.base_url)

    def _upload(
        self, path: str, data: bytes, filename: str, fields: dict[str, str] | None = None
    ) -> Response:
        body, headers = _multipart(data, filename, fields or {})
        return self.session.post(path, body=body, headers=headers)

    def health(self) -> Response:
        return self.session.get("/health")

    def validate(self, data: bytes, filename: str = "upload.csv", crm: str = "hubspot") -> Response:
        return self._upload("/validate", data, filename, {"crm": crm})

    def clean(self, data: bytes, filename: str = "upload.csv", crm: str = "hubspot") -> Response:
        return self._upload("/clean", data, filename, {"crm": crm})

    def profile(self, data: bytes, filename: str = "upload.csv") -> Response:
        return self._upload("/profile", data, filename)

    def map_columns(
        self, data: bytes, filename: str = "upload.csv", crm: str = "hubspot"
    ) -> Response:
        return self._upload("/map", data, filename, {"crm": crm})

    def mask(
        self,
        data: bytes,
        filename: str = "upload.csv",
        fields: list[str] | None = None,
        strategy: str = "redact",
    ) -> Response:
        form = {"strategy": strategy}
        if fields:
            form["fields"] = ",".join(fields)
        return self._upload("/mask", data, filename, form)

    def lineage(
        self, data: bytes, filename: str = "upload.csv", crm: str = "hubspot"
    ) -> Response:
        return self._upload("/lineage", data, filename, {"crm": crm})

    def quality(
        self,
        data: bytes,
        filename: str = "upload.csv",
        sla: dict[str, float] | None = None,
        action: str | None = None,
    ) -> Response:
        """Judge an upload against a quality SLA.

        ``sla`` maps a dimension name to its floor; ``action`` is the
        regression action (``alert``, ``block``, ``quarantine``).
        """
        form = {f"sla_{name}": str(value) for name, value in (sla or {}).items()}
        if action is not None:
            form["regression_action"] = action
        return self._upload("/quality", data, filename, form)

    def profile_columns(
        self,
        data: bytes,
        filename: str = "upload.csv",
        *,
        statistics: bool = False,
        patterns: bool = False,
        outliers: bool = False,
        outlier_method: str | None = None,
        outlier_k: float | None = None,
        outlier_contamination: float | None = None,
        outlier_columns: list[str] | None = None,
    ) -> Response:
        """Describe an upload column by column.

        Each section is opt-in, matching the ``profiling:`` config block, so
        the cost of a wide frame is only paid when it is asked for.
        """
        form: dict[str, str] = {}
        if statistics:
            form["statistics"] = "true"
        if patterns:
            form["patterns"] = "true"
        if outliers:
            form["outliers"] = "true"
        if outlier_method is not None:
            form["outlier_method"] = outlier_method
        if outlier_k is not None:
            form["outlier_k"] = str(outlier_k)
        if outlier_contamination is not None:
            form["outlier_contamination"] = str(outlier_contamination)
        if outlier_columns:
            form["outlier_columns"] = ",".join(outlier_columns)
        return self._upload("/profile/columns", data, filename, form)

    def audit(self, limit: int = 100) -> Response:
        return self.session.get(f"/audit?limit={limit}")

    def schedule(self, expression: str, count: int = 5) -> Response:
        import urllib.parse

        query = urllib.parse.urlencode({"expression": expression, "count": count})
        return self.session.get(f"/schedule?{query}")


def connect(base_url: str = "http://127.0.0.1:8600") -> DataFlowClient:
    """Connect a client to a running API."""
    return DataFlowClient(base_url)
