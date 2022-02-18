# TransLatin: van Manifestations naar Expressions

Om van Manifestations naar Expressions te komen is het belangrijk om na te gaan
welke Manifestations dezelfde intellectuele inhoud hebben. Zij vormen de
Expressions. Volledige edities (first printing, reprints) die door één auteur
(bijv. de Jezuïeten van Mechelen) zijn uitgebracht met min of meer dezelfde
titel (Joseph/Ioseph), hetzelfde genre kennen maar door verschillende drukkers
zijn gedrukt, vallen bijvoorbeeld onder dezelfde Expression.

Met de volgende metadata moet rekening worden gehouden in de query nu we van
Manifestations naar Expressions proberen te komen:

- Alle auteurs moeten overeenkomen (hard criterium volgorde maakt niet uit),
na implementatie van data Proot moeten we dit criterium waarschijnlijk herzien
omdat we dan veel meer onbekende auteurs hebben opgespoord die werkten voor een
organsation die we nu nog hebben onderscheiden als bijv. ‘Jezuïeten van…’). Kan
vooralsnog gewoon met ID’s van de auteurs.

- Áls de taal of talen van een Manifestation met zekerheid zijn vastgesteld,
dan moeten deze allemaal exact overeenkomen (volgorde speelt geen rol). Als er
veel Manifestations zijn waarvan de taal of talen niet met zekerheid zijn
vastgesteld en die om die reden niet kunnen worden samengevoegd tot dezelfde
Expression, zou ik deze graag nog eens willen bekijken.

- Min of meer dezelfde titel. Net als bij de laatste ontdubbeling van de
Manifestations zelf met een Levensthein afstand van 0.1 of 0.2 (ligt een beetje
aan de zoekopbrengst).

- ‘Form_type’ moet overeenkomen. Is iets dat ik sowieso nog even zou willen
langslopen voor we definitief Manifestations samenvoegen tot dezelfde Expression.

- Áls er een genre wordt genoemd, moet deze overeenkomen. Áls er een
subgenre wordt genoemd, mag deze niet conflicteren met een ander subgenre (er
worden wellicht Manifestations genoemd die hetzelfde overkoepelende genre
hebben, maar waarvan het subgenre net iets verschilt).

- Een tijdsframe van 25 jaar kan vooralsnog worden aangehouden om
Manifestations samen te voegen. Ik zal hierover nog overleg hebben met de
andere TransLatin-collega’s en laat het weten als dit nog moet worden
aangepast.

- Op termijn (na samenvoeging van data Proot): de personages moeten
overeenkomen.

## Work in progress

```sql
SELECT
    -- stuff related to first candidate
    M1.ORIGIN ORIGIN1,
    M1.FORM FORM1,
    M1.EARLIEST EARLIEST1,
    M1.LATEST LATEST1,
    MT1.TITLE TITLE1,
    MT1.LANGUAGE LANG1,
    MT1.CERTAINTY CERTAIN1,

    -- stuff related to second candidate
    M2.ORIGIN ORIGIN2,
    M2.FORM FORM2,
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
    AND LEVENSHTEIN(MT1.TITLE, MT2.TITLE) <= ROUND(GREATEST(LENGTH(MT1.TITLE), LENGTH(MT2.TITLE)) * 0.2)

    -- Form_type must match
    AND m1.form_type = m2.form_type

    -- Genre must match, if it exists
    AND (
        m1.genre = m2.genre
        OR m1.genre IS NULL
        OR m2.genre IS NULL
    )

    -- Subgenre must match, if it exists
    AND (
        m1.subgenre = m2.subgenre
        OR m1.subgenre IS NULL
        OR m2.subgenre IS NULL
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

    -- No need to see each symmetrical pair (origin1,origin2) again as (origin2,origin1)
    -- e.g. from (M24,M31) and (M31,M24) only keep (M24,M31) based on 24 < 31
    AND (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int < (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int

ORDER BY
    -- order by origin, e.g. (string) "M2008": seen as (int) 2008 => so "M2008", "M700", "M37" is ordered: M37, M700, M2008
    (SUBSTRING(M1.ORIGIN, 2, LENGTH(M1.ORIGIN)-1))::int,  -- first origin1
    (SUBSTRING(M2.ORIGIN, 2, LENGTH(M2.ORIGIN)-1))::int   -- then origin2
```
