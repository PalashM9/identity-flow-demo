from datetime import date
from app.verifier import evaluate_identity


def test_valid_demo_identity_is_verified():
    decision = evaluate_identity(
        full_name="Ava Schneider",
        document_number="DEMO-A1B2C3",
        expires_on=date(2031, 5, 14),
        ocr_text="Name: Ava Schneider\nDocument Number: DEMO-A1B2C3",
        today=date(2026, 10, 2),
    )

    assert decision.status == "VERIFIED"


def test_expired_demo_identity_is_rejected():
    decision = evaluate_identity(
        full_name="Mia Fischer",
        document_number="DEMO-X9Y8Z7",
        expires_on=date(2024, 3, 27),
        ocr_text="Name: Mia Fischer\nDocument Number: DEMO-X9Y8Z7",
        today=date(2026, 10, 2),
    )

    assert decision.status == "REJECTED"


def test_missing_document_number_needs_review():
    decision = evaluate_identity(
        full_name="Noah Weber",
        document_number="DEMO-D4E5F6",
        expires_on=date(2030, 11, 2),
        ocr_text="Name: Noah Weber",
        today=date(2026, 10, 2),
    )

    assert decision.status == "REVIEW_REQUIRED"