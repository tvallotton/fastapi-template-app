-- Add down migration script here

select drop_history_table('storage');
drop table storage;