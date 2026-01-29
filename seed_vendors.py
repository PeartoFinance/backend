"""
Vendor Seed Script - Real Data from Internet Research
Seeds database with real financial service providers across all categories
Run: python -c "from seed_vendors import seed_all_vendors; seed_all_vendors()"
"""
import uuid
from datetime import datetime, timezone
from app import create_app
from models import db, Vendor

# All vendor categories with real providers
VENDOR_DATA = {
    "Banking": [
        {"name": "JPMorgan Chase", "description": "Largest bank in the US, offering consumer and investment banking services.", "website": "https://www.chase.com", "services": ["Consumer Banking", "Investment Banking", "Wealth Management", "Credit Cards"]},
        {"name": "Bank of America", "description": "Major financial holding company with comprehensive banking and financial services.", "website": "https://www.bankofamerica.com", "services": ["Personal Banking", "Business Banking", "Mortgages", "Auto Loans"]},
        {"name": "Wells Fargo", "description": "One of the largest banks offering retail, commercial, and investment services.", "website": "https://www.wellsfargo.com", "services": ["Checking & Savings", "Home Loans", "Small Business", "Wealth Management"]},
        {"name": "Citibank", "description": "Global financial services with consumer and corporate banking solutions.", "website": "https://www.citi.com", "services": ["Personal Banking", "Credit Cards", "Wealth Management"]},
        {"name": "Ally Bank", "description": "Online-only bank known for competitive rates and no monthly fees.", "website": "https://www.ally.com", "services": ["Online Savings", "CDs", "Money Market", "Auto Loans"]},
        {"name": "Capital One", "description": "Digital banking with excellent mobile app and credit card offerings.", "website": "https://www.capitalone.com", "services": ["Checking", "Savings", "Credit Cards", "Auto Loans"]},
        {"name": "PNC Bank", "description": "Regional bank with strong digital tools and customer service.", "website": "https://www.pnc.com", "services": ["Personal Banking", "Business Banking", "Mortgages"]},
        {"name": "U.S. Bank", "description": "Fifth-largest bank in the US with comprehensive financial services.", "website": "https://www.usbank.com", "services": ["Personal Banking", "Business Banking", "Wealth Management"]},
    ],
    "Investment": [
        {"name": "Fidelity Investments", "description": "Top brokerage for beginners with low costs and extensive research tools.", "website": "https://www.fidelity.com", "services": ["Stock Trading", "ETFs", "Mutual Funds", "Retirement Planning"], "is_featured": True},
        {"name": "Charles Schwab", "description": "Leading discount brokerage with comprehensive investment services.", "website": "https://www.schwab.com", "services": ["Brokerage", "Robo-Advisor", "Financial Planning", "Banking"]},
        {"name": "Vanguard", "description": "Pioneer of low-cost index investing with minimal expense ratios.", "website": "https://www.vanguard.com", "services": ["Index Funds", "ETFs", "Retirement Accounts", "Financial Advice"]},
        {"name": "E*TRADE", "description": "Online brokerage with powerful trading platforms for all levels.", "website": "https://www.etrade.com", "services": ["Stock Trading", "Options", "Futures", "Managed Portfolios"]},
        {"name": "TD Ameritrade", "description": "Full-service brokerage known for thinkorswim trading platform.", "website": "https://www.tdameritrade.com", "services": ["Trading", "Research", "Education", "Retirement"]},
        {"name": "Robinhood", "description": "Commission-free trading app popular with younger investors.", "website": "https://www.robinhood.com", "services": ["Stocks", "Options", "Crypto", "Cash Management"]},
        {"name": "Interactive Brokers", "description": "Advanced platform for professional and active traders.", "website": "https://www.interactivebrokers.com", "services": ["Global Trading", "Margin", "APIs", "Prime Brokerage"]},
    ],
    "Insurance": [
        {"name": "State Farm", "description": "Largest auto and home insurer with exceptional customer satisfaction.", "website": "https://www.statefarm.com", "services": ["Auto Insurance", "Home Insurance", "Life Insurance", "Business Insurance"], "is_featured": True},
        {"name": "GEICO", "description": "Direct insurer known for competitive rates and digital service.", "website": "https://www.geico.com", "services": ["Auto Insurance", "Motorcycle", "Homeowners", "Renters"]},
        {"name": "Progressive", "description": "Innovative insurer with Name Your Price tool and Snapshot program.", "website": "https://www.progressive.com", "services": ["Auto Insurance", "Home Insurance", "Motorcycle", "Commercial"]},
        {"name": "USAA", "description": "Top-rated insurer exclusively serving military members and families.", "website": "https://www.usaa.com", "services": ["Auto Insurance", "Home Insurance", "Life Insurance", "Banking"]},
        {"name": "Allstate", "description": "Comprehensive personal lines insurer with local agents.", "website": "https://www.allstate.com", "services": ["Auto Insurance", "Home Insurance", "Life Insurance", "Condo Insurance"]},
        {"name": "Liberty Mutual", "description": "Major insurer offering bundling discounts and customizable coverage.", "website": "https://www.libertymutual.com", "services": ["Auto Insurance", "Home Insurance", "Umbrella", "Small Business"]},
        {"name": "Nationwide", "description": "Full-service insurer with strong pet and farm insurance options.", "website": "https://www.nationwide.com", "services": ["Auto", "Home", "Life", "Pet Insurance", "Farm"]},
        {"name": "MetLife", "description": "Leading life and health insurer with global presence.", "website": "https://www.metlife.com", "services": ["Life Insurance", "Dental", "Vision", "Disability"]},
    ],
    "Real Estate": [
        {"name": "Zillow", "description": "Largest real estate marketplace with home values, listings, and mortgage tools.", "website": "https://www.zillow.com", "services": ["Home Search", "Zestimate", "Mortgage", "Agent Directory"], "is_featured": True},
        {"name": "Redfin", "description": "Technology-driven brokerage with lower listing fees and agent rebates.", "website": "https://www.redfin.com", "services": ["Buying", "Selling", "Mortgage", "Home Tours"]},
        {"name": "Coldwell Banker", "description": "Well-established brokerage with global network of agents.", "website": "https://www.coldwellbanker.com", "services": ["Residential Sales", "Luxury Homes", "Commercial", "Property Management"]},
        {"name": "Keller Williams", "description": "Largest real estate franchise with extensive agent training programs.", "website": "https://www.kw.com", "services": ["Residential", "Commercial", "Luxury", "Land"]},
        {"name": "Compass", "description": "Modern brokerage with cutting-edge technology platform.", "website": "https://www.compass.com", "services": ["Buying", "Selling", "Concierge Services", "Market Analysis"]},
        {"name": "RE/MAX", "description": "Global real estate network with experienced agents.", "website": "https://www.remax.com", "services": ["Residential", "Commercial", "Luxury", "Relocation"]},
    ],
    "Tax Services": [
        {"name": "TurboTax", "description": "Leading tax software with step-by-step guidance and expert help.", "website": "https://turbotax.intuit.com", "services": ["Online Filing", "Expert Review", "Self-Employed", "Live Help"], "is_featured": True},
        {"name": "H&R Block", "description": "Tax preparation with both in-person and online options.", "website": "https://www.hrblock.com", "services": ["Tax Filing", "In-Person Help", "Online Filing", "Small Business"]},
        {"name": "Jackson Hewitt", "description": "Budget-friendly tax preparation with Walmart locations.", "website": "https://www.jacksonhewitt.com", "services": ["Tax Filing", "Refund Advance", "Year-Round Support"]},
        {"name": "TaxAct", "description": "Affordable tax software with accuracy guarantee.", "website": "https://www.taxact.com", "services": ["Online Filing", "Download Software", "Professional"]},
        {"name": "FreeTaxUSA", "description": "Free federal filing with very affordable state returns.", "website": "https://www.freetaxusa.com", "services": ["Free Filing", "All Forms Included", "Audit Support"]},
    ],
    "Crypto": [
        {"name": "Coinbase", "description": "Most popular US crypto exchange, beginner-friendly with 250+ coins.", "website": "https://www.coinbase.com", "services": ["Buy/Sell Crypto", "Staking", "Wallet", "Advanced Trading"], "is_featured": True},
        {"name": "Kraken", "description": "Advanced crypto exchange for experienced traders with low fees.", "website": "https://www.kraken.com", "services": ["Spot Trading", "Margin Trading", "Futures", "Staking"]},
        {"name": "Gemini", "description": "Security-focused exchange founded by Winklevoss twins.", "website": "https://www.gemini.com", "services": ["Buy/Sell Crypto", "Earn Interest", "NFTs", "ActiveTrader"]},
        {"name": "Crypto.com", "description": "All-in-one crypto platform with rewards card and DeFi wallet.", "website": "https://www.crypto.com", "services": ["Exchange", "Crypto Card", "Earn", "DeFi Wallet"]},
    ],
    "Retirement": [
        {"name": "TIAA", "description": "Retirement provider for education and non-profit sector employees.", "website": "https://www.tiaa.org", "services": ["403(b) Plans", "IRAs", "Annuities", "Financial Advice"]},
        {"name": "Empower", "description": "Full-service retirement platform with personalized planning.", "website": "https://www.empower.com", "services": ["401(k)", "IRA", "Wealth Management", "Financial Planning"]},
        {"name": "Principal", "description": "Retirement and employee benefits solutions for businesses.", "website": "https://www.principal.com", "services": ["401(k)", "Pension", "Insurance", "Investments"]},
    ],
    "Education": [
        {"name": "Coursera", "description": "Online learning platform with courses from top universities.", "website": "https://www.coursera.org", "services": ["Online Courses", "Certificates", "Degrees", "Business Training"]},
        {"name": "Udemy", "description": "Marketplace for online courses on any topic.", "website": "https://www.udemy.com", "services": ["Video Courses", "Lifetime Access", "Business Plans"]},
        {"name": "LinkedIn Learning", "description": "Professional development courses integrated with LinkedIn.", "website": "https://www.linkedin.com/learning", "services": ["Business Skills", "Technology", "Creative Skills"]},
    ],
    "Technology": [
        {"name": "Intuit QuickBooks", "description": "Leading small business accounting software.", "website": "https://quickbooks.intuit.com", "services": ["Accounting", "Payroll", "Payments", "Time Tracking"]},
        {"name": "Xero", "description": "Cloud accounting software for small businesses.", "website": "https://www.xero.com", "services": ["Accounting", "Bank Reconciliation", "Invoicing", "Payroll"]},
        {"name": "Mint", "description": "Free budgeting and expense tracking app.", "website": "https://mint.intuit.com", "services": ["Budget Tracking", "Bill Pay", "Credit Score", "Investments"]},
    ],
    "Legal": [
        {"name": "LegalZoom", "description": "Online legal services for individuals and businesses.", "website": "https://www.legalzoom.com", "services": ["Business Formation", "Wills & Trusts", "Trademarks", "Legal Advice"]},
        {"name": "Rocket Lawyer", "description": "Affordable legal documents and attorney consultations.", "website": "https://www.rocketlawyer.com", "services": ["Legal Documents", "Attorney Access", "Business Formation"]},
    ],
    "Marketing": [
        {"name": "HubSpot", "description": "All-in-one marketing, sales, and CRM platform.", "website": "https://www.hubspot.com", "services": ["CRM", "Marketing Automation", "Sales Tools", "Content Management"]},
        {"name": "Mailchimp", "description": "Email marketing and automation platform for small businesses.", "website": "https://www.mailchimp.com", "services": ["Email Marketing", "Automation", "Landing Pages", "Ads"]},
    ],
    "Travel": [
        {"name": "Expedia", "description": "Online travel agency for flights, hotels, and vacation packages.", "website": "https://www.expedia.com", "services": ["Flights", "Hotels", "Car Rentals", "Vacations"]},
        {"name": "Booking.com", "description": "Global accommodation booking platform.", "website": "https://www.booking.com", "services": ["Hotels", "Apartments", "Flights", "Car Rentals"]},
    ],
    "Health": [
        {"name": "Kaiser Permanente", "description": "Top-rated health insurance and healthcare provider.", "website": "https://www.kaiserpermanente.org", "services": ["Health Insurance", "Medical Care", "Pharmacy", "Telehealth"]},
        {"name": "UnitedHealthcare", "description": "Largest health insurer by premiums with extensive network.", "website": "https://www.uhc.com", "services": ["Health Insurance", "Medicare", "Medicaid", "Dental"]},
        {"name": "Blue Cross Blue Shield", "description": "Federation of health insurers with nationwide coverage.", "website": "https://www.bcbs.com", "services": ["Health Insurance", "Medicare", "Dental", "Vision"]},
    ],
}


