# Vind vergelijkbare titels

Het zou kunnen voorkomen dat titels als 'Jozef' soms ook in een veel langere vorm voorkomen (denk aan 'tocht van Jozef uit ...' etc.
Titels zijn vergelijkbaar als:

- de korte titel in de lange voorkomt;
- daarbij normalisatie van beide titels ivm latijn:
    - lowercase
    - j == i
    - v == u

```sql
SELECT *
FROM crosstab(
	$$
WITH results AS(
WITH main AS(
SELECT
    -- stuff related to first candidate
    M1.ORIGIN ORIGIN1,
    M1.FORM FORM1,
    M1.GENRE GENRE1,
    M1.SUBGENRE SUBGENRE1,
    M1.EARLIEST EARLIEST1,
    M1.LATEST LATEST1,
    MT1.TITLE TITLE1,
    MT1.LANGUAGE LANG1,
    MT1.CERTAINTY CERTAIN1,

    -- stuff related to second candidate
    M2.ORIGIN ORIGIN2,
    M2.FORM FORM2,
    M2.GENRE GENRE2,
    M2.SUBGENRE SUBGENRE2,
    M2.EARLIEST EARLIEST2,
    M2.LATEST LATEST2,
    MT2.TITLE TITLE2,
    MT2.LANGUAGE LANG2,
    MT2.CERTAINTY CERTAIN2

FROM
    AUTHORS_MANIFESTATIONS AM1
    JOIN MANIFESTATIONS M1 ON (M1.ID = AM1.MANIFESTATION_ID)
    JOIN MANIFESTATION_TITLES MT1 ON (M1.ID = MT1.MANIFESTATION_ID),

    AUTHORS_MANIFESTATIONS AM2
    JOIN MANIFESTATIONS M2 ON (M2.ID = AM2.MANIFESTATION_ID)
    JOIN MANIFESTATION_TITLES MT2 ON (M2.ID = MT2.MANIFESTATION_ID)

WHERE
    -- Find different manifestation candidates
    AM1.MANIFESTATION_ID <> AM2.MANIFESTATION_ID

    -- All candidate1 authors MUST be present as candidate2 authors, however candidate2 MAY have more authors.
    -- implementation:
    --   1) select all candidate1 authors;
    --   2) remove all candidate2 authors from this set;
    --   3) answer: candidates are a match if result is empty.
    AND NOT EXISTS (
        SELECT AUTHOR_ID
            FROM AUTHORS_MANIFESTATIONS AM
            WHERE AM.MANIFESTATION_ID = AM1.MANIFESTATION_ID
        EXCEPT SELECT AUTHOR_ID
            FROM AUTHORS_MANIFESTATIONS AM
            WHERE AM.MANIFESTATION_ID = AM2.MANIFESTATION_ID
    )

    -- Titles: all titles with Certain language of candidate1 MUST either exist for candidate2, or be Uncertain.
    -- implementation:
    --   1) select all candidate1 titles with Certain language;
    --   2) remove all candidate2 titles which are equal, OR with Uncertain language;
    --   3) answer: candidates are a match if result is empty.
    AND NOT EXISTS (
        SELECT LANGUAGE
            FROM MANIFESTATION_TITLES MT
            WHERE MT.MANIFESTATION_ID = AM1.MANIFESTATION_ID
            AND MT1.CERTAINTY = 'Certain'
        EXCEPT SELECT LANGUAGE
            FROM MANIFESTATION_TITLES MT
            WHERE MT.MANIFESTATION_ID = AM2.MANIFESTATION_ID
            AND (
                MT.LANGUAGE = MT2.LANGUAGE
                OR MT.CERTAINTY = 'Uncertain'
            )
    )

    -- find equal titles, and substrings, after normalisation
    AND LENGTH(MT1.TITLE) > 3  -- ignore 'Asa' and 'Dos'
    AND LENGTH(MT1.TITLE) <= LENGTH(MT2.TITLE)
    AND POSITION(
        TRANSLATE(LOWER(MT1.TITLE), 'jv', 'iu')
        in TRANSLATE(LOWER(MT2.TITLE), 'jv', 'iu')
    ) > 0

    -- Form_type must match
    AND M1.FORM_TYPE = M2.FORM_TYPE

    -- Form: "First printing" can never match another "First printing"
    AND NOT (
        M1.FORM = 'First Printing'
        AND M2.FORM = 'First Printing'
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

    -- A 'Reprint' can never occur before a 'First Printing'
    AND (  -- either M1 <= M2, or M1 ≠ 'First Printing', or M2 ≠ 'Reprint'
        ((EXTRACT(YEAR FROM M1.EARLIEST) + EXTRACT(YEAR FROM M1.LATEST)) / 2 <=
         (EXTRACT(YEAR FROM M2.EARLIEST) + EXTRACT(YEAR FROM M2.LATEST)) / 2)
        OR M1.FORM <> 'First Printing'
        OR M2.FORM <> 'Reprint'
    )
    AND (  -- similarly for M2 <= M1
        ((EXTRACT(YEAR FROM M2.EARLIEST) + EXTRACT(YEAR FROM M2.LATEST)) / 2 <=
         (EXTRACT(YEAR FROM M1.EARLIEST) + EXTRACT(YEAR FROM M1.LATEST)) / 2)
        OR M2.FORM <> 'First Printing'
        OR M1.FORM <> 'Reprint'
    )

ORDER BY
    -- order by origin, e.g. (string) "M2008": seen as (int) 2008 => so "M2008", "M700", "M37" is ordered: M37, M700, M2008
    SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1)::int,  -- first origin1
    SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1)::int   -- then origin2
)
SELECT *
FROM main m1
WHERE
    (SUBSTRING(ORIGIN1, 2, LENGTH(ORIGIN1)-1)::int < SUBSTRING(ORIGIN2, 2, LENGTH(ORIGIN2)-1)::int)
    OR NOT EXISTS (SELECT FROM main m2 WHERE m2.origin2 = m1.origin1 AND m2.origin1 = m1.origin2)
)
SELECT origin1, 'category_not_used', origin2
FROM results r1
WHERE NOT EXISTS (SELECT FROM results WHERE origin2 = r1.origin1)
$$
)
AS ct(origin text,
    peer1  text, peer2  text, peer3  text, peer4  text, peer5  text, peer6  text, peer7  text,
    peer8  text, peer9  text, peer10 text, peer11 text, peer12 text, peer13 text, peer14 text,
    peer15 text, peer16 text, peer17 text, peer18 text, peer19 text, peer20 text, peer21 text
)
```
