import sys
from pathlib import Path

# Force Python to include the project root in its import search path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.database.connection import get_connection


def main():
    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO sources
                    (source_name, source_type, source_url)
                VALUES
                    (%s, %s, %s)
                ON CONFLICT (source_name)
                DO NOTHING;
                """,
                (
                    "Demo Source",
                    "test",
                    "https://example.com",
                ),
            )

        connection.commit()

    print("Seed data inserted successfully.")


if __name__ == "__main__":
    main()