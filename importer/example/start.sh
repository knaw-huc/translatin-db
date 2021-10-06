docker run -it \
	-v /absolute/path/to/postgres/init.sql:/db/init.sql:ro \
	-v /absolute/path/to/excel/files:/upload:ro \
	wemi bash
