from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from crawler.config import DbConfig
from crawler.schema_sqlite import SCHEMA_SQLITE


@dataclass
class Database:
    config: DbConfig
    conn: sqlite3.Connection | object

    @staticmethod
    def connect(config: DbConfig) -> "Database":
        if config.engine == "sqlite":
            assert config.path is not None
            conn = sqlite3.connect(config.path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return Database(config=config, conn=conn)

        if config.engine == "mysql":
            import pymysql

            conn = pymysql.connect(
                host=config.host,
                port=config.port or 3306,
                user=config.user,
                password=config.password,
                database=config.database,
                autocommit=False,
                cursorclass=pymysql.cursors.DictCursor,
            )
            return Database(config=config, conn=conn)

        raise ValueError("unsupported engine")

    def bootstrap(self) -> None:
        if self.config.engine != "sqlite":
            return
        statements = [s.strip() for s in SCHEMA_SQLITE.split(";") if s.strip()]
        for stmt in statements:
            self.execute(stmt)
        self.commit()

    def execute(self, sql: str, params: tuple | list | None = None) -> int:
        params = params or ()
        if self.config.engine == "sqlite":
            cursor = self.conn.execute(sql, params)
            return cursor.rowcount

        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.rowcount

    def fetchall(self, sql: str, params: tuple | list | None = None) -> list[dict]:
        params = params or ()
        if self.config.engine == "sqlite":
            cursor = self.conn.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return list(rows)

    def fetchone(self, sql: str, params: tuple | list | None = None) -> dict | None:
        rows = self.fetchall(sql, params)
        return rows[0] if rows else None

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()

    def close(self) -> None:
        self.conn.close()
