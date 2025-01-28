-- Add up migration script here
create table city (
    id text primary key,
    region_id text references region(id)
);