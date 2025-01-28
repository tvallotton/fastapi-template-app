

with unique_streets as (
    select distinct on (street) id, city_id, street, NULL as "number", latitude, longitude, street as "address"
    from suggestion
    order by street desc
), street_suggestions as (
    select *
    from unique_streets
    order by  {address} <<-> address
    limit 8
), address_suggestions as (
    select 
        id, city_id, street, number, latitude, longitude, address
    from suggestion
    order by {address} <<-> address
    limit 8
), all_suggestions as (
    (select *, 0 as "origin" from street_suggestions) union all (select *, 1 as "origin"  from address_suggestions) 
)

select * from all_suggestions
order by  {address} <<-> address, origin limit 8;
