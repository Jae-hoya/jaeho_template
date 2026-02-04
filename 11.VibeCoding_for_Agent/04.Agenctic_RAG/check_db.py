from dotenv import load_dotenv
import os
import psycopg


def main() -> None:
    load_dotenv(r"C:\Users\skyop\jaeho_template\.env")

    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5433/postgres",
    )

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print("version:", version)

            cur.execute("SELECT COUNT(*) FROM loan_products")
            count = cur.fetchone()[0]
            print("rows:", count)


if __name__ == "__main__":
    main()
