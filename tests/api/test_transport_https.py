"""Verify transport behavior against a synthetic loopback HTTPS server."""

import asyncio
import gzip
import os
import ssl
from collections.abc import AsyncIterator
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from ipaddress import IPv4Address
from pathlib import Path

import pytest
import pytest_asyncio
from aiohttp import ClientSession, TCPConnector, web
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from pytest_socket import socket_allow_hosts

from ned_api import (
    NedConnectionError,
    NedResponseError,
    NedTimeoutError,
    NedTransport,
    TransportResponse,
)


@pytest.fixture(name="tls_contexts")
def _tls_contexts(tmp_path: Path) -> tuple[ssl.SSLContext, ssl.SSLContext]:
    """Generate a temporary certificate trusted only by the test client."""
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Loopback test")])
    now = datetime.now(UTC)
    certificate = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(minutes=1))
        .not_valid_after(now + timedelta(hours=1))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.SubjectAlternativeName([x509.IPAddress(IPv4Address("127.0.0.1"))]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    pem = certificate.public_bytes(serialization.Encoding.PEM)
    certificate_path = tmp_path / "certificate.pem"
    certificate_path.write_bytes(pem)
    key_path = tmp_path / "key.pem"
    descriptor = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as key_file:
        key_file.write(
            key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.PKCS8,
                serialization.NoEncryption(),
            )
        )
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    try:
        server_context.load_cert_chain(certificate_path, key_path)
    finally:
        key_path.unlink()
        certificate_path.unlink()
    client_context = ssl.create_default_context(cadata=pem.decode("ascii"))
    return server_context, client_context


@dataclass(slots=True)
class LocalHttps:
    """Describe a local server and synchronization events for slow requests."""

    origin: str
    session: ClientSession
    paths: list[str]
    received: asyncio.Event
    release: asyncio.Event


@pytest_asyncio.fixture(name="local_https")
async def _local_https(
    tls_contexts: tuple[ssl.SSLContext, ssl.SSLContext],
    socket_enabled: None,
) -> AsyncIterator[LocalHttps]:
    """Start a TLS server on an ephemeral IPv4 loopback port only."""
    # Re-enable socket creation only for this fixture, retaining loopback limits.
    socket_allow_hosts(["127.0.0.1"])
    server_context, client_context = tls_contexts
    paths: list[str] = []
    received = asyncio.Event()
    release = asyncio.Event()

    async def handle(request: web.Request) -> web.Response:
        """Return synthetic responses without accessing external resources."""
        paths.append(request.path)
        if request.path == "/redirect":
            return web.Response(status=302, headers={"Location": "/unexpected"})
        if request.path == "/encoded":
            return web.Response(
                body=gzip.compress(b"synthetic"), headers={"Content-Encoding": "gzip"}
            )
        if request.path == "/slow":
            received.set()
            await release.wait()
        if request.path == "/query":
            return web.Response(
                text=f"{request.query['q']}:{request.headers['Accept-Encoding']}"
            )
        return web.Response(body=b"abcd")

    app = web.Application()
    app.router.add_get("/{resource}", handle)
    runner = web.AppRunner(app, shutdown_timeout=2.0)
    await runner.setup()
    try:
        site = web.TCPSite(runner, "127.0.0.1", 0, ssl_context=server_context)
        await site.start()
        port = runner.addresses[0][1]
        async with ClientSession(
            connector=TCPConnector(ssl=client_context), raise_for_status=True
        ) as session:
            yield LocalHttps(
                f"https://127.0.0.1:{port}", session, paths, received, release
            )
    finally:
        release.set()
        await runner.cleanup()


@pytest.mark.asyncio
async def test_trusted_https_and_query(local_https: LocalHttps) -> None:
    """Perform a real trusted TLS exchange and preserve query encoding."""
    transport = NedTransport(local_https.session, local_https.origin)
    result = await transport.async_get("/query", params={"q": "a & b"})
    assert result == TransportResponse(
        status=200, body=b"a & b:identity", media_type="text/plain"
    )
    assert not local_https.session.closed


@pytest.mark.asyncio
async def test_untrusted_certificate(local_https: LocalHttps) -> None:
    """Reject the temporary certificate when no test trust anchor is configured."""
    async with ClientSession() as session:
        transport = NedTransport(session, local_https.origin)
        with pytest.raises(NedConnectionError) as caught:
            await transport.async_get("/resource")
        assert caught.value.__context__ is None
    assert not local_https.paths


@pytest.mark.asyncio
async def test_no_redirect_request(local_https: LocalHttps) -> None:
    """Return the redirect status without contacting its target."""
    transport = NedTransport(local_https.session, local_https.origin)
    assert (await transport.async_get("/redirect")).status == 302
    assert local_https.paths == ["/redirect"]


@pytest.mark.asyncio
async def test_wire_response_limit(local_https: LocalHttps) -> None:
    """Accept an exact byte limit and reject a larger response on the wire."""
    transport = NedTransport(
        local_https.session, local_https.origin, max_response_bytes=4
    )
    assert (await transport.async_get("/resource")).body == b"abcd"
    smaller = NedTransport(
        local_https.session, local_https.origin, max_response_bytes=3
    )
    with pytest.raises(NedResponseError, match="byte limit"):
        await smaller.async_get("/resource")
    assert not local_https.session.closed


@pytest.mark.asyncio
async def test_wire_content_encoding(local_https: LocalHttps) -> None:
    """Reject an actual compressed response without automatic decompression."""
    transport = NedTransport(local_https.session, local_https.origin)
    with pytest.raises(NedResponseError, match="content encoding"):
        await transport.async_get("/encoded")


@pytest.mark.asyncio
async def test_real_timeout(local_https: LocalHttps) -> None:
    """Enforce a real total timeout while the server holds its response."""
    transport = NedTransport(local_https.session, local_https.origin, timeout=1.0)
    try:
        async with asyncio.timeout(5):
            with pytest.raises(NedTimeoutError):
                await transport.async_get("/slow")
        assert local_https.received.is_set()
        assert not local_https.session.closed
    finally:
        local_https.release.set()


@pytest.mark.asyncio
async def test_real_cancellation(local_https: LocalHttps) -> None:
    """Cancel an in-flight real request and reuse the borrowed session."""
    transport = NedTransport(local_https.session, local_https.origin)
    task = asyncio.create_task(transport.async_get("/slow"))
    try:
        async with asyncio.timeout(5):
            await local_https.received.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
        assert not local_https.session.closed
        assert (await transport.async_get("/resource")).body == b"abcd"
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        local_https.release.set()
