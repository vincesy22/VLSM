import urllib.request
import json
import socket
from typing import Dict, Any


def safe_json_loads(raw_bytes: bytes) -> Dict[str, Any]:
    try:
        return json.loads(raw_bytes.decode())
    except Exception:
        return {"error": "Invalid JSON response"}


def get_ip_info() -> Dict[str, Any]:
    """
    Fetches public IP/geolocation data from ipapi.co.
    Always returns a dictionary; on any error returns {"error": "..."}.
    """
    url = "https://ipapi.co/json/"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            body = response.read()
            data = safe_json_loads(body)
            # Normalize some fields for UI consumers
            if "ip" in data:
                data.setdefault("public_ip", data.get("ip"))
            if "asn" not in data and "org" in data:
                # ipapi may return 'org' with "AS12345 Name"; keep org as-is
                data.setdefault("asn", data.get("asn", "N/A"))
            return data
    except Exception as e:
        return {"error": f"Failed to retrieve data: {e}"}


def _get_local_ipv4() -> str:
    """
    Determines the local IPv4 address by opening a UDP socket to a public IPv4 address.
    This doesn't send any packets on UDP — it's a trick to learn the local address.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Google DNS IPv4: 8.8.8.8 port 80 (UDP)
        s.connect(("8.8.8.8", 80))
        addr = s.getsockname()[0]
        s.close()
        return addr
    except Exception:
        return "N/A"


def _get_local_ipv6() -> str:
    """
    Determines the local IPv6 address by opening a UDP IPv6 socket to a public IPv6 address.
    If the environment doesn't support IPv6 or it's not configured, returns "N/A".
    """
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        # Google Public DNS IPv6:
        s.connect(("2001:4860:4860::8888", 80))
        addr = s.getsockname()[0]
        s.close()
        # Some systems return scope id e.g. "fe80::1%eth0" — keep as-is
        return addr
    except Exception:
        return "N/A"


def get_local_ips() -> Dict[str, str]:
    """
    Returns both local IPv4 and IPv6 addresses as a dict:
    { "local_ipv4": "...", "local_ipv6": "..." }
    Values are "N/A" when unavailable.
    """
    return {"local_ipv4": _get_local_ipv4(), "local_ipv6": _get_local_ipv6()}


if __name__ == "__main__":
    print("Testing network.py...")
    print("Local IPs:", get_local_ips())
    data = get_ip_info()
    import pprint

    pprint.pprint(data)
