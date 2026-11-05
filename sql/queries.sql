-- 1 WHERE: запланированные проекты
SELECT * FROM projects WHERE status_id=1;
-- 2 WHERE: проекты к контрольной дате
SELECT * FROM projects WHERE deadline<'2026-12-01' ORDER BY deadline,id;
-- 3 JOIN: проект и ответственный
SELECT p.name,d.name AS developer FROM projects p JOIN developers d ON d.id=p.developer_id;
-- 4 JOIN: проект и технологии
SELECT p.name,t.name AS technology FROM projects p JOIN project_technologies pt ON p.id=pt.project_id JOIN technologies t ON t.id=pt.technology_id;
-- 5 агрегат: число проектов
SELECT COUNT(*) AS total FROM projects;
-- 6 агрегат: крайние сроки
SELECT MIN(deadline) AS first_deadline,MAX(deadline) AS last_deadline FROM projects;
-- 7 GROUP BY: статистика по статусам с нулевыми группами
SELECT s.name,COUNT(p.id) AS total FROM statuses s LEFT JOIN projects p ON p.status_id=s.id GROUP BY s.id,s.name;
-- 8 GROUP BY HAVING: разработчики с проектами
SELECT d.name,COUNT(p.id) AS total FROM developers d LEFT JOIN projects p ON p.developer_id=d.id GROUP BY d.id,d.name HAVING COUNT(p.id)>0;
-- 9 подзапрос: разработчики без незавершенных проектов на контрольную дату
SELECT * FROM developers WHERE id NOT IN (SELECT developer_id FROM projects WHERE status_id<>3 AND deadline<='2026-12-20');
-- 10 LIMIT OFFSET: первая страница проектов
SELECT id,name,deadline FROM projects ORDER BY deadline,id LIMIT 5 OFFSET 0;
-- 11 две проверки AND
SELECT * FROM projects WHERE status_id<>3 AND deadline<'2026-11-06';
-- 12 группировка по технологиям
SELECT t.name,COUNT(pt.project_id) AS total FROM technologies t LEFT JOIN project_technologies pt ON t.id=pt.technology_id GROUP BY t.id,t.name;
