import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db
from app.models import AuditEvent, DemoPerson, VerificationApplication
from app.ocr import read_identity_document
from app.schemas import PersonResponse, VerificationResponse
from app.security import require_basic_auth
from app.seed import seed_demo_people
from app.verifier import evaluate_identity
from app.webhooks import add_to_outbox, deliver_outbox_event
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("/tmp/identity_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_people(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Identity Flow Demo",
    version="1.0.0",
    description="Local demo only. Uses fictional identities and must not be used for real verification.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Correlation-Id"],
)

def correlation_id_from_header(value: str | None) -> str:
    return value or str(uuid.uuid4())


@app.get("/health")
def health():
    return {"status": "ok", "service": "identity-api"}


@app.get("/v1/demo-people", response_model=list[PersonResponse])
def list_demo_people(
    _: str = Depends(require_basic_auth),
    db: Session = Depends(get_db),
):
    return db.query(DemoPerson).all()


@app.post("/v1/verifications/{person_id}", response_model=VerificationResponse)
async def verify_simulated_document(
    person_id: str,
    x_correlation_id: str | None = Header(default=None),
    _: str = Depends(require_basic_auth),
    db: Session = Depends(get_db),
):
    person = db.get(DemoPerson, person_id)

    if not person:
        raise HTTPException(status_code=404, detail="Demo person not found")

    correlation_id = correlation_id_from_header(x_correlation_id)

    decision = evaluate_identity(
        full_name=person.full_name,
        document_number=person.document_number,
        expires_on=person.expires_on,
        ocr_text=person.expected_ocr_text,
    )

    application = VerificationApplication(
        person_id=person.id,
        status=decision.status,
        decision_reason=decision.reason,
        ocr_text=person.expected_ocr_text,
        correlation_id=correlation_id,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    event_payload = {
        "application_id": application.id,
        "person_id": person.id,
        "status": application.status,
        "reason": application.decision_reason,
        "correlation_id": correlation_id,
    }

    db.add(
        AuditEvent(
            application_id=application.id,
            event_type="verification.completed",
            correlation_id=correlation_id,
            payload=event_payload,
        )
    )
    db.commit()

    outbox_event = add_to_outbox(
        db,
        event_type="verification.completed",
        payload=event_payload,
    )
    await deliver_outbox_event(db, outbox_event)

    logger.info(
        "verification_completed",
        extra={
            "application_id": application.id,
            "status": application.status,
            "correlation_id": correlation_id,
        },
    )

    return VerificationResponse(
        application_id=application.id,
        status=application.status,
        decision_reason=application.decision_reason,
        correlation_id=correlation_id,
        created_at=application.created_at,
    )


@app.post("/v1/verifications/upload/{person_id}", response_model=VerificationResponse)
async def verify_uploaded_demo_document(
    person_id: str,
    file: UploadFile = File(...),
    x_correlation_id: str | None = Header(default=None),
    _: str = Depends(require_basic_auth),
    db: Session = Depends(get_db),
):
    if file.content_type not in {"image/png", "image/jpeg"}:
        raise HTTPException(status_code=415, detail="Only PNG and JPEG files are allowed.")

    person = db.get(DemoPerson, person_id)

    if not person:
        raise HTTPException(status_code=404, detail="Demo person not found")

    correlation_id = correlation_id_from_header(x_correlation_id)
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    target = UPLOAD_DIR / safe_name

    content = await file.read()

    if len(content) > 5_000_000:
        raise HTTPException(status_code=413, detail="Maximum document size is 5 MB.")

    target.write_bytes(content)
    ocr_text = read_identity_document(str(target))

    decision = evaluate_identity(
        full_name=person.full_name,
        document_number=person.document_number,
        expires_on=person.expires_on,
        ocr_text=ocr_text,
    )

    application = VerificationApplication(
        person_id=person.id,
        status=decision.status,
        decision_reason=decision.reason,
        ocr_text=ocr_text,
        correlation_id=correlation_id,
    )
    db.add(application)
    db.commit()
    db.refresh(application)

    return VerificationResponse(
        application_id=application.id,
        status=application.status,
        decision_reason=application.decision_reason,
        correlation_id=correlation_id,
        created_at=application.created_at,
    )