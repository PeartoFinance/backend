import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('DB_HOST', 'localhost')
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASSWORD', '')
db_name = os.getenv('DB_NAME', 'pearto')

try:
    # Connect without database first
    conn = pymysql.connect(host=host, user=user, password=password)
    cursor = conn.cursor()
    
    # Create database if not exists
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"SUCCESS: Database '{db_name}' is ready.")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"ERROR: {e}")
    if "1045" in str(e):
        print("TIP: Your MySQL 'root' user likely has a password. Please enter it in the .env file at DB_PASSWORD.")
    elif "2003" in str(e):
        print("TIP: MySQL server is not running. Please start it (XAMPP, WAMP, or MySQL Service).")
