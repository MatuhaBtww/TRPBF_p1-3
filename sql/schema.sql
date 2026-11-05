PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS developers(id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name))>0));
CREATE TABLE IF NOT EXISTS technologies(id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name))>0));
CREATE TABLE IF NOT EXISTS statuses(id INTEGER PRIMARY KEY CHECK(id IN (1,2,3)), name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS projects(id INTEGER PRIMARY KEY, name TEXT NOT NULL CHECK(length(trim(name))>0), developer_id INTEGER NOT NULL REFERENCES developers(id) ON DELETE RESTRICT, status_id INTEGER NOT NULL REFERENCES statuses(id) ON DELETE RESTRICT, deadline TEXT NOT NULL CHECK(date(deadline) IS NOT NULL));
CREATE TABLE IF NOT EXISTS project_technologies(project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE, technology_id INTEGER NOT NULL REFERENCES technologies(id) ON DELETE RESTRICT, PRIMARY KEY(project_id, technology_id));
