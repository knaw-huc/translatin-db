- [x] Titels omzetten naar (title,language) paren
- [ ] Cartesisch product (translatin,ceneton,external) x (has_scan, has_transcription)
- [x] Author 'Anonymous' uitrollen naar author_01, author_02 etc. met kolom is_anonymous zodat er losse anonymi zijn ->
  
### Anonymous authors:
Opgelost met boolean 'is_anonymous' (not null) in de manifestation zelf en dan gewoon 0 gerelateerde
authors in de koppeltabel.
- [ ] Jirsi: ok?

### Maak (titel,language) uniek ipv alleen titel:
Tabellen voor titel en (language,certainty) samengevoegd tot een tabel met (titel,language,certainty) tupels.
```sql
translatin=# SELECT DISTINCT(language,certainty),count(*) \
             FROM manifestation_titles \
             GROUP BY language,certainty \
             ORDER BY count(*) DESC;
             
        row         | count
--------------------+-------
 (Latin,Certain)    |  1620
 (Dutch,Certain)    |   356
 (Dutch,Uncertain)  |   195
 (Latin,Uncertain)  |   116
 (French,Certain)   |    87
 (French,Uncertain) |     6
 (Spanish,Certain)  |     1
(7 rows)