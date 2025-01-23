insert into "storage_test_table" (id, storage_id)
values (
    {id},
    {storage_id} 
)
on conflict (id) do update set
    id          = {id},
    storage_id  = {storage_id}
returning id, storage_id;