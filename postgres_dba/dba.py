import logging

import typer

from postgres_dba.commands.backup_table import app as backup_table
from postgres_dba.commands.table_info import app as table_info
from postgres_dba.commands.watch_processlist import app as watch_processlist
from postgres_dba.commands.watch_replication import app as watch_replication
from postgres_dba.commands.watch_subscription import app as watch_subscription

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


app = typer.Typer()

app.add_typer(backup_table, name="backup-table", help="Create a backup table.")
app.add_typer(table_info, name="table-info", help="Get table info.")
app.add_typer(
    watch_processlist, name="watch-processlist", help="Watch the the longest running queries in the processlist."
)
app.add_typer(watch_replication, name="watch-replication", help="Watch the replication lag for all replication slots.")
app.add_typer(
    watch_subscription, name="watch-subscription", help="Watch the subscription sync state for all subscriptions."
)
