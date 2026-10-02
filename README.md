# Identity Flow Demo

A local, fictional identity-verification workflow built for learning and interview demonstration.

## Safety scope

- Uses three fictional identities only.
- Generates documents marked `DEMO ONLY — NOT A REAL ID`.
- Does not perform biometric matching, liveness detection, KYC, AML screening, or production identity verification.
- Must not be used with real passports, national IDs, residence permits, selfies, or personal data.

## Architecture

Client → FastAPI Basic Auth → OCR/rule decision → PostgreSQL audit/outbox → HMAC-signed webhook → Node.js receiver.

A separate Node.js/TypeScript MCP server exposes narrow read-only tools over fictional records.

## Components

- `api/`: Python FastAPI identity workflow and OCR
- `receiver/`: Node.js webhook consumer with HMAC verification and event idempotency
- `mcp-server/`: TypeScript MCP server with read-only demo tools
- `terraform/`: Local Docker infrastructure provisioned with Terraform
- `.gitlab-ci.yml`: CI validation, tests, container build and Terraform validation
- `scripts/`: Dummy-card generator and smoke test

## Reliability and security choices

- Basic Auth for local demo only
- Input type and file-size validation
- Correlation IDs
- HMAC webhook signature verification
- Event-ID-based idempotency at webhook consumer
- Outbox persistence and delivery attempts
- Structured service logs
- Docker image build reproducibility
- Terraform plan/validate workflow
- No real PII in demo data

## Run

```bash
cp .env.example .env
docker compose up --build
```

Then visit:

- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health
- Receiver health: http://localhost:3001/health