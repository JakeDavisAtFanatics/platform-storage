### pg_repack

Build the `pg_repack` Docker containers:

```bash
# Build pg_repack for Postgres 13
docker build docker/pg_repack_1.4.6_for_pg_13 -t pst/pg-repack-1.4.6

# Build pg_repack for Postgres 16
docker build docker/pg_repack_1.5.0_for_pg_16 -t pst/pg-repack-1.5.0

# Build pg_repack for Postgres 17
docker build docker/pg_repack_1.5.1_for_pg_17 -t pst/pg-repack-1.5.1
```

Create aliases to wrap the Docker command:
- This command mounts your local `~/.pgpass` to the container to handle Postgres authentication

```bash
alias pg_repack@13="docker run -v ~/.pgpass:/root/.pgpass:ro -it --rm --network host pst/pg-repack-1.4.6 pg_repack"
alias pg_repack@16="docker run -v ~/.pgpass:/root/.pgpass:ro -it --rm --network host pst/pg-repack-1.5.0 pg_repack"
alias pg_repack@17="docker run -v ~/.pgpass:/root/.pgpass:ro -it --rm --network host pst/pg-repack-1.5.1 pg_repack"
```

Use the aliases as you would the `pg_repack` tool normally:

```bash
$ pg_repack@17 --version
pg_repack 1.5.1

$ pg_repack@17 -h 127.0.0.1 -p 7432 -U postgres --dbname=ats_fanatics --table=jobs.batch_step_execution --dry-run
INFO: Dry run enabled, not executing repack
INFO: repacking table "jobs.batch_step_execution"
```