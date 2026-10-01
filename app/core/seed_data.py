from app.core.database import get_connection, initialize_database


SALES_DATA = [
    # North
    ("North", "Beverages", "Q1", 2025, 125000, 12500),
    ("North", "Beverages", "Q2", 2025, 138000, 13800),
    ("North", "Beverages", "Q3", 2025, 145000, 14500),
    ("North", "Snacks", "Q1", 2025, 98000, 9800),
    ("North", "Snacks", "Q2", 2025, 105000, 10500),
    ("North", "Snacks", "Q3", 2025, 110000, 11000),

    # South
    ("South", "Beverages", "Q1", 2025, 142000, 14200),
    ("South", "Beverages", "Q2", 2025, 135000, 13500),
    ("South", "Beverages", "Q3", 2025, 118000, 11800),
    ("South", "Snacks", "Q1", 2025, 115000, 11500),
    ("South", "Snacks", "Q2", 2025, 108000, 10800),
    ("South", "Snacks", "Q3", 2025, 95000, 9500),

    # East
    ("East", "Beverages", "Q1", 2025, 108000, 10800),
    ("East", "Beverages", "Q2", 2025, 112000, 11200),
    ("East", "Beverages", "Q3", 2025, 116000, 11600),
    ("East", "Snacks", "Q1", 2025, 87000, 8700),
    ("East", "Snacks", "Q2", 2025, 92000, 9200),
    ("East", "Snacks", "Q3", 2025, 97000, 9700),

    # West
    ("West", "Beverages", "Q1", 2025, 132000, 13200),
    ("West", "Beverages", "Q2", 2025, 128000, 12800),
    ("West", "Beverages", "Q3", 2025, 124000, 12400),
    ("West", "Snacks", "Q1", 2025, 101000, 10100),
    ("West", "Snacks", "Q2", 2025, 98000, 9800),
    ("West", "Snacks", "Q3", 2025, 94000, 9400),
]


def seed_database():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM sales")

    cursor.executemany(
        """
        INSERT INTO sales
        (region, product, quarter, year, revenue, units_sold)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        SALES_DATA,
    )

    connection.commit()
    connection.close()

    print(f"Inserted {len(SALES_DATA)} sales records.")


if __name__ == "__main__":
    seed_database()