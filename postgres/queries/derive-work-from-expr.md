```sql
SELECT
	-- stuff from expression 1
	E1.LABEL LABEL1,
	M1.ORIGIN ORIGIN1,
	MT1.TITLE TITLE1,
	M1.GENRE G1,
	M1.SUBGENRE GS1,
	AU1.NAME AUTHOR1,
	
	-- stuff from expression 2
	E2.LABEL LABEL2,
	M2.ORIGIN ORIGIN2,
	MT2.TITLE TITLE2,
	M2.GENRE G2,
	M2.SUBGENRE GS2,
	AU2.NAME AUTHOR2
FROM
	EXPRESSIONS E1
	JOIN EXPRESSION_MANIFESTATIONS EM1 ON (EM1.EXPRESSION_ID = E1.ID)
	JOIN MANIFESTATIONS M1 ON (EM1.MANIFESTATION_ID = M1.ID)
	JOIN MANIFESTATION_TITLES MT1 ON (MT1.MANIFESTATION_ID = M1.ID)
	JOIN AUTHORS_MANIFESTATIONS AM1 ON (AM1.MANIFESTATION_ID = M1.ID)
	JOIN AUTHORS AU1 ON (AM1.AUTHOR_ID = AU1.ID),
	
	EXPRESSIONS E2
	JOIN EXPRESSION_MANIFESTATIONS EM2 ON (EM2.EXPRESSION_ID = E2.ID)
	JOIN MANIFESTATIONS M2 ON (EM2.MANIFESTATION_ID = M2.ID)
	JOIN MANIFESTATION_TITLES MT2 ON (MT2.MANIFESTATION_ID = M2.ID)
	JOIN AUTHORS_MANIFESTATIONS AM2 ON (AM2.MANIFESTATION_ID = M2.ID)
	JOIN AUTHORS AU2 ON (AM2.AUTHOR_ID = AU2.ID)
	
WHERE
	-- Find different Expression candidates
	E1.ID <> E2.ID
	
	-- All authors involved in both E1 and E2 candidates must match:
	--   1) E1 and E2 must have equal (distinct) author counts;
	--   2) The set of distinct authors in E1 minus the set of distinct authors in E2 must be empty.
	AND (
		(select count(distinct am.author_id)
		 	from authors_manifestations am join expression_manifestations em on (em.manifestation_id = am.manifestation_id)
		 	where em.expression_id = e1.id)
		= (select count(distinct am.author_id)
			from authors_manifestations am join expression_manifestations em on (em.manifestation_id = am.manifestation_id)
			where em.expression_id = e2.id)
		AND NOT EXISTS (
			select distinct author_id
				from authors_manifestations am join expression_manifestations em on (em.manifestation_id = am.manifestation_id)
				where em.expression_id = e1.id
			except select distinct author_id
				from authors_manifestations am join expression_manifestations em on (em.manifestation_id = am.manifestation_id)
				where em.expression_id = e2.id
		)
	)
	
	-- Genre must match, if it exists
	AND (
		M1.GENRE = M2.GENRE
		OR M1.GENRE IS NULL
		OR M2.GENRE IS NULL
	)
	
	-- Subgenre must match, if it exists
	AND (
		M1.SUBGENRE = M2.SUBGENRE
		OR M1.SUBGENRE IS NULL
		OR M2.SUBGENRE IS NULL
	)
	
	-- Compare levenshtein distance between titles.
	AND LENGTH(replace(replace(lower(MT1.TITLE), 'ij', 'y'), 'w', 'vv')) <= 255  -- levenshtein() only works on string length <= 255
	AND LENGTH(replace(replace(lower(MT2.TITLE), 'ij', 'y'), 'w', 'vv')) <= 255
	AND LEVENSHTEIN(
			translate(replace(replace(lower(MT1.TITLE), 'ij', 'y'), 'w', 'vv'), 'ju[]', 'iv'),
			translate(replace(replace(lower(MT2.TITLE), 'ij', 'y'), 'w', 'vv'), 'ju[]', 'iv')
	) <= ROUND(GREATEST(LENGTH(MT1.TITLE), LENGTH(MT2.TITLE)) * 0.2)

ORDER BY
	(SUBSTRING(E1.LABEL, 2, LENGTH(E1.LABEL)-1))::int,
	(SUBSTRING(E2.LABEL, 2, LENGTH(E2.LABEL)-1))::int,
	(SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int,
	(SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int
```
