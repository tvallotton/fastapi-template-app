insert into "user" (id, email, is_admin)
values (
    {id}, 
    {email}, 
    {is_admin}
)
on conflict (id) do update set
    id       = {id},
    email    = {email},
    is_admin = {is_admin}
returning id, email, is_admin;