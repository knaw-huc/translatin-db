# Vind vergelijkbare titels

Het zou kunnen voorkomen dat titels als 'Jozef' soms ook in een veel langere vorm voorkomen (denk aan 'tocht van Jozef uit ...' etc.
Titels zijn vergelijkbaar als:

- de korte titel in de lange voorkomt;
- daarbij normalisatie van beide titels ivm latijn:
    - lowercase
    - j == i
    - v == u

```sql
SELECT M1.ORIGIN origin1,
    MT1.TITLE title1,
    M1.EARLIEST earliest1,
    M1.LATEST latest1,
    M1.FORM form1,
    M1.FORM_TYPE formtype1,
    M1.GENRE genre1,
    M1.SUBGENRE subgenre1,
    M2.ORIGIN origin2,
    MT2.TITLE title2,
    M2.EARLIEST earliest2,
    M2.LATEST latest2,
    M2.FORM form2,
    M2.FORM_TYPE formtype2,
    M2.GENRE genre2,
    M2.SUBGENRE subgenre2
FROM MANIFESTATIONS M1
    JOIN MANIFESTATION_TITLES MT1 on (M1.ID = MT1.MANIFESTATION_ID),
    MANIFESTATIONS M2
    JOIN MANIFESTATION_TITLES MT2 on (M2.ID = MT2.MANIFESTATION_ID)
WHERE MT1.MANIFESTATION_ID <> MT2.MANIFESTATION_ID
    AND LENGTH(MT1.TITLE) < LENGTH(MT2.TITLE)
    AND POSITION(
        TRANSLATE(LOWER(MT1.TITLE), 'jv', 'iu') in TRANSLATE(LOWER(MT2.TITLE), 'jv', 'iu')
    ) > 0
ORDER BY
    LENGTH(MT1.TITLE) DESC,
    MT2.TITLE
```
