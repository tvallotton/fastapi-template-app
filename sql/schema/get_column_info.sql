select 
    columns.column_name,
    data_type, 
    is_nullable = 'YES' or column_default is NULL as is_required,
    is_nullable = 'YES' as is_nullable,
    ccu.table_name as foreign_table,
    kcu.column_name as foreign_column
from information_schema.columns
    left join information_schema.key_column_usage kcu        on kcu.column_name = columns.column_name    and columns.table_name = kcu.table_name
    left join information_schema.table_constraints tc        on tc.constraint_name = kcu.constraint_name and tc.table_name = columns.table_name
    left join information_schema.constraint_column_usage ccu on ccu.constraint_name = tc.constraint_name
where
    columns.table_name = {table_name};
