import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.getenv("DACOOK_DATABASE", str(BASE_DIR / "data" / "dacook.db"))).resolve()
UPLOAD_DIR = Path(os.getenv("DACOOK_UPLOADS", str(BASE_DIR / "data" / "uploads"))).resolve()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def db():
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def rows(items):
    return [dict(item) for item in items]


def json_load(value, fallback):
    if value is None:
        return fallback
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
  avatar_path TEXT, is_admin INTEGER NOT NULL DEFAULT 0, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
  token TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at INTEGER NOT NULL, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS dish_cuisines (
  id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, emoji TEXT, ord INTEGER NOT NULL DEFAULT 0,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS dishes (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, image_path TEXT,
  tags TEXT NOT NULL DEFAULT '[]', cuisine_id TEXT REFERENCES dish_cuisines(id) ON DELETE SET NULL,
  source_url TEXT, status TEXT NOT NULL DEFAULT 'active', created_by TEXT REFERENCES users(id) ON DELETE SET NULL,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS dish_ingredients (
  id TEXT PRIMARY KEY, dish_id TEXT NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
  name TEXT NOT NULL, quantity TEXT, unit TEXT, ord INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS dish_steps (
  id TEXT PRIMARY KEY, dish_id TEXT NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
  ord INTEGER NOT NULL, body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meal_schedules (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, meal_type TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1,
  dining_time TEXT NOT NULL, create_lead_hours INTEGER NOT NULL DEFAULT 16,
  deadline_lead_minutes INTEGER NOT NULL DEFAULT 120, weekdays TEXT NOT NULL DEFAULT '[0,1,2,3,4,5,6]',
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS meals (
  id TEXT PRIMARY KEY, title TEXT, meal_type TEXT NOT NULL, date TEXT NOT NULL,
  dining_time INTEGER NOT NULL, order_deadline INTEGER NOT NULL,
  cook_id TEXT REFERENCES users(id) ON DELETE SET NULL, status TEXT NOT NULL DEFAULT 'ordering',
  is_auto INTEGER NOT NULL DEFAULT 0, schedule_id TEXT REFERENCES meal_schedules(id) ON DELETE SET NULL,
  created_by TEXT REFERENCES users(id) ON DELETE SET NULL, created_at INTEGER NOT NULL,
  UNIQUE(schedule_id, date)
);
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY, meal_id TEXT NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
  dish_id TEXT NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, note TEXT, created_at INTEGER NOT NULL,
  UNIQUE(meal_id, dish_id, user_id)
);
CREATE TABLE IF NOT EXISTS meal_dish_skips (
  meal_id TEXT NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
  dish_id TEXT NOT NULL REFERENCES dishes(id) ON DELETE CASCADE,
  skipped_by TEXT REFERENCES users(id) ON DELETE SET NULL, skipped_at INTEGER NOT NULL,
  PRIMARY KEY(meal_id, dish_id)
);
CREATE TABLE IF NOT EXISTS reviews (
  id TEXT PRIMARY KEY, meal_id TEXT NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  rating INTEGER NOT NULL, comment TEXT, created_at INTEGER NOT NULL,
  UNIQUE(meal_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date);
CREATE INDEX IF NOT EXISTS idx_orders_meal ON orders(meal_id);
CREATE INDEX IF NOT EXISTS idx_dishes_status ON dishes(status);
CREATE TABLE IF NOT EXISTS ingredient_canonical (
  id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS ingredient_aliases (
  id TEXT PRIMARY KEY, canonical_id TEXT NOT NULL REFERENCES ingredient_canonical(id) ON DELETE CASCADE,
  alias TEXT NOT NULL, created_at INTEGER NOT NULL, UNIQUE(canonical_id, alias)
);
CREATE INDEX IF NOT EXISTS idx_ingredient_aliases_canonical ON ingredient_aliases(canonical_id);
CREATE INDEX IF NOT EXISTS idx_ingredient_aliases_alias ON ingredient_aliases(alias);
"""


def init_db():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with db() as conn:
        conn.executescript(SCHEMA)
