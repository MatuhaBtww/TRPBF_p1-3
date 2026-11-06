"""Проверка учебных SQL-запросов через sqlite3 и SQLite CLI."""

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from .database import DATABASE, BASE_DIR, connect


def verify(database=DATABASE, cli=None):
    sql = "\n".join(
        line
        for line in (BASE_DIR / "sql/queries.sql")
        .read_text(encoding="utf-8")
        .splitlines()
        if not line.lstrip().startswith("--")
    )
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    results = []
    with connect(database) as con:
        assert con.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert not con.execute("PRAGMA foreign_key_check").fetchall()
        for number, statement in enumerate(statements, 1):
            rows = [dict(row) for row in con.execute(statement)]
            if cli:
                location = Path(database).resolve()
                result = subprocess.run(
                    [cli, "-json", location.name, statement],
                    cwd=location.parent,
                    check=True,
                    capture_output=True,
                )
                actual = (
                    json.loads(result.stdout.decode("utf-8"))
                    if result.stdout.strip()
                    else []
                )
                if actual != rows:
                    raise ValueError(
                        f"SQL {number}: результаты Python и CLI различаются"
                    )
            results.append({"query": number, "rows": rows})
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DATABASE)
    parser.add_argument("--cli", default=shutil.which("sqlite3"))
    args = parser.parse_args()
    if not args.cli:
        parser.error("SQLite CLI не найден. Укажите --cli с путем к sqlite3.exe")
    print(
        json.dumps(
            {"sqlite_cli": args.cli, "results": verify(args.database, args.cli)},
            ensure_ascii=False,
            indent=2,
        )
    )
