from __future__ import annotations

import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from email.message import Message
from typing import Callable, Iterable


class UnsafeURL(ValueError):
    """Raised when a URL violates the outbound fetch safety policy."""


class ResponseTooLarge(UnsafeURL):
    """Raised when a response exceeds the configured byte limit."""


@dataclass(frozen=True, slots=True)
class FetchLimits:
    timeout_seconds: int = 30
    max_response_bytes: int = 2_000_000
    max_redirects: int = 5


@dataclass(slots=True)
class SafeHTTPResponse:
    requested_url: str
    final_url: str
    status: int
    headers: Message
    body: bytes


Resolver = Callable[[str, int], Iterable[tuple]]
Opener = Callable[[urllib.request.Request, int], object]


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def _reject(self, req, fp, code, msg, headers):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

    http_error_301 = _reject
    http_error_302 = _reject
    http_error_303 = _reject
    http_error_307 = _reject
    http_error_308 = _reject


class SafeHTTPClient:
    REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})

    def __init__(
        self,
        *,
        limits: FetchLimits | None = None,
        resolver: Resolver | None = None,
        opener: Opener | None = None,
    ):
        self.limits = limits or FetchLimits()
        self._resolver = resolver or self._resolve
        if opener is None:
            built = urllib.request.build_opener(_NoRedirectHandler())
            self._opener = lambda request, timeout: built.open(request, timeout=timeout)
        else:
            self._opener = opener

    def fetch(
        self,
        url: str,
        *,
        allowed_hosts: set[str] | None = None,
    ) -> SafeHTTPResponse:
        requested_url = url
        current_url = url
        for redirect_count in range(self.limits.max_redirects + 1):
            parsed = self._validate_url(current_url, allowed_hosts=allowed_hosts)
            self._validate_resolved_host(parsed.hostname or "", parsed.port or self._default_port(parsed.scheme))
            request = urllib.request.Request(
                current_url,
                headers={"User-Agent": "OutreachProgram/0.1"},
                method="GET",
            )
            try:
                response = self._opener(request, self.limits.timeout_seconds)
            except urllib.error.HTTPError as exc:
                if exc.code not in self.REDIRECT_STATUSES:
                    raise
                response = exc

            status = int(getattr(response, "status", getattr(response, "code", 0)))
            headers = getattr(response, "headers", Message())
            if status in self.REDIRECT_STATUSES:
                location = headers.get("Location")
                response.close()
                if not location:
                    raise UnsafeURL(f"redirect from {current_url!r} has no Location header")
                if redirect_count >= self.limits.max_redirects:
                    raise UnsafeURL("redirect limit exceeded")
                current_url = urllib.parse.urljoin(current_url, location)
                continue

            content_length = headers.get("Content-Length")
            if content_length:
                try:
                    if int(content_length) > self.limits.max_response_bytes:
                        response.close()
                        raise ResponseTooLarge("response exceeds configured byte limit")
                except ValueError:
                    pass
            body = response.read(self.limits.max_response_bytes + 1)
            response.close()
            if len(body) > self.limits.max_response_bytes:
                raise ResponseTooLarge("response exceeds configured byte limit")
            final_url = getattr(response, "geturl", lambda: current_url)()
            self._validate_url(final_url, allowed_hosts=allowed_hosts)
            self._validate_resolved_host(
                urllib.parse.urlsplit(final_url).hostname or "",
                urllib.parse.urlsplit(final_url).port or self._default_port(urllib.parse.urlsplit(final_url).scheme),
            )
            return SafeHTTPResponse(
                requested_url=requested_url,
                final_url=final_url,
                status=status,
                headers=headers,
                body=body,
            )
        raise UnsafeURL("redirect limit exceeded")

    def validate_destination(self, url: str, *, allowed_hosts: set[str] | None = None) -> str:
        """Apply the same URL, host-scope, DNS, and private-address checks without fetching."""
        parsed = self._validate_url(url, allowed_hosts=allowed_hosts)
        self._validate_resolved_host(
            parsed.hostname or "",
            parsed.port or self._default_port(parsed.scheme),
        )
        return (parsed.hostname or "").casefold().rstrip(".")

    @staticmethod
    def _validate_url(url: str, *, allowed_hosts: set[str] | None) -> urllib.parse.SplitResult:
        try:
            parsed = urllib.parse.urlsplit(url)
            port = parsed.port
        except ValueError as exc:
            raise UnsafeURL(f"invalid URL: {url!r}") from exc
        if parsed.scheme.casefold() not in {"http", "https"}:
            raise UnsafeURL("only http and https URLs are allowed")
        if parsed.username or parsed.password:
            raise UnsafeURL("URL credentials are not allowed")
        hostname = (parsed.hostname or "").casefold().rstrip(".")
        if not hostname:
            raise UnsafeURL("URL hostname is required")
        if port is not None and not 1 <= port <= 65535:
            raise UnsafeURL("URL port is invalid")
        if allowed_hosts:
            normalized = {host.casefold().rstrip(".") for host in allowed_hosts}
            if not any(hostname == host or hostname.endswith(f".{host}") for host in normalized):
                raise UnsafeURL(f"URL host is outside the allowed host scope: {hostname}")
        return parsed

    def _validate_resolved_host(self, hostname: str, port: int) -> None:
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            addresses = self._resolver(hostname, port)
        else:
            addresses = [(None, None, None, None, (hostname, port))]
        seen = False
        for info in addresses:
            sockaddr = info[4] if len(info) > 4 else info
            address = sockaddr[0]
            seen = True
            ip = ipaddress.ip_address(address)
            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
                or ip.is_unspecified
            ):
                raise UnsafeURL(f"URL resolves to a private or reserved address: {address}")
        if not seen:
            raise UnsafeURL(f"URL hostname did not resolve: {hostname}")

    @staticmethod
    def _resolve(hostname: str, port: int) -> list[tuple]:
        return socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)

    @staticmethod
    def _default_port(scheme: str) -> int:
        return 443 if scheme.casefold() == "https" else 80
