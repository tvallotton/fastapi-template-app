insert into "place" (
    id, 
    city_id, 
    street, 
    number, 
    geometry
)
values (
    {id}, 
    {city_id}, 
    {street}, 
    {number}, 
    geo.st_setsrid(geo.st_makepoint({longitude},{latitude}), 4326)
)
on conflict (id) do update set
    id = {id}, 
    city_id = {city_id},
    street = {street}, 
    number = {number}, 
    geometry  = geo.st_setsrid(geo.st_makepoint({longitude},{latitude}), 4326 )
returning 
    id, 
    city_id, 
    street, 
    number, 
    geo.st_x(geometry) as "longitude",
    geo.st_y(geometry) as "latitude";