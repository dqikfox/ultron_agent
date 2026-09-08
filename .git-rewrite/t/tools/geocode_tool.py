from .base import Tool
from geopy.geocoders import Nominatim

class GeocodeTool(Tool):
    name = "geocode"
    description = "Geocode an address to latitude and longitude."
    parameters = {
        "type": "object",
        "properties": {
            "address": {"type": "string", "description": "The address to geocode."}
        },
        "required": ["address"]
    }

    def __init__(self):
        super().__init__()
        self.geolocator = Nominatim(user_agent="ultron_agent")

    def match(self, command: str) -> bool:
        return "geocode" in command.lower() or "latitude" in command.lower() or "longitude" in command.lower()

    def execute(self, command: str = "", address: str = "") -> str:
        addr = address or command
        location = self.geolocator.geocode(addr)
        if location:
            return f"Latitude: {location.latitude}, Longitude: {location.longitude}"
        else:
            return "Address not found."
