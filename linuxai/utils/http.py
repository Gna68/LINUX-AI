"""HTTP minimal berbasis stdlib (urllib).

Satu-satunya modul yang membuka koneksi jaringan. Redirect DITOLAK supaya
header API key tidak pernah terkirim ke host lain.
"""
from __future__ import annotations

import http.client
import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

from linuxai import __version__

MAX_RESPONSE_BYTES = 4 * 1024 * 1024


class HttpTimeout(Exception):
    """Permintaan melewati batas waktu."""


class HttpConnectionError(Exception):
    """Gagal terhubung (DNS, koneksi putus, dsb.)."""


@dataclass
class HttpResult:
    status: int
    data: Optional[dict]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _send(req: urllib.request.Request, headers: dict, timeout: float) -> HttpResult:
    req.add_header("User-Agent", f"linuxai/{__version__}")
    for key, value in headers.items():
        req.add_header(key, value)
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as resp:
            status = resp.status
            raw = resp.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as err:
        status = err.code
        try:
            raw = err.read(MAX_RESPONSE_BYTES + 1)
        except Exception:
            raw = b""
    except socket.timeout as err:
        raise HttpTimeout() from err
    except urllib.error.URLError as err:
        if isinstance(err.reason, socket.timeout):
            raise HttpTimeout() from err
        raise HttpConnectionError() from err
    except (OSError, http.client.HTTPException, ValueError) as err:
        raise HttpConnectionError() from err

    data = None
    if len(raw) <= MAX_RESPONSE_BYTES:
        try:
            parsed = json.loads(raw.decode("utf-8", errors="replace"))
            data = parsed if isinstance(parsed, dict) else None
        except ValueError:
            data = None
    return HttpResult(status=status, data=data)


def post_json(url: str, headers: dict, payload: dict, timeout: float = 30.0) -> HttpResult:
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    return _send(req, headers, timeout)


def get_json(url: str, headers: dict, timeout: float = 30.0) -> HttpResult:
    """GET tanpa body (dipakai untuk mengambil daftar model)."""
    return _send(urllib.request.Request(url, method="GET"), headers, timeout)
