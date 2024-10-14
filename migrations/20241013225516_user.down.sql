-- Add migration script here
drop table "user";
select drop_history_table('user');