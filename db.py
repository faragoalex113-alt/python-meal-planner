# db.py
import sqlite3
from typing import Optional


class FoodDB:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def list_by_category(self, category: str) -> list[dict]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, category, serving_gml, kcal, kj,
                       protein_g, carbs_g, sugar_g, fat_g, sat_fat_g, fiber_g, salt_g
                FROM foods
                WHERE category = ?
                ORDER BY name
                """,
                (category,),
            )
            rows = cur.fetchall()

        return [self._row_to_dict(r) for r in rows]

    def search_by_name(self, query: str, limit: int = 25) -> list[dict]:
        q = f"%{query.strip()}%"
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, category, serving_gml, kcal, kj,
                       protein_g, carbs_g, sugar_g, fat_g, sat_fat_g, fiber_g, salt_g
                FROM foods
                WHERE name LIKE ?
                ORDER BY name
                LIMIT ?
                """,
                (q, limit),
            )
            rows = cur.fetchall()

        return [self._row_to_dict(r) for r in rows]

    def get_by_id(self, food_id: int) -> Optional[dict]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, name, category, serving_gml, kcal, kj,
                       protein_g, carbs_g, sugar_g, fat_g, sat_fat_g, fiber_g, salt_g
                FROM foods
                WHERE id = ?
                """,
                (food_id,),
            )
            row = cur.fetchone()

        return self._row_to_dict(row) if row else None

    @staticmethod
    def _row_to_dict(r) -> dict:
        return {
            "id": r[0],
            "name": r[1],
            "category": r[2],
            "serving_gml": r[3],
            "kcal": int(r[4]) if r[4] is not None else 0,
            "kj": r[5],
            "protein_g": r[6] or 0.0,
            "carbs_g": r[7] or 0.0,
            "sugar_g": r[8] or 0.0,
            "fat_g": r[9] or 0.0,
            "sat_fat_g": r[10] or 0.0,
            "fiber_g": r[11] or 0.0,
            "salt_g": r[12] or 0.0,
        }