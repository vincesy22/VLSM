# Public IP and Geolocation Finder
# Version that uses only built-in Python modules (no requests needed)

import urllib.request
import json

def get_ip_info():
    try:
        # Open the API URL
        with urllib.request.urlopen("https://ipapi.co/json/") as response:
            data = json.loads(response.read().decode())

        print("\n PUBLIC IP ADDRESS INFORMATION \n")
        print(f"IPv4 Address : {data.get('ip', 'N/A')}")
        print(f"Version      : {data.get('version', 'N/A')}")
        print(f"City         : {data.get('city', 'N/A')}")
        print(f"Region       : {data.get('region', 'N/A')}")
        print(f"Country      : {data.get('country_name', 'N/A')} ({data.get('country_code', 'N/A')})")
        print(f"Latitude     : {data.get('latitude', 'N/A')}")
        print(f"Longitude    : {data.get('longitude', 'N/A')}")
        print(f"Timezone     : {data.get('timezone', 'N/A')}")
        print(f"ISP          : {data.get('org', 'N/A')}")
        print(f"ASN          : {data.get('asn', 'N/A')}")
        print("\nData provided by ipapi.co\n")

    except Exception as e:
        print(" Error retrieving data:", e)

if __name__ == "__main__":
    get_ip_info()
