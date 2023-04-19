SELECT
    M.origin AS "Manifestation ID",
    MT.title AS "Title",
    M.earliest AS "Earliest",
    M.latest AS "Latest",
    MT.language AS "Lang",
    A.name AS "Author"
FROM
    manifestations M
    JOIN manifestation_titles MT ON (MT.manifestation_id = M.id)
    JOIN authors_manifestations AM ON (AM.manifestation_id = M.id)
    JOIN authors A ON (AM.author_id = A.id)
WHERE
    M.has_dramaweb_scan OR M.has_dramaweb_transcription
ORDER BY
    MT.title,
    M.earliest,
    M.latest,
    M.origin
