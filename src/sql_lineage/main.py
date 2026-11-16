"""
An SQL lineage tool, built on the awesome SQLGlot library.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import pathlib
import sys
from collections.abc import Sequence

from sql_lineage import lineage


def _get_version() -> str:
    return f"bills-sql-lineage {importlib.metadata.version('bills-sql-lineage')}"


def _to_path(file_path: str, validate: bool = False) -> pathlib.Path:
    """
    Convert a file path to a pathlib.Path object.
    """

    path = pathlib.Path(file_path)
    if validate:
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")

    return path


def generate_lineage_graph(
    file: str,
    target: str | None = None,
    dialect: str | None = None,
) -> None:
    """
    Parse an SQL file into a Mermaid graph by tracing CTEs.

    :param file: The path to the SQL file to parse.
    :param target: The path to write the Mermaid graph to. If not provided,
        the graph will be written to a file with the same name as the input
        file, but with a ``.mermaid`` extension.
    :param dialect: The SQL dialect to use. If not provided, SQLGlot will
        attempt to infer the dialect.
    """

    file_path = _to_path(file, validate=True)
    target_path = (
        _to_path(target) if target else file_path.with_suffix(".mermaid")
    )

    sql = file_path.read_text(encoding="utf-8")
    mermaid = lineage.sql_to_mermaid(sql, dialect)

    target_path.write_text(mermaid, encoding="utf-8")
    # Switch to logging at some point
    print(f"Mermaid graph written to: {target_path.absolute()}")


def main(argv: Sequence[str] | None = None) -> int:
    """
    Parse the arguments and run the command.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version",
        action="version",
        version=_get_version(),
    )

    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--target", type=pathlib.Path)
    parser.add_argument("--dialect", type=str)

    args = parser.parse_args(argv)

    outcome = 0
    for filename in args.filenames:
        try:
            generate_lineage_graph(
                file=filename,
                target=args.target,
                dialect=args.dialect,
            )
        except Exception as err:
            print(
                f"error: failed to generate graph for {filename}: {err}",
                file=sys.stderr,
            )
            outcome |= 1

    return outcome


if __name__ == "__main__":
    raise SystemExit(main())  # pragma: no cover
