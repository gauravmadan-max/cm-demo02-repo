"""Host resolution diagnostics for internal operations."""

import ipaddress
import re
import subprocess

_HOSTNAME_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?$"
)


def is_valid_host(host: str) -> bool:
    """Validate that host is a valid hostname, IPv4 address, or IPv6 address."""
    if not host or len(host) > 253:
        return False
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    return bool(_HOSTNAME_REGEX.match(host))


def resolve_host(host: str) -> str:
    """Run host resolution lookup and return command output."""
    if not is_valid_host(host):
        raise ValueError("invalid host format")
    output = subprocess.check_output(
        ["getent", "hosts", "--", host],
        shell=False,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=5,
    )
    return output.strip()
