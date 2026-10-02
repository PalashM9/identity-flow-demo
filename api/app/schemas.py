from datetime import date, datetime
from pydantic import BaseModel, Field


class PersonResponse(BaseModel):
    id: str
    full_name: str
    date_of_birth: date
    document_number: str
    expires_on: date
    country: str

    class Config:
        from_attributes = True


class VerificationResponse(BaseModel):
    application_id: str
    status: str
    decision_reason: str
    correlation_id: str
    created_at: datetime


class VerifyRequest(BaseModel):
    person_id: str = Field(..., description="Fictional demo person ID")
    simulate_ocr: bool = True