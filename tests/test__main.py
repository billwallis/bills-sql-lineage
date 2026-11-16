import pathlib

import pytest

from sql_lineage import main


def test__main__can_parse_and_write_to_target__with_default_target_name(
    mock_datetime,
    tmp_path: pathlib.Path,
    sql_with_ctes: str,
    mermaid_with_ctes: str,
):
    mermaid_path = tmp_path / "test.mermaid"
    sql_path = tmp_path / "test.sql"
    sql_path.write_text(sql_with_ctes, encoding="utf-8")

    main.main([str(sql_path)])

    assert mermaid_path.exists()
    assert mermaid_path.read_text(encoding="utf-8") == mermaid_with_ctes


def test__main__can_parse_and_write_to_target__with_specified_target_name(
    mock_datetime,
    tmp_path: pathlib.Path,
    sql_with_ctes: str,
    mermaid_with_ctes: str,
):
    mermaid_path = tmp_path / "model.mermaid"
    sql_path = tmp_path / "test.sql"
    sql_path.write_text(sql_with_ctes, encoding="utf-8")

    main.main([str(sql_path), "--target", str(mermaid_path)])

    assert mermaid_path.exists()
    assert mermaid_path.read_text(encoding="utf-8") == mermaid_with_ctes


def test__main__throws_error__when_file_not_found(
    capsys: pytest.CaptureFixture,
):
    rc = main.main(["nonexistent.sql"])
    captured = capsys.readouterr()

    assert rc == 1
    assert captured.out == ""
    assert captured.err == "error: failed to generate graph for nonexistent.sql: File not found: nonexistent.sql\n"


def test__main__throws_error__when_there_is_some_value_error(
    capsys: pytest.CaptureFixture,
):
    tests_dir = pathlib.Path(__file__).parent
    rc = main.main([str(tests_dir)])
    captured = capsys.readouterr()

    assert rc == 1
    assert captured.out == ""
    assert captured.err == f"error: failed to generate graph for {tests_dir}: Not a file: {tests_dir}\n"
