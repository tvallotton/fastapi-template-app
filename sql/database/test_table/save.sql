insert into test_table (id, field) 
values ({id}, {field})
on conflict (id) do update set 
    id = {id},
    field = {field}
returning id, field