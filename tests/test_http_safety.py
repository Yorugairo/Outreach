from __future__ import annotations

import io
from email.message import Message

import pytest

from src.fetchers.http_client import (
    FetchLimits,
    SafeHTTPClient,
    UnsafeURL,
)


class FakeResponse:
    def __init__(self, body: bytes, *, status: int = 200, url: str = "https://example.com/"):
        self._body = body
        self.status = status
        self.code = status
        self.url = url
        self.headers = Message()
        self.headers["Content-Length"] = str(len(body))

    def read(self, size: int = -1) -> bytes:
        return self._body if size < 0 else self._body[:size]

    def geturl(self) -> str:
        return self.url

    def close(self) -> None:
        return None


def public_resolver(host: str, port: int):
    return [(None, None, None, None, ("93.184.216.34", port))]


def test_rejects_non_http_scheme_before_resolution():
    client = SafeHTTPClient(resolver=public_resolver)

    with pytest.raises(UnsafeURL, match="http and https"):
        client.fetch("file:///etc/passwd")


def test_rejects_private_dns_destination():
    def private_resolver(host: str, port: int):
        return [(None, None, None, None, ("127.0.0.1", port))]

    client = SafeHTTPClient(resolver=private_resolver)

    with pytest.raises(UnsafeURL, match="private"):
        client.fetch("https://internal.example/")


def test_revalidates_redirect_destination_and_rejects_private_target():
    first = FakeResponse(b"", status=302, url="https://example.com/")
    first.headers["Location"] = "http://169.254.169.254/latest/meta-data/"
    responses = iter([first])

    def opener(request, timeout):
        return next(responses)

    def resolver(host: str, port: int):
        if host == "example.com":
            return [(None, None, None, None, ("93.184.216.34", port))]
        return [(None, None, None, None, ("10.0.0.1", port))]

    client = SafeHTTPClient(
        limits=FetchLimits(max_redirects=2),
        resolver=resolver,
        opener=opener,
    )

    with pytest.raises(UnsafeURL, match="private"):
        client.fetch("https://example.com/")


def test_rejects_response_larger_than_limit():
    client = SafeHTTPClient(
        limits=FetchLimits(max_response_bytes=3),
        resolver=public_resolver,
        opener=lambda request, timeout: FakeResponse(b"abcd"),
    )

    with pytest.raises(UnsafeURL, match="response exceeds"):
        client.fetch("https://example.com/")


def test_enforces_allowed_host_scope():
    client = SafeHTTPClient(resolver=public_resolver)

    with pytest.raises(UnsafeURL, match="host scope"):
        client.fetch("https://other.example/", allowed_hosts={"example.com"})


def test_returns_body_and_final_url_for_safe_response():
    client = SafeHTTPClient(
        resolver=public_resolver,
        opener=lambda request, timeout: FakeResponse(b"hello", url="https://example.com/final"),
    )

    result = client.fetch("https://example.com/start", allowed_hosts={"example.com"})

    assert result.body == b"hello"
    assert result.status == 200
    assert result.final_url == "https://example.com/final"
