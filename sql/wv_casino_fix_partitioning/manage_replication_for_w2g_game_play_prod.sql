-- Example script, must update pub/sub names.

-- when writes stopped, drop table from publication on the child
-- on child as replication user 
-- export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-cert-1mi fbg-cert-1mi-postgresql)
ALTER PUBLICATION pub_fbg_cert_1mi_to_fbg_cert_1 DROP TABLE public.w2g_gameplay;

-- refresh the publication on the parent to pickup dropped table
-- on parent as replication user
-- export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-cert-1 fbg-cert-1-postgresql)
ALTER SUBSCRIPTION sub_fbg_cert_1mi_to_fbg_cert_1 REFRESH PUBLICATION;

-- Do Matt's partitioning scripts

-- when partitioning complete, add table to publication on child
-- on child as replication user 
-- export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-cert-1mi fbg-cert-1mi-postgresql)
ALTER PUBLICATION pub_fbg_cert_1mi_to_fbg_cert_1 ADD TABLE public.w2g_gameplay;

-- refresh the publication on the parent to pickup added table, do not copy data!
-- on parent as replication user
-- export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-cert-1 fbg-cert-1-postgresql)
ALTER SUBSCRIPTION sub_fbg_cert_1mi_to_fbg_cert_1 REFRESH PUBLICATION WITH (copy_data = false);