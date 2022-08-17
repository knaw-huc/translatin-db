drop table if exists works cascade;
create table works (
    id uuid primary key,
    label text not null -- 'W1 .. Wxx'
);
create unique index on works (label);

drop table if exists expressions_work cascade;
create table expressions_work (
    work_id uuid not null references works (id),
    expression_id uuid not null references expressions (id),
    primary key (work_id, expression_id)
);
create unique index on expressions_work (expression_id);
