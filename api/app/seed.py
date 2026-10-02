from datetime import date
from sqlalchemy.orm import Session

from app.models import DemoPerson

DEMO_PEOPLE = [
    {
        "full_name": "Ava Schneider",
        "date_of_birth": date(1993, 5, 14),
        "document_number": "DEMO-A1B2C3",
        "expires_on": date(2031, 5, 14),
        "country": "DE",
        "expected_ocr_text": """DEMO IDENTITY CARD
Name: Ava Schneider
Date of Birth: 1993-05-14
Document Number: DEMO-A1B2C3
Country: DE
Expiry Date: 2031-05-14
DEMO ONLY - NOT A REAL ID""",
    },
    {
        "full_name": "Noah Weber",
        "date_of_birth": date(1988, 11, 2),
        "document_number": "DEMO-D4E5F6",
        "expires_on": date(2030, 11, 2),
        "country": "DE",
        "expected_ocr_text": """DEMO IDENTITY CARD
Name: Noah Weber
Date of Birth: 1988-11-02
Document Number: DEMO-D4E5F6
Country: DE
Expiry Date: 2030-11-02
DEMO ONLY - NOT A REAL ID""",
    },
    {
        "full_name": "Mia Fischer",
        "date_of_birth": date(1995, 3, 27),
        "document_number": "DEMO-X9Y8Z7",
        "expires_on": date(2024, 3, 27),
        "country": "DE",
        "expected_ocr_text": """DEMO IDENTITY CARD
Name: Mia Fischer
Date of Birth: 1995-03-27
Document Number: DEMO-X9Y8Z7
Country: DE
Expiry Date: 2024-03-27
DEMO ONLY - NOT A REAL ID""",
    },
]


def seed_demo_people(db: Session) -> None:
    if db.query(DemoPerson).count() > 0:
        return

    for person in DEMO_PEOPLE:
        db.add(DemoPerson(**person))

    db.commit()