SELECT count(*) 
FROM information_schema.tables 
WHERE table_name = CONCAT({table_name}, '_history');
