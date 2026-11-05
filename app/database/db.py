import sqlite3
from pathlib import Path


# =========================================================
# DATABASE LOCATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    exist_ok=True
)

DATABASE_PATH = DATA_DIR / "lumora.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Create and return a connection to Lumora's SQLite database.
    """

    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()


    # -----------------------------------------------------
    # CONVERSATIONS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # -----------------------------------------------------
    # MESSAGES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id INTEGER NOT NULL,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (
                conversation_id
            )
            REFERENCES conversations(id)

        )
    """)


    # -----------------------------------------------------
    # MEMORIES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            note TEXT,

            media_path TEXT,

            memory_date TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # =====================================================
    # MEMORY TYPE MIGRATION
    # =====================================================

    cursor.execute("""
        PRAGMA table_info(memories)
    """)

    memory_columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "memory_type" not in memory_columns:

        cursor.execute("""
            ALTER TABLE memories
            ADD COLUMN memory_type TEXT DEFAULT 'media'
        """)

        cursor.execute("""
            UPDATE memories
            SET memory_type = 'media'
            WHERE memory_type IS NULL
               OR memory_type = ''
        """)


    # =====================================================
    # CONVERT OLD TEXT MEMORIES
    # =====================================================

    cursor.execute("""
        UPDATE memories
        SET memory_type = 'long_term'
        WHERE (
            media_path IS NULL
            OR media_path = ''
        )
        AND memory_type = 'media'
    """)
    # =====================================================
    # MEMORY CATEGORY MIGRATION
    # =====================================================

    cursor.execute("""
        PRAGMA table_info(memories)
    """)

    memory_columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "category" not in memory_columns:

        cursor.execute("""
            ALTER TABLE memories
            ADD COLUMN category TEXT DEFAULT 'general'
        """)

        cursor.execute("""
            UPDATE memories
            SET category = 'general'
            WHERE category IS NULL
               OR category = ''
        """)


    # -----------------------------------------------------
    # IMPORTANT DATES
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS important_dates (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            date TEXT NOT NULL,

            note TEXT,

            reminder_enabled INTEGER DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    connection.commit()

    connection.close()