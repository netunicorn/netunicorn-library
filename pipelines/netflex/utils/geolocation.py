import requests

def get_geolocation(ip: str):
    """
    Get the geolocation of an IP address using ip-api.com.
    """
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        location_data = response.json()

        if location_data and 'city' in location_data:
            city = location_data['city']
            loc = location_data.get('loc', '34.0549,118.2426')
            lat, lon = loc.split(',')
            return (city, float(lat), float(lon))
        else:
            return ("losangeles", 34.0549, 118.2426)
        
    except Exception as e:
        print(f"Error fetching geolocation: {e}")
        return ("losangeles", 34.0549, 118.2426)