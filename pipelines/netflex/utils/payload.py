from .geolocation import get_geolocation

def netflex_payload_transformer(payload: dict) -> dict:
    (location_str, *_) = get_geolocation("8.8.8.8")
    
    return {
        "client_location": location_str,
        "measurement_type": payload["speedtest"]["task_type"],
        "measurement_data": payload["speedtest"]["task_results"]
    }