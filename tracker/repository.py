from service import decode
from db.database import connect


def state():
    with connect() as con:
        data = {
            kind: [dict(r) for r in con.execute(f"SELECT * FROM {kind}")]
            for kind in ("developers", "technologies", "statuses")
        }
        data["projects"] = []
        for row in con.execute("SELECT * FROM projects"):
            p = dict(row)
            p["technology_ids"] = [
                r[0]
                for r in con.execute(
                    "SELECT technology_id FROM project_technologies WHERE project_id=?",
                    (p["id"],),
                )
            ]
            data["projects"].append(p)
    return decode(data)
