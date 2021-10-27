SELECT PUB.NAME PUBLISHER,
	PL.NAME PLACE,
	EARLIEST,
	LATEST,
	MAN.ORIGIN
FROM MANIFESTATIONS MAN,
	MANIFESTATIONS_PUBLISHERS MP,
	PLACES PL,
	PUBLISHERS PUB
WHERE MAN.ID = MP.MANIFESTATION_ID
	AND PL.ID = MP.PLACE_ID
	AND PUB.ID = MP.PUBLISHER_ID
GROUP BY PUBLISHER,
	PLACE,
	EARLIEST,
	LATEST,
	ORIGIN
ORDER BY PUBLISHER,
	EARLIEST,
	LATEST
