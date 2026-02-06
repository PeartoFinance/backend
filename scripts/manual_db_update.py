
import os
import sys
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'pearto'),
        port=int(os.getenv('DB_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

def update_schema():
    print("Starting manual schema update...")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Check if ytd_return column exists in market_data
        print("Checking market_data table for ytd_return column...")
        cursor.execute("""
            SELECT count(*) as count 
            FROM information_schema.columns 
            WHERE table_schema = %s 
            AND table_name = 'market_data' 
            AND column_name = 'ytd_return'
        """, (os.getenv('DB_NAME', 'pearto'),))
        
        result = cursor.fetchone()
        
        if result['count'] == 0:
            print("Column ytd_return not found. Adding it...")
            try:
                cursor.execute("""
                    ALTER TABLE market_data 
                    ADD COLUMN ytd_return DECIMAL(10, 4) NULL COMMENT 'Year-to-Date return percentage'
                """)
                conn.commit()
                print("Successfully added ytd_return column to market_data.")
            except Exception as e:
                print(f"Error adding column: {e}")
                conn.rollback()
        else:
            print("Column ytd_return already exists. Skipping.")
            
        # 2. Add indexes if they don't exist
        # idx_market_country
        try:
            print("Checking/Adding idx_market_country...")
            cursor.execute("""
                CREATE INDEX idx_market_country ON market_data (country_code, asset_type)
            """)
            conn.commit()
            print("Created idx_market_country.")
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1061: # Duplicate key name
                print("Index idx_market_country already exists.")
            else:
                print(f"Error creating index: {e}")

        # idx_market_movers
        try:
            print("Checking/Adding idx_market_movers...")
            cursor.execute("""
                CREATE INDEX idx_market_movers ON market_data (asset_type, is_listed, change_percent)
            """)
            conn.commit()
            print("Created idx_market_movers.")
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1061:
                print("Index idx_market_movers already exists.")
            else:
                print(f"Error creating index: {e}")

        # idx_market_volume
        try:
            print("Checking/Adding idx_market_volume...")
            cursor.execute("""
                CREATE INDEX idx_market_volume ON market_data (asset_type, is_listed, volume)
            """)
            conn.commit()
            print("Created idx_market_volume.")
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1061:
                print("Index idx_market_volume already exists.")
            else:
                print(f"Error creating index: {e}")
                
        print("Schema update completed successfully.")
        
    except Exception as e:
        print(f"Critical error connecting to database: {e}")
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

if __name__ == "__main__":
    update_schema()
