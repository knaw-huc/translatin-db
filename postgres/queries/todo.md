Zou je, als opmaat naar de realisatie van het Expression-niveau, eens een query
kunnen schrijven die nagaat welke records: 1) exact dezelfde auteur hebben 2)
exact hetzelfde jaar van uitgave hebben (of indien er sprake is van een
periode: overlapping qua periodisering met elkaar) 3) min of meer dezelfde
titel hebben (ik weet niet of je met Levenshtein-distance of Soundex kunt
werken, maar in dat geval bijvoorbeeld een waarde van 0.9). Mocht dit laatste
matchingscriterium lastig worden in SQL (wat ik me kan voorstellen), dan is
exacte matching op titel ook goed. Deze query zou moeten bepalen of er nog
dubbele registraties in het Manifestations-bestand staan.

## Welke titels lijken op elkaar
```sql
SELECT LEVENSHTEIN(MT1.TITLE,MT2.TITLE) DIST,
	MAN1.ORIGIN MAN1,
	'"' || MT1.TITLE || '"' T1,
	MAN2.ORIGIN MAN2,
	'"' || MT2.TITLE || '"' T2,
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
