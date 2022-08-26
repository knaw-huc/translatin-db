SELECT
	DISTINCT ON (
		FLOOR(EXTRACT(YEAR FROM m.earliest)/10)
	)
	FLOOR(EXTRACT(YEAR FROM m.earliest)/10)*10 AS "Decade",
	count(m.id) AS "# Manifestations"
FROM
	manifestations m
GROUP BY
	FLOOR(EXTRACT(YEAR FROM m.earliest)/10)
ORDER BY
	FLOOR(EXTRACT(YEAR FROM m.earliest)/10)

