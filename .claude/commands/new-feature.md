# New Feature

Scaffold a full vertical slice for a new backend feature named **$ARGUMENTS**.

## What to create

### 1. Router — `backend/src/app/routers/domain/<feature>.py`
- Thin router: only handle HTTP concerns (status codes, request/response models)
- Delegate all logic to the service
- Mount at `/api/v1/<feature>`
- Register the router in `backend/src/app/main.py`

### 2. Service — `backend/src/app/services/<feature>_service.py`
- All business logic lives here
- No FastAPI imports — plain Python only
- Full type hints on every function
- Google-style docstrings

### 3. Request models — `backend/src/app/models/requests/<feature>.py`
- Pydantic v2 models for POST/PUT request bodies
- Use `model_config = ConfigDict(strict=True)` where appropriate

### 4. Response models — `backend/src/app/models/responses/<feature>.py`
- Pydantic v2 models for API responses
- Include an ID field and timestamps where relevant

### 5. Tests — `backend/tests/test_<feature>.py`
- Use pytest with the FastAPI `TestClient`
- Cover: happy path, validation errors, not-found cases
- Use fixtures for repeated setup

## Conventions
- Follow the thin-router/fat-service pattern from CLAUDE.md
- Use `X | None` not `Optional[X]`, built-in generics (`list[str]`) not `typing`
- Never hardcode secrets or config — use dynaconf settings
