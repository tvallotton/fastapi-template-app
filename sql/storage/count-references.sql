select count(*)
from storage
join {table_name:ident} on {table_name:ident}.{column_name:ident} = storage.{foreign_column_name:ident}
where storage.id = {id}