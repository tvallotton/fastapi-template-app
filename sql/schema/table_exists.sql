select count(*) != 0 as "exists"
from information_schema.tables 
where table_name = {table_name}
