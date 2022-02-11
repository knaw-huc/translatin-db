Zou je, als opmaat naar de realisatie van het Expression-niveau, eens een query
kunnen schrijven die nagaat welke records:
 1) exact dezelfde auteur hebben, bij meer auteurs: ten minste één auteur "overlap";
 2) exact hetzelfde jaar van uitgave hebben (of indien er sprake is van een periode: overlapping qua periodisering met elkaar);
 3) min of meer dezelfde titel hebben (ik weet niet of je met Levenshtein-distance of Soundex kunt werken, maar in dat geval bijvoorbeeld een waarde van 0.9). Mocht dit laatste matchingscriterium lastig worden in SQL (wat ik me kan voorstellen), dan is exacte matching op titel ook goed.

Deze query zou moeten bepalen of er nog dubbele registraties in het Manifestations-bestand staan.

```sql
SELECT
    -- author name who worked on both candidates
    AUTHOR.NAME AUTHOR,

    -- stuff related to first candidate
    M1.ORIGIN ORIGIN1,
    M1.FORM FORM1,
    M1.EARLIEST EARLIEST1,
    M1.LATEST LATEST1,
    MT1.TITLE TITLE1,
    MT1.LANGUAGE LANG1,
    MT1.CERTAINTY CERTAIN1,
    PUB1.NAME PUB1,

    -- stuff related to second candidate
    M2.ORIGIN ORIGIN2,
    M2.FORM FORM2,
    M2.EARLIEST EARLIEST2,
    M2.LATEST LATEST2,
    MT2.TITLE TITLE2,
    MT2.LANGUAGE LANG2,
    MT2.CERTAINTY CERTAIN2,
    PUB2.NAME PUB2,

    -- distance between the two titles
    LEVENSHTEIN(MT1.TITLE, MT2.TITLE) LEVENSHTEIN

FROM
    AUTHORS_MANIFESTATIONS AM1
    JOIN AUTHORS AUTHOR ON (AUTHOR.ID = AM1.AUTHOR_ID)
    JOIN MANIFESTATIONS M1 ON (M1.ID = AM1.MANIFESTATION_ID)
    JOIN MANIFESTATION_TITLES MT1 ON (M1.ID = MT1.MANIFESTATION_ID)
    LEFT JOIN MANIFESTATIONS_PUBLISHERS MP1 ON (M1.ID = MP1.MANIFESTATION_ID)
    LEFT JOIN PUBLISHERS PUB1 ON (PUB1.ID = MP1.PUBLISHER_ID),

    AUTHORS_MANIFESTATIONS AM2
    JOIN MANIFESTATIONS M2 ON (M2.ID = AM2.MANIFESTATION_ID)
    JOIN MANIFESTATION_TITLES MT2 ON (M2.ID = MT2.MANIFESTATION_ID)
    LEFT JOIN MANIFESTATIONS_PUBLISHERS MP2 ON (M2.ID = MP2.MANIFESTATION_ID)
    LEFT JOIN PUBLISHERS PUB2 ON (PUB2.ID = MP2.PUBLISHER_ID)

WHERE
    -- Find the same authors for different manifestations
    AM1.AUTHOR_ID = AM2.AUTHOR_ID
    AND AM1.MANIFESTATION_ID <> AM2.MANIFESTATION_ID

    -- If publisher(s) are known, they must be equal, if multiple there must be overlap
    AND (
        MP1.PUBLISHER_ID = MP2.PUBLISHER_ID
        OR MP1.PUBLISHER_ID IS NULL
        OR MP2.PUBLISHER_ID IS NULL
    )

    -- Compare manifestation dates for overlap / equality / inclusion.
    -- Implemented as follows:
    --   * either the average of m1's earliest/latest lies between m2's earliest and latest;
    --   * or the other way around: avg of m2's earliest/latest lies between m1's earliest and latest.
    -- Uses TO_TIMESTAMP, and EXTRACT EPOCH to convert between date and epoch value for averaging.
    AND (
        TO_TIMESTAMP((EXTRACT(EPOCH FROM M1.EARLIEST) + EXTRACT(EPOCH FROM M1.LATEST)) / 2)::date BETWEEN M2.EARLIEST AND M2.LATEST
     OR TO_TIMESTAMP((EXTRACT(EPOCH FROM M2.EARLIEST) + EXTRACT(EPOCH FROM M2.LATEST)) / 2)::date BETWEEN M1.EARLIEST AND M1.LATEST
    )

    -- Edition (Form) must be equal.
    -- Sometimes it is unknown whether a Synopsis was a manuscript or printed, in
    -- which case the form was set to 'Synopsis'. Therefore Synopsis should be
    -- treated equal to both 'Synopsis (manuscript)' and 'Synopsis (printed)'
    AND (
        M1.FORM = M2.FORM
        OR (M1.FORM = 'Synopsis' AND M2.FORM in ('Synopsis (manuscript)', 'Synopsis (printed)'))
        OR (M2.FORM = 'Synopsis' AND M1.FORM in ('Synopsis (manuscript)', 'Synopsis (printed)'))
    )

    -- Titles must be in the same language, or uncertain (either one 'uncertain' is enough)
    AND (
        MT1.LANGUAGE = MT2.LANGUAGE
        OR MT1.CERTAINTY = 'Uncertain'
        OR MT2.CERTAINTY = 'Uncertain'
    )

    -- Compare levenshtein distance between titles.
    AND LENGTH(MT1.TITLE) <= 255  -- levenshtein() only works on string length <= 255
    AND LENGTH(MT2.TITLE) <= 255
    AND LEVENSHTEIN(MT1.TITLE, MT2.TITLE) <= ROUND(GREATEST(LENGTH(MT1.TITLE), LENGTH(MT2.TITLE)) * 0.1)

    -- No need to see each symmetrical pair (origin1,origin2) again as (origin2,origin1)
    -- e.g. from (M24,M31) and (M31,M24) only keep (M24,M31) based on 24 < 31
    AND (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int < (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int

ORDER BY
    -- Order first by Author, then by some sensible "lower number entries go first" based off of candidate's "Origin"
    AUTHOR,
    -- order by origin, e.g. (string) "M2008": seen as (int) 2008 => so "M2008", "M700", "M37" is ordered: M37, M700, M2008
    (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int,  -- first origin1
    (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int   -- then origin2
```
