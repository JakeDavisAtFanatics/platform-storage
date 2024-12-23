# PST (Platform Storage Tools)

A collection of tools for PostgreSQL database management and environment configuration.

## Installation

Create and activate a Python 3.12 virtual environment:
- This path is required `~/.pst`
- Python 3.12 is currently a requirement for `aider-chat`. When upgrading, also update the interpreter in `.vscode/settings.json`.

```bash
python3.12 -m venv ~/.pst && source ~/.pst/bin/activate
```

Install project requirements:

```bash
pip install -r requirements.txt
```

Install PST module:

```bash
pip install -e .
```

Install `psql`:

```bash
brew install libpq
```

Create and configure `~/.psqlrc`:

```bash
\x auto
\pset pager off
\set PROMPT1 '%m %n@%/%R%#%x '
\set PROMPT2 '%m %n@%/%R%# '
\set VERBOSITY verbose
\timing
```

Add tools to your path and helper aliases in `~/.zshrc` or `~/.bashrc`:

```bash
# Platform Storage Tools
export PATH="$HOME/workspace/platform-storage-tools/bin:$PATH" # PST bash scripts
export PATH="/opt/homebrew/opt/libpq/bin:$PATH" # psql
alias activate="source $HOME/.pst/bin/activate" # Activate PST virtual env
alias pgdev="pg dev fbg-dev-1 fbg-dev-1-postgresql postgres" # Connect to dev parent
alias pginfdev="pg inf-dev fbg-inf-dev-1 fbg-inf-dev-1-postgresql postgres" # Connect to inf-dev parent
alias pgtest="pg test fbg-test-1 fbg-test-1-postgresql postgres" # Connect to test parent
alias pgcert="pg cert fbg-cert-1 fbg-cert-1-postgresql postgres" # Connect to cert parent
alias pgprod="pg prod fbg-prod-1 fbg-prod-1-postgresql postgres" # Connect to prod parent
```

## Usage

First, you must always activate the virtual environment:

```bash
# If you added the alias during installation you can just run
activate

# Or run
source ~/.pst/bin/activate
```

### pginit

Initialize Postgres environment files:
- This is required to use other PST tools
- Find Postgres instances and add them to `~/.pst/envs/$env.yaml`
- Configure Postgres connections in `~/.pgpass` 

```bash
usage: pginit
```

### pg

Interactively connect to Postgres instances:

```bash
usage: pg [-h] [stage] [environment] [instance] [user]

PostgreSQL Interactive Tool

positional arguments:
  stage        Stage name
  environment  Environment name
  instance     Instance name
  user         Username

options:
  -h, --help   show this help message and exit

# List all available stages
pg

# List all available environments in dev
pg dev

# List all available instances in fbg-dev-1
pg dev fbg-dev-1

# List all available users on fbg-dev-1-postgresql
pg dev fbg-dev-1 fbg-dev-1-postgresql

# Connect to fbg-dev-1-postgresql as the postgres user
pg dev fbg-dev-1 fbg-dev-1-postgresql postgres

# If you added the aliases during installation you can quickly connect to parents by running
pgdev
pginfdev
pgtest
pgcert
pgprod
```

### pghosts

Print Postgres endpoints and ports (from `~/.pgpass`) matching a search term:

```bash
# List all hostnames matching inf-dev
pghosts inf-dev
```

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