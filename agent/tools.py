from langchain_core.tools import tool

from .store import BOOKINGS, HOTELS


@tool
def find_hotels(city: str, max_nightly_rate: int | None = None) -> list[dict]:
    """List Harbor Hotels in a city, optionally under a nightly rate in euros, with rooms left."""
    wanted = city.strip().lower()
    return [
        hotel
        for hotel in HOTELS
        if hotel["city"].lower() == wanted
        and (max_nightly_rate is None or hotel["nightly_rate"] <= max_nightly_rate)
    ]


@tool
def get_booking(booking_id: str) -> dict:
    """Look up a booking by its id (for example HB-5001)."""
    key = booking_id.strip().upper()
    booking = BOOKINGS.get(key)
    if booking is None:
        return {"found": False, "booking_id": booking_id}
    return {"found": True, "booking_id": key, **booking}


@tool
def cancel_booking(booking_id: str) -> dict:
    """Cancel a confirmed booking. Checked-in or already cancelled bookings cannot be cancelled."""
    key = booking_id.strip().upper()
    booking = BOOKINGS.get(key)
    if booking is None:
        return {"cancelled": False, "error": "booking_not_found"}
    if booking["status"] != "confirmed":
        return {"cancelled": False, "error": f"booking_is_{booking['status']}"}
    booking["status"] = "cancelled"
    return {"cancelled": True, "booking_id": key}


@tool
def check_late_checkout(booking_id: str) -> dict:
    """Check whether a confirmed booking can check out late, until 1 pm."""
    key = booking_id.strip().upper()
    booking = BOOKINGS.get(key)
    if booking is None:
        return {"available": False, "error": "booking_not_found"}
    return {"available": booking["status"] == "confirmed", "booking_id": key, "until": "13:00"}


TOOLS = [find_hotels, get_booking, cancel_booking, check_late_checkout]
