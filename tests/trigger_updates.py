from app import app
from jobs.market_jobs import update_all_forex, update_all_commodities

print("Starting manual update...")
with app.app_context():
    print("Updating Forex...")
    res_forex = update_all_forex()
    print(f"Forex Result: {res_forex}")
    
    print("Updating Commodities...")
    res_comm = update_all_commodities()
    print(f"Commodities Result: {res_comm}")

print("Done.")
