
-- we use a materialized view because 
-- I couldn't get postgres to index use the 
-- gist index on a regular view
create materialized view suggestion as (
    select distinct on (street, number)
        id,
        city_id,
        street,
        number,
        geo.st_y(geometry) as latitude,
        geo.st_x(geometry) as longitude,
        (case when "number" is not null then street || ' ' || "number" else  street end) as address
    from place
);

create index suggestion_address on suggestion using gist (address gist_trgm_ops);
