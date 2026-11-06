from pathlib import Path
import argparse
from service import decode, encode
from storage import read_json
from .database import BASE_DIR, DATABASE, connect


def import_data(source, destination=DATABASE):
    data = encode(decode(read_json(Path(source))))
    with connect(destination) as con:
        con.executescript((BASE_DIR / "sql/schema.sql").read_text(encoding="utf-8"))
        if con.execute("SELECT COUNT(*) FROM projects").fetchone()[0]:
            raise ValueError("База уже содержит проекты; импорт отменен без перезаписи")
        for kind in ("developers", "technologies", "statuses"):
            con.executemany(
                f"INSERT INTO {kind}(id,name) VALUES (?,?)",
                [(r["id"], r["name"]) for r in data[kind]],
            )
        for p in data["projects"]:
            con.execute(
                "INSERT INTO projects VALUES (?,?,?,?,?)",
                (p["id"], p["name"], p["developer_id"], p["status_id"], p["deadline"]),
            )
            con.executemany(
                "INSERT INTO project_technologies VALUES (?,?)",
                [(p["id"], t) for t in p["technology_ids"]],
            )
        return {
            kind: con.execute(f"SELECT COUNT(*) FROM {kind}").fetchone()[0]
            for kind in data
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(BASE_DIR / "data" / "seed.json"))
    parser.add_argument("--database", default=str(DATABASE))
    args = parser.parse_args()
    print(import_data(args.source, args.database))
