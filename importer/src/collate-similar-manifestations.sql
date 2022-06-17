SELECT *
FROM crosstab(
    $$
with main as (
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
                
    -- Titles: Alle talen van de Manifestation (ongeacht de zekerheid waarmee deze zijn vastgesteld) moeten overeenkomen. 
    -- De volgorde speelt hierbij geen rol geen rol.
    -- implementation:
    --   1) candidate1 and candidate2 must have equal number of titles;
    --   2) select all candidate1 titles;
    --   3) remove all candidate2 titles;
    --   4) answer: candidates match if result is empty
    AND (
        (select count(language) from manifestation_titles mt where mt.manifestation_id = am1.manifestation_id)
         = (select count(language) from manifestation_titles mt where mt.manifestation_id = am2.manifestation_id)
        AND NOT EXISTS (
            SELECT LANGUAGE
                FROM MANIFESTATION_TITLES MT
                WHERE MT.MANIFESTATION_ID = AM1.MANIFESTATION_ID
            EXCEPT SELECT LANGUAGE
                FROM MANIFESTATION_TITLES MT
                WHERE MT.MANIFESTATION_ID = AM2.MANIFESTATION_ID
        )
    )

    -- Compare levenshtein distance between titles.
    AND LENGTH(replace(replace(lower(MT1.TITLE), 'ij', 'y'), 'w', 'vv')) <= 255  -- levenshtein() only works on string length <= 255
    AND LENGTH(replace(replace(lower(MT2.TITLE), 'ij', 'y'), 'w', 'vv')) <= 255
    AND LEVENSHTEIN(
            translate(replace(replace(lower(MT1.TITLE), 'ij', 'y'), 'w', 'vv'), 'ju[]', 'iv'),
            translate(replace(replace(lower(MT2.TITLE), 'ij', 'y'), 'w', 'vv'), 'ju[]', 'iv')
        ) <= ROUND(GREATEST(LENGTH(MT1.TITLE), LENGTH(MT2.TITLE)) * 0.2)

    -- Form_type must match
    AND M1.FORM_TYPE = M2.FORM_TYPE
    
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
        
    -- No need to see each symmetrical pair (origin1,origin2) again as (origin2,origin1)
    -- e.g. from (M24,M31) and (M31,M24) only keep (M24,M31) based on 24 < 31
    AND (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int < (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int

ORDER BY
    -- order by origin, e.g. (string) "M2008": seen as (int) 2008 => so "M2008", "M700", "M37" is ordered: M37, M700, M2008
    (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int,  -- first origin1
    (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int   -- then origin2
)
select origin1, 'category_not_used', origin2
from main m1
where not exists (select from main where origin2 = m1.origin1)
    $$
) as ct(origin text,
    peer1  text, peer2  text, peer3  text, peer4  text, peer5  text,
    peer6  text, peer7  text, peer8  text, peer9  text, peer10 text,
    peer11 text, peer12 text, peer13 text, peer14 text, peer15 text,
    peer16 text, peer17 text, peer18 text, peer19 text, peer20 text,
    peer21 text, peer22 text, peer23 text, peer24 text, peer25 text
)
