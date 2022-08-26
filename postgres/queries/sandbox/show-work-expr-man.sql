SELECT
DISTINCT ON (
	substring(w.label, 2, length(w.label) - 1)::int,
	substring(e.label, 2, length(e.label) - 1)::int,
	substring(m.origin, 2, length(m.origin) - 1)::int,
	mt.title,
	mt.language,
	au.id
)
	w.label AS "Work",
	e.label AS "Expression",
	m.origin AS "Manifestation",
	substring(mt.title, 1, 50) AS "Title",
	mt.language AS "Lang",
	au.name AS "Author"
FROM
	works w
	JOIN work_expressions we ON (w.id = we.work_id)
	JOIN expression_manifestations em ON (em.expression_id = we.expression_id)
	JOIN expressions e ON (e.id = em.expression_id)
	JOIN manifestations m ON (m.id = em.manifestation_id)
	JOIN manifestation_titles mt ON (m.id = mt.manifestation_id)
	JOIN authors_manifestations am ON (m.id = am.manifestation_id)
	JOIN authors au ON (au.id = am.author_id)
ORDER BY
	substring(w.label, 2, length(w.label) - 1)::int,
	substring(e.label, 2, length(e.label) - 1)::int,
	substring(m.origin, 2, length(m.origin) - 1)::int,
	mt.title,
	mt.language,
	au.id
