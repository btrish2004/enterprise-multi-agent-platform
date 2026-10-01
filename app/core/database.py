import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/sales.db")


def get_connection():
    """Create a connection to the sales database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the sales table if it does not exist."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT NOT NULL,
            product TEXT NOT NULL,
            quarter TEXT NOT NULL,
            year INTEGER NOT NULL,
            revenue REAL NOT NULL,
            units_sold INTEGER NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DATABASE_PATH}")