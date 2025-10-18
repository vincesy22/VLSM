import urllib.request
import json
import socket

def get_local_ips():
    """Return local IPv4 and IPv6 addresses."""
    local_ipv4 = "N/A"
    local_ipv6 = "N/A"
    try:
        # Get local IPv4
        local_ipv4 = socket.gethostbyname(socket.gethostname())

        # Get local IPv6 (if available)
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6):
            ipv6 = info[4][0]
            if not ipv6.startswith("fe80"):  # ignore link-local
                local_ipv6 = ipv6
                break
        if local_ipv6 == "N/A":
            # fallback to link-local if no global one
            for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6):
                ipv6 = info[4][0]
                if ipv6.startswith("fe80"):
                    local_ipv6 = ipv6
                    break
    except Exception:
        pass
    return {"local_ipv4": local_ipv4, "local_ipv6": local_ipv6}


def get_ip_info():
    """
    Fetch public IP and geolocation data from ipapi.co (IPv4 + IPv6 if available).
    Adds local IPs to the returned dictionary.
    """
    def fetch_from_api(url):
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())

    try:
        # Public IP (auto)
        data = fetch_from_api("https://ipapi.co/json/")

        # Public IPv6 (optional)
        try:
            ipv6_data = fetch_from_api("https://ipapi.co/ipv6/json/")
            data["ipv6"] = ipv6_data.get("ip", "N/A")
        except Exception:
            data["ipv6"] = "N/A"

        # Add local IPs
        data.update(get_local_ips())

        return data

    except Exception as e:
        return {"error": f"Failed to retrieve data: {e}"}


if __name__ == "__main__":
    print("Testing network.py...")
    result = get_ip_info()
    import pprint
    pprint.pprint(result)
