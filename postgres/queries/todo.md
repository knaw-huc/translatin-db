Zou je, als opmaat naar de realisatie van het Expression-niveau, eens een query
kunnen schrijven die nagaat welke records: 1) exact dezelfde auteur hebben 2)
exact hetzelfde jaar van uitgave hebben (of indien er sprake is van een
periode: overlapping qua periodisering met elkaar) 3) min of meer dezelfde
titel hebben (ik weet niet of je met Levenshtein-distance of Soundex kunt
werken, maar in dat geval bijvoorbeeld een waarde van 0.9). Mocht dit laatste
matchingscriterium lastig worden in SQL (wat ik me kan voorstellen), dan is
exacte matching op titel ook goed. Deze query zou moeten bepalen of er nog
dubbele registraties in het Manifestations-bestand staan.
