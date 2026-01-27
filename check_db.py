
from app import create_app
from models import db, CompanyFinancials, AnalystRecommendation

def check_db():
    app = create_app()
    with app.app_context():
        print("--- Database Verification ---")
        
        # Check Financials
        fins = CompanyFinancials.query.all()
        print(f"Total Financial Records: {len(fins)}")
        for f in fins[:2]:
            print(f" - {f.symbol}: {f.fiscal_date_ending} (Revenue: {f.revenue})")
            
        # Check Forecasts
        recs = AnalystRecommendation.query.all()
        print(f"\nTotal Forecast Records: {len(recs)}")
        for r in recs[:2]:
            print(f" - {r.symbol}: Buy={r.buy}, Sell={r.sell} (Target Mean: {r.target_mean})")

if __name__ == "__main__":
    check_db()