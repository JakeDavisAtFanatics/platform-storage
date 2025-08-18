import logging

import typer

from dba.commands.backup_table import app as backup_table
from dba.commands.table_info import app as table_info
from dba.commands.watch_replication import app as watch_replication
from dba.commands.watch_subscription import app as watch_subscription

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


app = typer.Typer()

app.add_typer(backup_table, name="backup-table", help="Create backup table.")
app.add_typer(table_info, name="table-info", help="Get table info.")
app.add_typer(watch_replication, name="watch-replication", help="Watch replication lag.")
app.add_typer(watch_subscription, name="watch-subscription", help="Watch subscription sync state.")
