from configuration_preferences.domain.trip import Trip
from configuration_preferences.infrastructure.link_repository import TripRepository

class TripService:
    def __init__(self):
        self.repository = TripRepository()

    def add_trip(self, data):
        trip = Trip(
            title=data["title"],
            date=data["date"],
            time=data["time"],
            route=data["route"]
        )
        self.repository.save_trip(trip)
        return {"message": "Trip registrado correctamente."}

    def get_all_trips(self):
        trips = self.repository.get_all_trips()
        return trips