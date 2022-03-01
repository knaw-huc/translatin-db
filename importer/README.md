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

## Experimental

### create provenance table about this import
```sql
create table _provenance (name text, size integer, sha1sum char(40));
```

### add entries for each file (manually for now, later from script)
```sql
insert into import (name,size, sha1sum) values ('TransLatin_Authors.xlsx', 40515, 'a82a5d334b81fc5f078dacba3dc752204db9d3ce'), ('TransLatin_Manifestations.xlsx', 1371909, 'bf657ad6b831a1b05f05636048a0a33d7f434f0b'), ('TransLatin_Printers_Publishers.xlsx',31169,'ff18236f137617502f9fed2bd1075cd2e7323ee3');
```

### add timestamp as an afterthought
```sql
alter table _provenance add column imported_at timestamp;
update _provenance set imported_at = now();
```
