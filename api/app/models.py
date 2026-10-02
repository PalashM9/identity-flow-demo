from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_id() -> str:
    return str(uuid4())


class DemoPerson(Base):
    __tablename__ = "demo_people"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(Date, nullable=False)
    document_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    expires_on: Mapped[datetime] = mapped_column(Date, nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="DE")
    expected_ocr_text: Mapped[str] = mapped_column(Text, nullable=False)

    applications: Mapped[list["VerificationApplication"]] = relationship(back_populates="person")


class VerificationApplication(Base):
    __tablename__ = "verification_applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    person_id: Mapped[str] = mapped_column(ForeignKey("demo_people.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="PENDING")
    decision_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    ocr_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    correlation_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    person: Mapped["DemoPerson"] = relationship(back_populates="applications")
    events: Mapped[list["AuditEvent"]] = relationship(back_populates="application")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    application_id: Mapped[str] = mapped_column(ForeignKey("verification_applications.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    application: Mapped["VerificationApplication"] = relationship(back_populates="events")


class WebhookOutbox(Base):
    __tablename__ = "webhook_outbox"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    event_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)