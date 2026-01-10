import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('DB_HOST', 'localhost')
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
db_name = os.getenv('DB_NAME', 'pearto')

try:
    conn = pymysql.connect(host=host, user=user, password=password, database=db_name)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    if tables:
        print("Tables found:")
        for t in tables:
            print(f" - {t[0]}")
    else:
        print("No tables found in database.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
