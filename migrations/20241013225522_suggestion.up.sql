-- Add up migration script here

create view suggestion as (
    select distinct on (street, number) *, 
        geo.st_y(geometry) as latitude,
        geo.st_x(geometry) as longitude,
        (case when "number" is not null then street || ' ' || "number" else  street end) as address
    from place
);

create index place_address_idx on place using gin ((case when "number" is not null then street || ' ' || "number" else  street end) gin_trgm_ops);
