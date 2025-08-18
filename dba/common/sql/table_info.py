from psycopg.sql import SQL, Composed, Literal

from dba.common.sql import Query
from dba.models import PostgresTable


def select_check_constraints_query(table: PostgresTable) -> Query:
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

    return Query(sql)


def select_column_count_query(table: PostgresTable) -> Query:
    sql: Composed = SQL(
        "SELECT COUNT(1) FROM information_schema.columns WHERE table_schema = {} AND table_name = {};"
    ).format(Literal(table.schema_), Literal(table.name))

    return Query(sql)


def select_column_definition_query(table: PostgresTable) -> Query:
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

    return Query(sql)


def select_foreign_keys_query(table: PostgresTable) -> Query:
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

    return Query(sql)


def select_indexes_query(table: PostgresTable) -> Query:
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

    return Query(sql)


def select_referenced_by_foreign_keys_query(table: PostgresTable) -> Query:
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

    return Query(sql)


def select_table_oid_query(table: PostgresTable) -> Query:
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

    return Query(sql)


def select_table_stats_query(table: PostgresTable) -> Query:
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

    return Query(sql)


def select_triggers_query(table: PostgresTable) -> Query:
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

    return Query(sql)
