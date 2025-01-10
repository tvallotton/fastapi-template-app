-- Add up migration script here
create table storage (
    id uuid primary key default gen_random_uuid(),
    bucket text not null,
    sha1 bytea not null,
    unique (bucket, sha1)
);

select create_history_table('storage');
