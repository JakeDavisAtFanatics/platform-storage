GRANT INSERT, UPDATE, DELETE ON game_play TO ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'game_play' AND grantee = 'ats_owner';