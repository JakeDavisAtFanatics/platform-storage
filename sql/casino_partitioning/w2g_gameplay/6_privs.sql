GRANT INSERT, UPDATE, DELETE ON w2g_gameplay TO ats_owner;
SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE table_name = 'w2g_gameplay' AND grantee = 'ats_owner';