SELECT DISTINCT
	a.name AS "Author",
	p.name AS "Publisher",
	count(*) AS "# samenwerkingen"
FROM
	authors a
	JOIN authors_manifestations am ON (am.author_id = a.id)
	JOIN manifestations_publishers mp ON (mp.manifestation_id = am.manifestation_id)
	JOIN publishers p ON (mp.publisher_id = p.id)
GROUP BY
	a.name,
	p.name
ORDER BY
	"# samenwerkingen" DESC
