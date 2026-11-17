import datetime
import pathlib
from typing import Any

import pytest

FIXTURES_PATH = pathlib.Path(__file__).parent / "fixtures"


def read_fixture(fixture_name: str) -> str:
    return pathlib.Path(FIXTURES_PATH / fixture_name).read_text(encoding="utf-8")


@pytest.fixture
def mock_datetime(monkeypatch):
    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls, **kwargs: Any) -> datetime.datetime:
            return datetime.datetime(2024, 1, 1)

    monkeypatch.setattr(datetime, "datetime", MockDatetime)


def _read_fixture_dir_names(root_dir: pathlib.Path) -> list[str]:
    return [path.name for path in root_dir.iterdir()]


@pytest.fixture(
    scope="session",
    params=_read_fixture_dir_names(FIXTURES_PATH),
)
def sql_mermaid_pair(request: pytest.FixtureRequest) -> tuple[str, str]:
    return (
        read_fixture(f"{request.param}/mock.sql"),
        read_fixture(f"{request.param}/mock.mermaid"),
    )
