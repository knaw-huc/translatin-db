# Find out if there are any reprints before First printing

Bij het zoeken naar Expressions gegeven Manifestations, selecteren we expliciet op
dat een 'Reprint' nooit vóór een 'First printing' kan komen.

Om de data nog eens extra onder de loep te nemen, zou het handig zijn om te weten
of er manifestations zijn die verder wél aan alle andere criteria voldoen, maar
waarbij juist een 'Reprint' voor de 'First printing' komt.

```sql
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

    -- Compare levenshtein distance between titles.
    AND LENGTH(MT1.TITLE) <= 255  -- levenshtein() only works on string length <= 255
    AND LENGTH(MT2.TITLE) <= 255
    AND LEVENSHTEIN(MT1.TITLE, MT2.TITLE) <=
        ROUND(GREATEST(LENGTH(MT1.TITLE), LENGTH(MT2.TITLE)) * 0.2)

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

    -- Candidate manifestations must be <= 25 years from each other.
    -- implementation:
    --   1) get average of (earliest,latest) year for both candidates;
    --   2) subtract to get the 'distance' between candidates;
    --   3) check if <= 25 years (depending on which candidate was earliest).
    AND (
        (EXTRACT(YEAR FROM M1.EARLIEST) + EXTRACT(YEAR FROM M1.LATEST)) / 2 -
        (EXTRACT(YEAR FROM M2.EARLIEST) + EXTRACT(YEAR FROM M2.LATEST)) / 2
        BETWEEN -25 AND 25
    )

    -- Find 'Reprint's that actually occur BEFORE their 'First Printing'
    AND (
        (M1.FORM = 'Reprint' AND M2.FORM = 'First Printing'
        AND ((EXTRACT(YEAR FROM M1.EARLIEST) + EXTRACT(YEAR FROM M1.LATEST)) / 2 < (EXTRACT(YEAR FROM M2.EARLIEST) + EXTRACT(YEAR FROM M2.LATEST)) / 2))
        OR
        (M2.FORM = 'Reprint' AND M1.FORM = 'First Printing'
        AND ((EXTRACT(YEAR FROM M2.EARLIEST) + EXTRACT(YEAR FROM M2.LATEST)) / 2 < (EXTRACT(YEAR FROM M1.EARLIEST) + EXTRACT(YEAR FROM M1.LATEST)) / 2))
    )
    
    -- No need to see each symmetrical pair (origin1,origin2) again as (origin2,origin1)
    -- e.g. from (M24,M31) and (M31,M24) only keep (M24,M31) based on 24 < 31
    AND (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int <
        (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int

ORDER BY
    -- order by origin, e.g. (string) "M2008": seen as (int) 2008 => so "M2008", "M700", "M37" is ordered: M37, M700, M2008
    (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int,  -- first origin1
    (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int   -- then origin2
```
