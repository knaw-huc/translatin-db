drop table if exists expressions cascade;
create table expressions (
    id uuid primary key,
    label text not null -- 'E1 .. Exx'
);
create unique index on expressions (label);

drop table if exists expression_manifestations cascade;
create table expression_manifestations (
    expression_id uuid not null references expressions (id),
    manifestation_id uuid not null references manifestations (id),
    primary key (expression_id, manifestation_id)
);
create unique index on expression_manifestations (manifestation_id);
