-- Add migration script here

create table "user" (
    id uuid primary key default gen_random_uuid(),
    email text not null unique,
    is_admin boolean not null default false
);

select create_history_table('user');

