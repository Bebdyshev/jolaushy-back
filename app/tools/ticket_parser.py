from sqlalchemy.orm import Session
from schemas.models import Ticket, RoadmapInDB
from datetime import datetime, date

def find_tickets(db: Session, roadmap_id: int, destination: str, start_date: str, end_date: str) -> str:
    """
    Finds flight tickets for the given destination and dates and saves them to the database.
    This is a mock tool and does not call a real API.
    """
    try:
        # Create dummy tickets
        ticket_to = Ticket(
            roadmap_id=roadmap_id,
            type="flight",
            from_="Home City",
            to=destination,
            departure=datetime.strptime(start_date, "%Y-%m-%d"),
            arrival=datetime.strptime(start_date, "%Y-%m-%d"),
            price=350,
            provider_url="https://example.com/flight_to"
        )

        ticket_from = Ticket(
            roadmap_id=roadmap_id,
            type="flight",
            from_=destination,
            to="Home City",
            departure=datetime.strptime(end_date, "%Y-%m-%d"),
            arrival=datetime.strptime(end_date, "%Y-%m-%d"),
            price=380,
            provider_url="https://example.com/flight_from"
        )
        
        db.add(ticket_to)
        db.add(ticket_from)
        db.commit()

        return f"Successfully found and saved 2 tickets for the trip to {destination}."
    except Exception as e:
        db.rollback()
        return f"An error occurred while finding tickets: {e}" 