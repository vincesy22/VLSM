import folium

def generate_map(latitude, longitude, output_file="ip_map.html"):
    """
    Generates a folium map centered at the given coordinates.
    Returns the output filename.
    """
    try:
        m = folium.Map(location=[latitude, longitude], zoom_start=10)
        m.save(output_file)
        return output_file
    except Exception as e:
        return None
