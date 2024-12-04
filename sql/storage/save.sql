insert into "storage" (id, bucket, sha1)
values (
    {id}, 
    {bucket}, 
    {sha1}
)
on conflict (id) do update set
    id      = {id},
    bucket  = {bucket},
    sha1    = {sha1}
returning id, bucket, sha1;