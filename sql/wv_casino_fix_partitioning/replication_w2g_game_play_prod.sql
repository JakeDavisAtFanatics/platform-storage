-- Example script, should be must update pub/sub names.

-- As replication user, drop table from publication on the child
-- export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-cert-1mi fbg-cert-1mi-postgresql)
ALTER PUBLICATION pub_fbg_cert_1mi_to_fbg_cert_1 DROP TABLE public.w2g_gameplay;

-- As replication user, refresh the publication on the parent
-- export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-cert-1 fbg-cert-1-postgresql)
ALTER SUBSCRIPTION sub_fbg_cert_1mi_to_fbg_cert_1 REFRESH PUBLICATION;

-- run partitioning scripts for w2g_gameplay

-- As replication user, add table to publication on child
-- export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-cert-1mi fbg-cert-1mi-postgresql)
ALTER PUBLICATION pub_fbg_cert_1mi_to_fbg_cert_1 ADD TABLE public.w2g_gameplay;

-- As replication user, refresh the publication on the parent, do not copy data!
-- export $(fbg postgres credentials get --skip-refresh --skip-test --user replication --env fbg-cert-1 fbg-cert-1-postgresql)
ALTER SUBSCRIPTION sub_fbg_cert_1mi_to_fbg_cert_1 REFRESH PUBLICATION WITH (copy_data = false);