def seed_all_vendors():
    """Seed database with all vendors from research data."""
    app = create_app()
    
    with app.app_context():
        created = 0
        updated = 0
        
        for category, vendors in VENDOR_DATA.items():
            for v_data in vendors:
                # Check if vendor exists by name
                existing = Vendor.query.filter_by(name=v_data['name']).first()
                
                if existing:
                    # Update existing vendor
                    existing.category = category
                    existing.description = v_data['description']
                    existing.website = v_data.get('website')
                    existing.services = v_data.get('services', [])
                    existing.is_featured = v_data.get('is_featured', False)
                    existing.updated_at = datetime.now(timezone.utc)
                    updated += 1
                else:
                    # Create new vendor
                    new_vendor = Vendor(
                        id=str(uuid.uuid4()),
                        name=v_data['name'],
                        description=v_data['description'],
                        category=category,
                        website=v_data.get('website'),
                        services=v_data.get('services', []),
                        is_featured=v_data.get('is_featured', False),
                        rating=4.0 + (hash(v_data['name']) % 10) / 10,  # Random 4.0-4.9
                        review_count=10 + (hash(v_data['name']) % 990),  # Random 10-999
                        status='active',
                        country_code='US',
                        created_at=datetime.now(timezone.utc)
                    )
                    db.session.add(new_vendor)
                    created += 1
        
        db.session.commit()
        print(f"✅ Vendor seeding complete: {created} created, {updated} updated")
        print(f"📊 Categories: {list(VENDOR_DATA.keys())}")
        return {'created': created, 'updated': updated}


if __name__ == '__main__':
    seed_all_vendors()
