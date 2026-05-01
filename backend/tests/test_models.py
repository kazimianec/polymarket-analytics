import pytest
from pydantic import ValidationError

from app.models.responses.health import CheckResult, HealthResponse


def test_health_response_valid() -> None:
    """HealthResponse should accept all required fields."""
    model = HealthResponse(
        status="ok",
        app_name="fullstack-template",
        env="testing",
        runtime="local",
        checks={"database": CheckResult(status="ok")},
    )
    assert model.status == "ok"


def test_health_response_rejects_missing_field() -> None:
    """HealthResponse should raise ValidationError when required fields are absent."""
    with pytest.raises(ValidationError):
        HealthResponse()


def test_check_result_ok() -> None:
    """CheckResult should accept status ok with no detail."""
    check = CheckResult(status="ok")
    assert check.status == "ok"
    assert check.detail is None


def test_check_result_error_with_detail() -> None:
    """CheckResult should accept status error with a detail string."""
    check = CheckResult(status="error", detail="connection refused")
    assert check.status == "error"
    assert check.detail == "connection refused"
