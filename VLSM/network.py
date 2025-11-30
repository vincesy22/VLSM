import urllib.request
import json

def get_ip_info():
    """
    Fetches IP data from the API.
    Crucially, it always returns a dictionary, even on error.
    """
    try:
        with urllib.request.urlopen("https://ipapi.co/json/", timeout=10) as response:
            return json.loads(response.read().decode())
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

