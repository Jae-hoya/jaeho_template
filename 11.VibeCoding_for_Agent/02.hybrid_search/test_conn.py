import psycopg

conn_string = "postgresql://postgres:postgres@localhost:5433/postgres"
print(f"Connecting to: {conn_string}")

try:
    conn = psycopg.connect(conn_string)
    print("Connection successful!")

    # Test ParadeDB extensions
    cur = conn.cursor()
    cur.execute("SELECT extname FROM pg_extension WHERE extname IN ('vector', 'pg_search');")
    extensions = cur.fetchall()
    print(f"Available extensions: {extensions}")

    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
