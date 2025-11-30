import urllib.request
import json
from map_generator import generate_map

def get_ip_info():
    """
    Fetches IP data from the API.
    Crucially, it always returns a dictionary, even on error.
    If successful and latitude/longitude are available, generates a map and adds 'map_file' to the dictionary.
    """
    try:
        with urllib.request.urlopen("https://ipapi.co/json/", timeout=10) as response:
            data = json.loads(response.read().decode())
            # Generate map if latitude and longitude are available
            if 'latitude' in data and 'longitude' in data and data['latitude'] is not None and data['longitude'] is not None:
                map_file = generate_map(data['latitude'], data['longitude'])
                data['map_file'] = map_file
            return data
    except Exception as e:
        return {"error": f"Failed to retrieve data: {e}"}

if __name__ == '__main__':
    print("Testing network.py...")
    data = get_ip_info()
    if "error" in data:
        print(f"An error occurred: {data['error']}")
    else:
        import pprint
        pprint.pprint(data)

