
import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from handlers.market_data.forex_handler import import_forex_to_db, COMMON_CURRENCIES

app = create_app()

with app.app_context():
    print("Importing Common Forex Rates...")
    # Import common currencies
    results = import_forex_to_db(list(COMMON_CURRENCIES.keys()))
    print(f"Imported: {results['updated']}, Errors: {results['errors']}")
    print("Done.")
