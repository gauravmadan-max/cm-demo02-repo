"""Host resolution diagnostics for internal operations."""

import subprocess


def resolve_host(host: str) -> str:
    """Run host resolution lookup and return command output."""
    command = f"getent hosts {host}"
    output = subprocess.check_output(
        command,
        shell=True,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=5,
    )
    return output.strip()
