-- Add down migration script here
DROP TRIGGER tg_pgqueuer_changed ON pgqueuer;
DROP FUNCTION fn_pgqueuer_changed;
DROP TABLE pgqueuer;
DROP TABLE pgqueuer_statistics;
DROP TABLE pgqueuer_schedules;
DROP TYPE pgqueuer_status;
DROP TYPE pgqueuer_statistics_status;