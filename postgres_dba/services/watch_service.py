import logging
from time import sleep

from postgres_dba.common.data_types import Query, Row
from postgres_dba.models.response_model import Response
from postgres_dba.services.postgres.postgres_service import PostgresService
from postgres_dba.utils.utils import print_table_from_rows

logger = logging.getLogger(__name__)


class WatchService:
    def __init__(self, pg: PostgresService, interval: int = 2):
        self.pg: PostgresService = pg
        self.interval: int = interval

    def watch(self, query: Query) -> Response[None]:
        try:
            with self.pg.get_cursor(autocommit=True) as cur:
                while True:
                    cur.execute(query)
                    response: Response[list[Row]] = self.pg.fetch_all_using_cursor(cur)

                    if response.has_error:
                        logger.error(response)

                    rows: list[Row] = response.data or []
                    print_table_from_rows(rows)
                    sleep(self.interval)
        except KeyboardInterrupt:
            logger.info("Stopped watching.")
            watch_response: Response = Response.success()

            return watch_response
        except Exception as e:
            watch_response: Response = Response.failure(error=e)

            return watch_response
