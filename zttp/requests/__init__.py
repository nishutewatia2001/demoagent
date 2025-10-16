"""Minimal requests-compatible shim using urllib from the standard library."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib import parse, request as urllib_request


@dataclass
class Response:
    status_code: int
    content: bytes
    headers: Dict[str, str]

    @property
    def text(self) -> str:
        return self.content.decode("utf-8")

    def json(self) -> Any:
        return json.loads(self.text)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def _apply_params(url: str, params: Optional[Dict[str, object]]) -> str:
    if not params:
        return url
    query = parse.urlencode(params, doseq=True)
    parts = parse.urlsplit(url)
    existing = parts.query
    new_query = "&".join(filter(None, [existing, query]))
    return parse.urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))


def get(url: str, params: Optional[Dict[str, object]] = None, timeout: int = 15) -> Response:
    full_url = _apply_params(url, params)
    with urllib_request.urlopen(full_url, timeout=timeout) as resp:
        content = resp.read()
        headers = dict(resp.headers.items())
        status_code = getattr(resp, "status", resp.getcode())
        return Response(status_code=status_code, content=content, headers=headers)


__all__ = ["Response", "get"]
