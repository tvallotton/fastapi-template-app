
-- Add migration script here

create function update_history() returns trigger as
$$
declare
    tbl_history text        := FORMAT('%I.%I', TG_TABLE_SCHEMA, TG_TABLE_NAME || '_history');
    valid_since timestamptz := now();
    valid_until timestamptz := NULL;
    
begin
    if (TG_OP = 'DELETE') then
        execute 'UPDATE ' || tbl_history || ' SET valid_until = $1 WHERE id = $2.id AND valid_until IS NULL'
            using now(), old;
        return OLD;
    elsif (TG_OP = 'UPDATE') then
        execute 'UPDATE ' || tbl_history || ' SET valid_until = $1 WHERE id = $2.id AND valid_until IS NULL'
            using valid_since, new;
        execute 'INSERT INTO ' || tbl_history ||
                ' SELECT $1, $2, $3.*' using valid_since, valid_until, NEW;
        return NEW;
    elseif (TG_OP = 'INSERT') then
        execute 'UPDATE ' || tbl_history || ' SET valid_until = $1 WHERE id = $2.id AND valid_until IS NULL'
            using valid_since, new;
        execute 'INSERT INTO ' || tbl_history ||
                ' SELECT $1, $2, $3.*' using valid_since, valid_until, NEW;
        return NEW;
    end if;
    return NULL;
    -- Foreign key violation means required related entity doesn't exist anymore.
    -- Just skipping trigger invocation
exception
    when foreign_key_violation then
        return NULL;
end;
$$
    language plpgsql;