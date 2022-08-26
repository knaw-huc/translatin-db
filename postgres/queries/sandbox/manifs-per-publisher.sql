SELECT DISTINCT	p.name AS "Publisher",
	count(m.id) AS "# Manifestations"
FROM
	manifestations m
	JOIN manifestations_publishers mp ON (mp.manifestation_id = m.id)
	JOIN publishers p ON (mp.publisher_id = p.id)
GROUP BY p.name
ORDER BY "# Manifestations" DESC
