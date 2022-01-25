Zou je, als opmaat naar de realisatie van het Expression-niveau, eens een query
kunnen schrijven die nagaat welke records:
 1) exact dezelfde auteur hebben, bij meer auteurs: ten minste één auteur "overlap";
 2) exact hetzelfde jaar van uitgave hebben (of indien er sprake is van een periode: overlapping qua periodisering met elkaar);
 3) min of meer dezelfde titel hebben (ik weet niet of je met Levenshtein-distance of Soundex kunt werken, maar in dat geval bijvoorbeeld een waarde van 0.9). Mocht dit laatste matchingscriterium lastig worden in SQL (wat ik me kan voorstellen), dan is exacte matching op titel ook goed.

Deze query zou moeten bepalen of er nog dubbele registraties in het Manifestations-bestand staan.

## Uiteindelijke query
```sql
SELECT AU.NAME AUTHOR,
	M1.ORIGIN ORIGIN1,
	M1.EARLIEST EARLIEST1,
	TO_TIMESTAMP((EXTRACT(EPOCH FROM M1.EARLIEST) + EXTRACT(EPOCH FROM M1.LATEST)) / 2)::date AVG1,
	M1.LATEST LATEST1,
	MT1.TITLE TITLE1,
	M2.ORIGIN ORIGIN2,
	M2.EARLIEST EARLIEST2,
	TO_TIMESTAMP((EXTRACT(EPOCH FROM M2.EARLIEST) + EXTRACT(EPOCH FROM M2.LATEST)) / 2)::date AVG2,
	M2.LATEST LATEST2,
	MT2.TITLE TITLE2,
	LEVENSHTEIN(MT1.TITLE, MT2.TITLE) LEVENSHTEIN
FROM AUTHORS_MANIFESTATIONS AM1,
	AUTHORS_MANIFESTATIONS AM2,
	AUTHORS AU,
	MANIFESTATIONS M1,
	MANIFESTATIONS M2,
	MANIFESTATION_TITLES MT1,
	MANIFESTATION_TITLES MT2
WHERE
	-- Various table joins
	AU.ID = AM1.AUTHOR_ID
	AND M1.ID = AM1.MANIFESTATION_ID
	AND M2.ID = AM2.MANIFESTATION_ID
	AND MT1.MANIFESTATION_ID = M1.ID
	AND MT2.MANIFESTATION_ID = M2.ID

	-- Find the same authors for different manifestations
	AND AM1.AUTHOR_ID = AM2.AUTHOR_ID
	AND AM1.MANIFESTATION_ID <> AM2.MANIFESTATION_ID

	-- Compare manifestation dates for overlap / equality / inclusion.
	-- Implemented as follows:
	--   * either the average of m1's earliest/latest lies between m2's earliest and latest;
	--   * or the other way around: avg of m2's earliest/latest lies between m1's earliest and latest.
	--
	-- Uses TO_TIMESTAMP, and EXTRACT EPOCH to convert between date and epoch value for averaging.
	AND (
		TO_TIMESTAMP((EXTRACT(EPOCH FROM M1.EARLIEST) + EXTRACT(EPOCH FROM M1.LATEST)) / 2)::date BETWEEN M2.EARLIEST AND M2.LATEST
	 OR TO_TIMESTAMP((EXTRACT(EPOCH FROM M2.EARLIEST) + EXTRACT(EPOCH FROM M2.LATEST)) / 2)::date BETWEEN M1.EARLIEST AND M1.LATEST
	)

	-- Compare levenshtein distance between titles.
	AND LENGTH(MT1.TITLE) <= 255  -- levenshtein() only works on string length <= 255
	AND LENGTH(MT2.TITLE) <= 255
	AND LEVENSHTEIN(MT1.TITLE, MT2.TITLE) <= ROUND(GREATEST(LENGTH(MT1.TITLE), LENGTH(MT2.TITLE)) * 0.1)

	-- No need to see each symmetrical pair (origin1,origin2) again as (origin2,origin1)
	-- e.g. from (M24,M31) and (M31,M24) only keep (M24,M31) based on 24 < 31
	AND (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int < (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int

ORDER BY AUTHOR,
	-- order by origin, e.g. (string) "M2008": seen as (int) 2008 => so "M2008", "M700", "M37" is ordered: M37, M700, M2008
	(SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int,  -- first origin1
	(SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int   -- then origin2
```

## Welke titels lijken op elkaar
```sql
SELECT LEVENSHTEIN(MT1.TITLE, MT2.TITLE) DIST,
	MAN1.ORIGIN MAN1,
	REGEXP_REPLACE(MT1.TITLE, ' $', '▫') T1,
	MT1.LANGUAGE,
	MAN2.ORIGIN MAN2,
	REGEXP_REPLACE(MT2.TITLE, ' $', '▫') T2,
	MT2.LANGUAGE,
	ROUND(GREATEST(LENGTH(MT1.TITLE),LENGTH(MT2.TITLE)) * 0.1) MAX_DIST
FROM MANIFESTATION_TITLES MT1,
	MANIFESTATION_TITLES MT2,
	MANIFESTATIONS MAN1,
	MANIFESTATIONS MAN2
WHERE MT1.MANIFESTATION_ID <> MT2.MANIFESTATION_ID
	AND MT1.TITLE <> MT2.TITLE
	AND LENGTH(MT1.TITLE) <= 255  -- unfortunately levenshtein() only works on string length <= 255
	AND LENGTH(MT2.TITLE) <= 255
	AND LEVENSHTEIN(MT1.TITLE,MT2.TITLE) <= ROUND(GREATEST(LENGTH(MT1.TITLE),LENGTH(MT2.TITLE)) * 0.1)
	AND MAN1.ID = MT1.MANIFESTATION_ID
	AND MAN2.ID = MT2.MANIFESTATION_ID
	AND (SUBSTRING(MAN1.ORIGIN, 2, LENGTH(MAN1.ORIGIN)-1))::int < (SUBSTRING(MAN2.ORIGIN, 2, LENGTH(MAN2.ORIGIN)-1))::int
ORDER BY T1, (SUBSTRING(MAN1.ORIGIN, 2, LENGTH(MAN1.ORIGIN)-1))::int
```

We zien dat er enkele titels eindigen op een spatie, bijv. `M917` "Menecrates" (Latin) versus `M832` "Menecrates " (French).

Laten we dat eerst uitzoeken en verbeteren.

### Welke titel (in welke taal) heeft een ' ' (spatie) aan het einde:
```sql
SELECT MAN.ORIGIN,
	MT.LANGUAGE,
	regexp_replace(MT.title, ' $', '▫')
FROM MANIFESTATIONS MAN,
	MANIFESTATION_TITLES MT
WHERE MAN.ID = MT.MANIFESTATION_ID
	AND RIGHT(MT.TITLE, 1) = ' '
ORDER BY (SUBSTRING(MAN.ORIGIN, 2, LENGTH(MAN.ORIGIN) - 1))::int
```
