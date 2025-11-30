import re
from unittest.mock import patch
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from VLSM.network import get_ip_info

def test_ipv4_format():
    mock_response = {
        "ip": "123.45.67.89",
        "version": "IPv4"
    }

    with patch("network.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = str.encode(
            '{"ip": "123.45.67.89", "version": "IPv4"}'
        )

        data = get_ip_info()
        ipv4 = data["ip"]

        pattern = r"^\d{1,3}(\.\d{1,3}){3}$"
        assert re.match(pattern, ipv4), "Invalid IPv4 address format"


def test_ipv4_error_handling():
    with patch("network.urllib.request.urlopen", side_effect=Exception("API down")):
        data = get_ip_info()
        assert "error" in data
