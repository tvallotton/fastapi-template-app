
-- Add migration script here

create function create_history_table(base_table text) returns void as
$$
declare 
    table_name text := FORMAT('%I', base_table);
    table_history_name text := FORMAT('%I', base_table || '_history');
    sql_ text := null;
begin
    execute 'create table ' || table_history_name || ' ( 
        valid_since timestamptz not null,
        valid_until timestamptz,
        like ' || table_name || '
        );
        create trigger '|| table_history_name ||'
        after insert or update or delete on '|| table_name ||' for each row execute function update_history();
        create index on '|| table_history_name ||' (valid_since);
        create index on '|| table_history_name ||' (valid_until);
        ';
end;
$$
language plpgsql;

create or replace function drop_history_table(base_table text) returns void as 
$$
declare 
    table_name text := FORMAT('%I', base_table || '_history');
begin
    execute 'drop trigger if exists ' || table_name  ||' on ' || base_table;
    execute 'drop table ' || table_name;
end;
$$
language plpgsql;