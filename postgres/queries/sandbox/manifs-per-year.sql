SELECT
	DISTINCT EXTRACT(YEAR FROM m.earliest) AS "Year",
	count(m.id) AS "# Manifestations"
FROM
	manifestations m
GROUP BY
	EXTRACT(YEAR FROM m.earliest)
ORDER BY
	EXTRACT(YEAR FROM m.earliest)

