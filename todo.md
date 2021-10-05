* Titels omzetten naar (title,language) paren
* Cartetisch product (translatin,ceneton,external) x (has_scan, has_transcription)

* Author 'Anonymous' uitrollen naar author_01, author_02 etc. met kolom is_anonymous zodat er losse anonymi zijn ->
  opgelost met boolean 'is_anonymous' (not null) in de manifestation zelf en dan gewoon 0 gerelateerde authors in de
  koppeltabel. Jirsi: ok?
