import aiosqlite
import json
import os
from datetime import datetime

DATABASE_PATH = os.getenv("DATABASE_URL", "./formpilot.db")


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path TEXT NOT NULL,
                user_context TEXT NOT NULL,
                fields_json TEXT NOT NULL,
                summary TEXT,
                is_mock INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_analysis(
    image_path: str,
    user_context: str,
    fields: list,
    summary: str | None = None,
    is_mock: bool = False,
) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO analyses (image_path, user_context, fields_json, summary, is_mock, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                image_path,
                user_context,
                json.dumps(fields),
                summary,
                1 if is_mock else 0,
                datetime.utcnow().isoformat(),
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_analysis(analysis_id: int) -> dict | None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            result = dict(row)
            result["fields"] = json.loads(result["fields_json"])
            result["is_mock"] = bool(result["is_mock"])
            result["created_at"] = datetime.fromisoformat(result["created_at"])
            return result


async def list_analyses(limit: int = 50, offset: int = 0) -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT id, user_context, fields_json, image_path, created_at
            FROM analyses
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ) as cursor:
            rows = await cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                fields = json.loads(item["fields_json"])
                results.append(
                    {
                        "id": item["id"],
                        "user_context": item["user_context"],
                        "field_count": len(fields),
                        "created_at": datetime.fromisoformat(item["created_at"]),
                        "thumbnail_path": item["image_path"],
                    }
                )
            return results
