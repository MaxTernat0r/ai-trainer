"""Tiny TCP proxy for forwarding container SMTP traffic through the host.

Production VPS can reach Gmail SMTP over IPv6 from the host, while Docker
containers only have IPv4 and the provider filters outbound SMTP over IPv4.
This proxy runs with host networking, listens only on the Docker bridge gateway,
and forwards bytes to Gmail over IPv6.
"""

from __future__ import annotations

import asyncio
import logging
import os
import socket


BUFFER_SIZE = 65536
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("smtp_tcp_proxy")


def _target_family() -> socket.AddressFamily:
    value = os.getenv("SMTP_PROXY_TARGET_FAMILY", "ipv6").strip().lower()
    if value == "ipv6":
        return socket.AF_INET6
    if value == "ipv4":
        return socket.AF_INET
    return socket.AF_UNSPEC


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while data := await reader.read(BUFFER_SIZE):
            writer.write(data)
            await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def _handle_client(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
) -> None:
    target_host = os.getenv("SMTP_PROXY_TARGET_HOST", "smtp.gmail.com")
    target_port = int(os.getenv("SMTP_PROXY_TARGET_PORT", "587"))
    peer = client_writer.get_extra_info("peername")
    try:
        logger.info("accepted %s -> %s:%s", peer, target_host, target_port)
        target_reader, target_writer = await asyncio.open_connection(
            target_host,
            target_port,
            family=_target_family(),
        )
        logger.info("connected %s -> %s:%s", peer, target_host, target_port)
        await asyncio.gather(
            _pipe(client_reader, target_writer),
            _pipe(target_reader, client_writer),
        )
    except Exception:
        logger.exception("proxy connection failed for %s", peer)
        client_writer.close()
        await client_writer.wait_closed()


async def main() -> None:
    listen_host = os.getenv("SMTP_PROXY_LISTEN_HOST", "172.18.0.1")
    listen_port = int(os.getenv("SMTP_PROXY_LISTEN_PORT", "587"))
    server = await asyncio.start_server(_handle_client, listen_host, listen_port)
    logger.info("listening on %s:%s", listen_host, listen_port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
