## Import Translatin WEMI Excel files into central pgadmin

### build docker image
```shell
./build.sh
```

### start shell in container
```shell
./start.sh
```

### verify mounts (optional)
```shell
ls            # should contain code
ls -l /db     # should contain init.sql
ls -l /upload # should contain Translatin_XXX.xlsx files
```

### (re-)create database
!! Note: destructive operation. Clears out entire database on pgadmin server by
dropping all tables and re-creating them !!
```shell
./db.sh < /db/init.sql
```

### (re-)import excel sheet data
```shell
./import-authors.py
./import-publishers.py
./import-manifestations.py   # depends on and must run *after* importing {authors,publishers}
```

### verify some data using psql (optional)
```shell
./db.sh
```
then
```sql
\dt
select count(*) from authors;
select count(*) from publishers;
select count(*) from manifestations;
```
