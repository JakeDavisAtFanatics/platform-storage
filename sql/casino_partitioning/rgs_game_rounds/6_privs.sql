GRANT INSERT, UPDATE, DELETE ON rgs_game_rounds TO ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'rgs_game_rounds' AND grantee = 'ats_owner';