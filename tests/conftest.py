import datetime
import pathlib
from typing import Any

import pytest

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def read_fixture(fixture_name: str) -> str:
    return pathlib.Path(FIXTURES / fixture_name).read_text(encoding="utf-8")


@pytest.fixture
def mock_datetime(monkeypatch):
    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls, **kwargs: Any) -> datetime.datetime:
            return datetime.datetime(2024, 1, 1)

    monkeypatch.setattr(datetime, "datetime", MockDatetime)


@pytest.fixture(
    scope="session",
    params=["mock-1", "mock-2"],
)
def sql_mermaid_pair(request: pytest.FixtureRequest) -> tuple[str, str]:
    sql = read_fixture(f"{request.param}.sql")
    mermaid = read_fixture(f"{request.param}.mermaid")
    return sql, mermaid
