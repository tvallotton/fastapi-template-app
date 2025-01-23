select 
    columns.column_name as "column_name"
    , tc.table_name as "reference_table_name"
    , kcu.column_name as "reference_column_name"
from information_schema.columns
    join information_schema.constraint_column_usage ccu on ccu.column_name = columns.column_name    and columns.table_name = ccu.table_name 
    join information_schema.table_constraints tc        on ccu.constraint_name = tc.constraint_name and tc.constraint_type = 'FOREIGN KEY'
    join information_schema.key_column_usage kcu        on tc.constraint_name = kcu.constraint_name 
    
where
    columns.table_name = {table_name}