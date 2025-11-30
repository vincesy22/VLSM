import re
from unittest.mock import patch
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from VLSM.network import get_ip_info

def test_ipv6_format():
    mock_ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

    with patch("network.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.read.return_value = str.encode(
            f'{{"ip": "{mock_ipv6}", "version": "IPv6"}}'
        )

        data = get_ip_info()
        ipv6 = data["ip"]

        pattern = r"^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$"
        assert re.match(pattern, ipv6), "Invalid IPv6 format"


def test_ipv6_error_handling():
    with patch("network.urllib.request.urlopen", side_effect=Exception("Timeout")):
        data = get_ip_info()
        assert "error" in data
