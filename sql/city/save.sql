insert into "city" (id, region_id)
values (
    {id}, 
    {region_id}
)
on conflict (id) do update set
    id        = {id},
    region_id = {region_id}
returning id, region_id;