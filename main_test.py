from services import FlightService,AirportService,CityService


flight = FlightService()
flight.update_flight(1,{
"name":"FR14234",
"arrivalAirport": "Sof3ia airport",
"departureAirport": "Lart655hi Airport",
"departureTime": "13:00",
"travelTime": 2430,
"price": "6657"
})


print(flight.get_all_flights())
