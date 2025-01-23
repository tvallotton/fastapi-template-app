select count(*)
from storage
join {reference_table_name:ident} on {reference_table_name:ident}.{reference_column_name:ident} = storage.{column_name:ident}
where storage.id = {id}