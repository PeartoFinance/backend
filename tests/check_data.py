
from app import app, db
from models import CommodityData, ForexRate

with app.app_context():
    try:
        commodities_count = CommodityData.query.count()
        forex_count = ForexRate.query.count()
        print(f"CommodityData count: {commodities_count}")
        print(f"ForexRate count: {forex_count}")
        
        if commodities_count > 0:
            print("Sample Commodity:", CommodityData.query.first().to_dict())
            
        if forex_count > 0:
            print("Sample Forex:", ForexRate.query.first().to_dict())
            
    except Exception as e:
        print(f"Error: {e}")
