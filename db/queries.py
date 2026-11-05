from .database import connect

def list_projects(query=''):
    with connect() as con:
        return con.execute('SELECT p.*,d.name AS developer_name,s.name AS status_name FROM projects p JOIN developers d ON d.id=p.developer_id JOIN statuses s ON s.id=p.status_id WHERE p.name LIKE ? ORDER BY p.deadline,p.id', ('%'+query+'%',)).fetchall()

def available_developers(on_date):
    with connect() as con:
        return con.execute('SELECT * FROM developers WHERE id NOT IN (SELECT developer_id FROM projects WHERE status_id<>3 AND deadline<=?)', (on_date,)).fetchall()

def statistics():
    with connect() as con:
        return con.execute('SELECT s.name,COUNT(p.id) AS total FROM statuses s LEFT JOIN projects p ON p.status_id=s.id GROUP BY s.id,s.name ORDER BY s.id').fetchall()
