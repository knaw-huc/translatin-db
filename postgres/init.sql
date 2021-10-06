drop type if exists form cascade;
create type form as enum (
    'First Printing',
    'Fragment',
    'Manuscript',
    'Mention',
    'Reprint',
    'Synopsis',
    'Synopsis (manuscript)',
    'Synopsis (printed)'
);

drop type if exists form_type cascade;
create type form_type as enum (
    'Fragment',
    'Full edition',
    'Synopsis'
);

drop table if exists manifestations cascade;
create table manifestations (
    id uuid primary key,
    origin text not null, -- 'M1 .. M2249 in TransLatin_Manifestations.xlsx'
    earliest date not null,
    latest date not null,
    form form,
    form_type form_type not null,
    is_anonymous boolean not null,
    genre text,
    subgenre text,
    has_dramaweb_scan boolean,                  -- internal: somewhere in project there is a scan (column Y)
    has_dramaweb_transcription boolean,         -- internal: transcription was made in this project (column Y)
    ceneton_scan text,                          -- optional url, taken from column 'BD'
    ceneton_transcription text,                 -- optional url, taken from column 'BE'
    external_scan text,                         -- optional url, taken from column 'AM'
    external_transcription boolean not null,    -- not in excel, always false to start, can manually set to true
    fingerprint text,
    characters text,
    literature text,
    remarks text
);
create unique index on manifestations(origin);

drop type if exists languages cascade;
create type languages as enum (
-- this is MvdP's list of languages used in Translatin, taken from Confluence page
    'Croatian',
    'Czech',
    'Danish',
    'Dutch',
    'English',
    'French',
    'German',
    'Greek',
    'Hungarian',
    'Italian',
    'Latin',
    'Norwegian',
    'Polish',
    'Russian',
    'Spanish',
    'Swedish'
);

drop type if exists certainty cascade;
create type certainty as enum ('Certain', 'Uncertain');

drop table if exists manifestation_titles cascade;
create table manifestation_titles (
    manifestation_id uuid not null,
    title text not null,
    language languages not null,
    certainty certainty not null,
    primary key (manifestation_id, title, language),
    foreign key (manifestation_id) references manifestations (id)
);
create index on manifestation_titles (language, certainty);

drop table if exists manifestation_ceneton cascade;
create table manifestation_ceneton (
    manifestation_id uuid not null,
    ceneton_id text not null,
    primary key (manifestation_id, ceneton_id),
    foreign key (manifestation_id) references manifestations (id)
);

drop type if exists author_types cascade;
create type author_types as enum ('Person', 'Organization');

drop table if exists authors cascade;
create table authors (
    id uuid primary key,
    name text not null,
    origin smallint not null, -- '1 .. 147 in TransLatin_Authors.xlsx'
    type author_types not null,
    first_name text,
    prefix text,
    surname text,
    birth_earliest date,
    birth_latest date,
    birth_place smallint,
    death_earliest date,
    death_latest date,
    death_place smallint,
    occupation text,
    religion text,
    image text,
    wikidata text
);
create unique index on authors (name);
create unique index on authors (origin);

drop table if exists places cascade;
create table places (
    id smallserial primary key,
    name text
);
create unique index on places (name);

drop table if exists author_names cascade;
create table author_names (
    author_id uuid not null,
    name text not null,
    primary key (author_id, name),
    foreign key (author_id) references authors (id)
);

drop table if exists author_viaf_links cascade;
create table author_viaf_links (
    author_id uuid not null,
    viaf text not null,
    primary key (author_id, viaf),
    foreign key (author_id) references authors (id)
);

drop table if exists author_nta_links cascade;
create table author_nta_links (
    author_id uuid not null,
    nta text not null,
    primary key (author_id, nta),
    foreign key (author_id) references authors (id)
);

drop table if exists authors_manifestations cascade;
create table authors_manifestations (
    author_id uuid not null,
    manifestation_id uuid not null,
    primary key (author_id, manifestation_id),
    foreign key (manifestation_id) references manifestations (id),
    foreign key (author_id) references authors (id)
);
create unique index on authors_manifestations (manifestation_id, author_id);

drop table if exists publishers cascade;
create table publishers (
    id uuid primary key,
    name text not null,
    wed_erven text,         -- create optional enum type ('Wed', 'Erven', 'Both')?
    first_name text,        -- empty for publishers
    patronym text,          -- e.g., 'jansz.'
    prefix text,            -- e.g., 'de', 'vander'
    addition text,          -- e.g., (i) (ii)
    surname text not null   -- equal to 'name' for publishers (e.g., Elzevier)
);
create unique index on publishers (name);

drop table if exists publisher_names cascade;
create table publisher_names (
    publisher_id uuid not null,
    name text not null,
    primary key (publisher_id, name),
    foreign key (publisher_id) references publishers (id)
);
create unique index on publisher_names (name, publisher_id);

drop table if exists manifestations_publishers cascade;
create table manifestations_publishers (
    manifestation_id uuid not null,
    publisher_id uuid not null,
    primary key (manifestation_id, publisher_id),
    foreign key (manifestation_id) references manifestations (id),
    foreign key (publisher_id) references publishers (id)
);
create unique index on manifestations_publishers (publisher_id, manifestation_id);
