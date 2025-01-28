-- Add up migration script here
create table place (
    id int primary key,
    city_id text not null references city(id),
    street text not null,
    number text,
    geometry geo.geometry(Point, 4326)
);
