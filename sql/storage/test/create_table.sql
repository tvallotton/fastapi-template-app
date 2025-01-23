create table storage_test_table (
    id uuid primary key default gen_random_uuid(),
    storage_id uuid not null references storage(id)
);