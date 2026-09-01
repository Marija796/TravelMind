"""
Pure string-building functions for a destination's default accommodation/
flight search links - no ORM/model imports, so these are safe to call from
both Destination.save() and a data migration without coupling either to
live model behavior.

These are real, working search-results URLs (not a fake/generic homepage
link) built from each destination's own city/country, so two different
destinations never end up with the same link. An admin can still override
either field with a specific URL; these generators only fill in a default
when the stored field is left blank.
"""
from urllib.parse import urlencode


def generate_booking_url(city, country):
    location = f'{city}, {country}' if city else country
    return 'https://www.booking.com/searchresults.html?' + urlencode({'ss': location})


def generate_flight_url(city, name):
    destination = city or name
    return 'https://www.google.com/travel/flights?' + urlencode({'q': f'Flights to {destination}'})
