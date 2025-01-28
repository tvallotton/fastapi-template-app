insert into "region" (id)
values (
    {id}
)
on conflict (id) do update set
    id = {id}
returning id;