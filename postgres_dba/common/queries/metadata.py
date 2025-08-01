from psycopg.sql import SQL, Composed, Literal

from postgres_dba.common.data_types import Query
from postgres_dba.models.postgres_table_model import PostgresTable
from postgres_dba.utils.utils import log_sql


def select_check_constraints_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
     r.conname AS name,
     pg_catalog.pg_get_constraintdef (r.oid, true) AS check
FROM
     pg_catalog.pg_constraint r
WHERE
     r.conrelid = {}
     AND r.contype = 'c'
ORDER BY
     1;
""").format(Literal(table.oid))

    log_sql("select_foreign_keys_sql", sql)

    return Query(sql)


def select_column_count_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL(
        "SELECT COUNT(1) FROM information_schema.columns WHERE table_schema = {} AND table_name = {};"
    ).format(Literal(table.schema_), Literal(table.name))

    log_sql("select_column_count_sql", sql)

    return Query(sql)


def select_column_definition_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""                 
SELECT
    a.attname AS COLUMN,
    pg_catalog.format_type (a.atttypid, a.atttypmod) AS TYPE,
    (
        SELECT
            c.collname
        FROM
            pg_catalog.pg_collation c,
            pg_catalog.pg_type t
        WHERE
            c.oid = a.attcollation
            AND t.oid = a.atttypid
            AND a.attcollation <> t.typcollation
    ) AS COLLATION,
    CASE
        WHEN a.attnotnull THEN 'not null'
        ELSE ''
    END AS NULLABLE,
    (
        SELECT
            pg_catalog.pg_get_expr (d.adbin, d.adrelid, TRUE)
        FROM
            pg_catalog.pg_attrdef d
        WHERE
            d.adrelid = a.attrelid
            AND d.adnum = a.attnum
            AND a.atthasdef
    ) AS DEFAULT
FROM
     pg_catalog.pg_attribute a
WHERE
     a.attrelid = {}
     AND a.attnum > 0
     AND NOT a.attisdropped
ORDER BY
     a.attnum;
""").format(Literal(table.oid))

    log_sql("select_column_definition_sql", sql)

    return Query(sql)


def select_foreign_keys_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
     conname AS name,
     pg_catalog.pg_get_constraintdef (r.oid, true) as reference
FROM
     pg_catalog.pg_constraint r
WHERE
     r.conrelid = {}
     AND r.contype = 'f'
     AND conparentid = 0
ORDER BY
     conname;
""").format(Literal(table.oid))

    log_sql("select_foreign_keys_sql", sql)

    return Query(sql)


def select_indexes_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
     c2.relname AS name,
     CASE
          WHEN i.indisprimary THEN 'PRIMARY KEY'
          WHEN i.indisunique THEN 'UNIQUE'
          ELSE ''
     END AS type,
     '(' || substring(
          pg_catalog.pg_get_indexdef (i.indexrelid, 0, true)
          FROM
               '\((.*)\)'
     ) || ')' AS columns
FROM
     pg_catalog.pg_class c,
     pg_catalog.pg_class c2,
     pg_catalog.pg_index i
     LEFT JOIN pg_catalog.pg_constraint con ON (
          conrelid = i.indrelid
          AND conindid = i.indexrelid
          AND contype IN ('p', 'u', 'x')
     )
WHERE
     c.oid = {}
     AND c.oid = i.indrelid
     AND i.indexrelid = c2.oid
ORDER BY
     i.indisprimary DESC,
     columns;
""").format(Literal(table.oid))

    log_sql("select_indexes_sql", sql)

    return Query(sql)


def select_publications_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
    pubname AS name,
    NULL AS column,
    NULL AS column
FROM pg_catalog.pg_publication p
     JOIN pg_catalog.pg_publication_namespace pn ON p.oid = pn.pnpubid
     JOIN pg_catalog.pg_class pc ON pc.relnamespace = pn.pnnspid
WHERE pc.oid = {} and pg_catalog.pg_relation_is_publishable({})
UNION
SELECT pubname
     , pg_get_expr(pr.prqual, c.oid)
     , (CASE WHEN pr.prattrs IS NOT NULL THEN
         (SELECT string_agg(attname, ', ')
           FROM pg_catalog.generate_series(0, pg_catalog.array_upper(pr.prattrs::pg_catalog.int2[], 1)) s,
                pg_catalog.pg_attribute
          WHERE attrelid = pr.prrelid AND attnum = prattrs[s])
        ELSE NULL END) FROM pg_catalog.pg_publication p
     JOIN pg_catalog.pg_publication_rel pr ON p.oid = pr.prpubid
     JOIN pg_catalog.pg_class c ON c.oid = pr.prrelid
WHERE pr.prrelid = {}
UNION
SELECT pubname
     , NULL
     , NULL
FROM pg_catalog.pg_publication p
WHERE p.puballtables AND pg_catalog.pg_relation_is_publishable({})
ORDER BY 1;
""").format(Literal(table.oid), Literal(table.oid), Literal(table.oid), Literal(table.oid))

    log_sql("select_publications_sql", sql)

    return Query(sql)


def select_referenced_by_foreign_keys_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
     conrelid::pg_catalog.regclass AS table,
     conname AS name,
     pg_catalog.pg_get_constraintdef(oid, true) AS reference
FROM
     pg_catalog.pg_constraint c
WHERE
     confrelid IN (
          SELECT
               pg_catalog.pg_partition_ancestors('19311')
          UNION ALL VALUES
               ({}::pg_catalog.regclass)
     )
     AND contype = 'f'
     AND conparentid = 0
ORDER BY 1;
""").format(Literal(table.oid))

    log_sql("select_referenced_by_foreign_keys_sql", sql)

    return Query(sql)


def select_table_oid_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
    c.oid
FROM
    pg_catalog.pg_class c
    LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
WHERE
    c.relname OPERATOR(pg_catalog.~) {} COLLATE pg_catalog.default
    AND n.nspname OPERATOR(pg_catalog.~) {} COLLATE pg_catalog.default
    AND pg_catalog.pg_table_is_visible(c.oid);
""").format(Literal(f"^({table.name})$"), Literal(f"^({table.schema_})$"))

    log_sql("select_table_oid_sql", sql)

    return Query(sql)


def select_table_stats_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
     reltuples::BIGINT AS row_estimate,
     pg_size_pretty (pg_relation_size (c.oid)) AS table_size,
     pg_size_pretty (pg_indexes_size (c.oid)) AS index_size,
     pg_size_pretty (pg_total_relation_size (c.oid)) AS total_size
FROM
     pg_class c
WHERE
     c.oid = {};
""").format(Literal(table.oid))

    log_sql("select_table_stats_sql", sql)

    return Query(sql)


def select_triggers_sql(table: PostgresTable) -> Query:
    sql: Composed = SQL("""
SELECT
     t.tgname AS name,
     substring(
          pg_get_triggerdef (t.oid, true)
          FROM
               'CREATE TRIGGER [^ ]+ (.+)'
     ) AS definition
FROM
     pg_catalog.pg_trigger t
WHERE
     t.tgrelid = {}
     AND (
          NOT t.tgisinternal
          OR (
               t.tgisinternal
               AND t.tgenabled = 'D'
          )
     )
ORDER BY
     1;
""").format(Literal(table.oid))

    log_sql("select_triggers_sql", sql)

    return Query(sql)
