"""
Seed script for Glossary Terms and Help Center data.
Migrates the 25 hardcoded glossary terms + help categories/articles.

Usage:
  cd backend && python seed_glossary_help.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models.base import db
from models.misc import GlossaryTerm
from models.education import HelpCategory, HelpArticle
from datetime import datetime

# ── Glossary terms (migrated from frontend hardcoded list) ──
GLOSSARY_TERMS = [
    {"term": "APR", "definition": "Annual Percentage Rate - The yearly interest rate charged on borrowed money or earned through investments.", "category": "banking"},
    {"term": "APY", "definition": "Annual Percentage Yield - The real rate of return earned on an investment, taking compound interest into account.", "category": "banking"},
    {"term": "Bear Market", "definition": "A market condition where prices are falling or expected to fall, typically by 20% or more from recent highs.", "category": "trading"},
    {"term": "Blue Chip", "definition": "Shares of large, well-established, financially stable companies with a history of reliable growth.", "category": "investing"},
    {"term": "Bond", "definition": "A fixed-income instrument representing a loan made by an investor to a borrower, typically corporate or governmental.", "category": "investing"},
    {"term": "Bull Market", "definition": "A market condition where prices are rising or expected to rise, characterized by optimism and investor confidence.", "category": "trading"},
    {"term": "Compound Interest", "definition": "Interest calculated on both the initial principal and the accumulated interest from previous periods.", "category": "banking"},
    {"term": "Dividend", "definition": "A portion of a company's earnings distributed to shareholders, usually paid quarterly.", "category": "investing"},
    {"term": "Diversification", "definition": "A risk management strategy that mixes a variety of investments within a portfolio to reduce overall risk.", "category": "investing"},
    {"term": "ETF", "definition": "Exchange-Traded Fund - A type of security that tracks an index, commodity, or basket of assets and trades like a stock on an exchange.", "category": "investing"},
    {"term": "Equity", "definition": "Ownership interest in a company, represented by shares of stock.", "category": "investing"},
    {"term": "FDIC", "definition": "Federal Deposit Insurance Corporation - A US government agency that insures deposits in banks and savings associations up to $250,000.", "category": "banking"},
    {"term": "Hedge", "definition": "An investment made to reduce the risk of adverse price movements in an asset, often using derivatives.", "category": "derivatives"},
    {"term": "Index Fund", "definition": "A mutual fund or ETF designed to follow certain preset rules to track a specified basket of investments such as the S&P 500.", "category": "investing"},
    {"term": "IPO", "definition": "Initial Public Offering - The first time a company sells shares of stock to the public on a stock exchange.", "category": "investing"},
    {"term": "Liquidity", "definition": "How quickly and easily an asset can be converted into cash without significantly affecting its market price.", "category": "trading"},
    {"term": "Market Cap", "definition": "Market Capitalization - The total market value of a company's outstanding shares of stock, calculated as share price times number of shares.", "category": "investing"},
    {"term": "Mutual Fund", "definition": "An investment vehicle made up of a pool of funds collected from many investors to invest in securities like stocks, bonds, and other assets.", "category": "investing"},
    {"term": "P/E Ratio", "definition": "Price-to-Earnings Ratio - A valuation measure comparing a company's stock price to its earnings per share, used to assess if a stock is over or undervalued.", "category": "investing"},
    {"term": "Portfolio", "definition": "A collection of financial investments like stocks, bonds, commodities, cash, and cash equivalents held by an individual or institution.", "category": "investing"},
    {"term": "ROI", "definition": "Return on Investment - A performance measure used to evaluate the efficiency or profitability of an investment, expressed as a percentage.", "category": "investing"},
    {"term": "SEC", "definition": "Securities and Exchange Commission - The US government regulatory agency overseeing the securities industry, protecting investors and maintaining fair markets.", "category": "economics"},
    {"term": "SIP", "definition": "Systematic Investment Plan - A method of investing a fixed amount regularly in mutual funds, enabling rupee cost averaging.", "category": "investing"},
    {"term": "Volatility", "definition": "A statistical measure of the dispersion of returns for a given security or market index, indicating the degree of variation in price.", "category": "trading"},
    {"term": "Yield", "definition": "The income return on an investment, such as interest or dividends received, expressed as a percentage of the investment's cost or current value.", "category": "investing"},
    # Additional useful terms
    {"term": "Ask Price", "definition": "The lowest price a seller is willing to accept for a security. Also known as the offer price.", "category": "trading"},
    {"term": "Bid Price", "definition": "The highest price a buyer is willing to pay for a security at a given time.", "category": "trading"},
    {"term": "Spread", "definition": "The difference between the bid price and ask price of a security, representing the transaction cost.", "category": "trading"},
    {"term": "Leverage", "definition": "The use of borrowed capital to increase the potential return of an investment. Higher leverage means higher risk.", "category": "derivatives"},
    {"term": "Margin", "definition": "The amount of equity a trader must deposit with a broker as collateral to borrow funds for trading.", "category": "derivatives"},
    {"term": "Short Selling", "definition": "A trading strategy where an investor borrows and sells a security, hoping to buy it back at a lower price to profit from the decline.", "category": "trading"},
    {"term": "Stop Loss", "definition": "An order placed to sell a security when it reaches a certain price, designed to limit an investor's loss on a position.", "category": "trading"},
    {"term": "Cryptocurrency", "definition": "A digital or virtual currency that uses cryptography for security and operates on a decentralized network, typically blockchain.", "category": "crypto"},
    {"term": "Blockchain", "definition": "A distributed, decentralized, public ledger technology that records transactions across many computers in a way that cannot be altered retroactively.", "category": "crypto"},
    {"term": "DeFi", "definition": "Decentralized Finance - Financial services built on blockchain technology that operate without traditional intermediaries like banks.", "category": "crypto"},
    {"term": "Staking", "definition": "The process of locking up cryptocurrency holdings to support blockchain operations and earn rewards, similar to earning interest.", "category": "crypto"},
    {"term": "GDP", "definition": "Gross Domestic Product - The total monetary value of all finished goods and services produced within a country's borders in a specific time period.", "category": "economics"},
    {"term": "Inflation", "definition": "The rate at which the general level of prices for goods and services rises, eroding purchasing power over time.", "category": "economics"},
    {"term": "Interest Rate", "definition": "The amount charged by a lender to a borrower for the use of assets, expressed as a percentage of the principal.", "category": "economics"},
    {"term": "Technical Analysis", "definition": "A method of evaluating securities by analyzing statistics generated by market activity, such as past prices and volume.", "category": "technical"},
    {"term": "Moving Average", "definition": "A calculation used in technical analysis to smooth out price data by creating a constantly updated average price over a specific time period.", "category": "technical"},
    {"term": "RSI", "definition": "Relative Strength Index - A momentum oscillator that measures the speed and change of price movements on a scale of 0 to 100.", "category": "technical"},
    {"term": "MACD", "definition": "Moving Average Convergence Divergence - A trend-following momentum indicator showing the relationship between two moving averages of a security's price.", "category": "technical"},
    {"term": "Support Level", "definition": "A price level where a downtrend can be expected to pause due to a concentration of demand or buying interest.", "category": "technical"},
    {"term": "Resistance Level", "definition": "A price level where an uptrend can be expected to pause due to a concentration of supply or selling interest.", "category": "technical"},
]

# ── Help Categories ──
HELP_CATEGORIES = [
    {
        "name": "Getting Started",
        "slug": "getting-started",
        "icon": "rocket",
        "description": "Learn the basics of using Pearto Finance",
        "order_index": 1,
        "articles": [
            {
                "title": "How to create an account",
                "slug": "how-to-create-an-account",
                "content": "Creating a Pearto Finance account is quick and easy.\n\n1. Click the 'Sign Up' button on the homepage\n2. Enter your email address and create a password\n3. Verify your email by clicking the link sent to your inbox\n4. Complete your profile with your name and preferences\n5. You're ready to start exploring!\n\nYou can also sign up using Google or Apple for a faster experience.",
                "is_featured": True,
            },
            {
                "title": "Setting up your profile",
                "slug": "setting-up-your-profile",
                "content": "Personalize your Pearto experience by setting up your profile.\n\n1. Go to Settings from the sidebar or your avatar menu\n2. Upload a profile photo\n3. Set your preferred currency and country\n4. Choose your investment interests (stocks, crypto, forex, etc.)\n5. Configure notification preferences\n\nA complete profile helps us tailor market data and news to your interests.",
                "is_featured": False,
            },
            {
                "title": "Navigating the dashboard",
                "slug": "navigating-the-dashboard",
                "content": "Your dashboard is your command center for all things finance.\n\n• Sidebar: Access all major sections like Stocks, Crypto, News, Tools\n• Ticker Tape: Live scrolling prices of major indices at the top\n• Watchlist: Your personalized list of followed securities\n• Market Overview: Quick snapshot of major markets\n• News Feed: Latest financial news filtered to your interests\n\nUse the search bar at the top to quickly find any stock, crypto, or tool.",
                "is_featured": True,
            },
        ]
    },
    {
        "name": "Account & Billing",
        "slug": "account-and-billing",
        "icon": "credit-card",
        "description": "Manage your subscription, payments, and account settings",
        "order_index": 2,
        "articles": [
            {
                "title": "Managing your subscription",
                "slug": "managing-your-subscription",
                "content": "Pearto offers both free and premium subscription tiers.\n\nFree Tier:\n• Basic market data with slight delay\n• Limited watchlist (10 securities)\n• Standard news access\n\nPremium Tier:\n• Real-time market data\n• Unlimited watchlist\n• Advanced charting tools\n• AI-powered insights\n• Priority support\n\nTo change your plan, go to Settings > Subscription. Changes take effect at the start of your next billing cycle.",
                "is_featured": True,
            },
            {
                "title": "Payment methods",
                "slug": "payment-methods",
                "content": "We accept the following payment methods:\n\n• Credit/Debit Cards (Visa, Mastercard, American Express)\n• PayPal\n• Bank Transfer (for annual plans)\n\nTo add or update your payment method:\n1. Go to Settings > Billing\n2. Click 'Update Payment Method'\n3. Enter your new payment details\n4. Click Save\n\nAll payments are processed securely through Stripe. We never store your full card details.",
                "is_featured": False,
            },
            {
                "title": "Refund policy",
                "slug": "refund-policy",
                "content": "We want you to be satisfied with Pearto Finance.\n\n• Monthly plans: Cancel anytime, no refunds for partial months\n• Annual plans: Full refund within 14 days of purchase\n• Pro-rated refunds may be available for annual plans after 14 days\n\nTo request a refund:\n1. Contact support@pearto.com with your account email\n2. Include your reason for cancellation\n3. We'll process eligible refunds within 5-7 business days\n\nCancelling your subscription will not delete your account data.",
                "is_featured": False,
            },
        ]
    },
    {
        "name": "Trading & Investing",
        "slug": "trading-and-investing",
        "icon": "trending-up",
        "description": "Learn about market data, portfolio tracking, and financial tools",
        "order_index": 3,
        "articles": [
            {
                "title": "Understanding market data",
                "slug": "understanding-market-data",
                "content": "Pearto provides comprehensive market data across multiple asset classes.\n\nStocks: Real-time and delayed quotes for major exchanges (NYSE, NASDAQ, LSE, etc.)\nCrypto: Live prices for 100+ cryptocurrencies\nForex: Major, minor, and exotic currency pairs\nCommodities: Gold, silver, oil, and more\n\nData Sources:\n• Free tier: 15-minute delayed data\n• Premium tier: Real-time streaming data\n\nAll prices are sourced from reliable market data providers and updated continuously during market hours.",
                "is_featured": True,
            },
            {
                "title": "Using the portfolio tracker",
                "slug": "using-the-portfolio-tracker",
                "content": "Track your investments in one place with our portfolio tracker.\n\nAdding Holdings:\n1. Go to Portfolio from the sidebar\n2. Click 'Add Holding'\n3. Search for the security (stock, crypto, ETF)\n4. Enter purchase price, quantity, and date\n5. Click Save\n\nFeatures:\n• Real-time P&L tracking\n• Asset allocation pie chart\n• Performance history chart\n• Dividend tracking\n• Currency conversion for international holdings\n\nYou can create multiple portfolios to organize different investment strategies.",
                "is_featured": False,
            },
            {
                "title": "Financial calculators guide",
                "slug": "financial-calculators-guide",
                "content": "Access powerful financial calculators from the Tools section.\n\nAvailable Calculators:\n• Compound Interest Calculator: Project investment growth over time\n• Loan/EMI Calculator: Calculate monthly payments for loans\n• SIP Calculator: Plan systematic investment returns\n• Retirement Calculator: Estimate retirement savings needs\n• Tax Calculator: Estimate your tax liability\n• Currency Converter: Convert between 150+ currencies\n\nEach calculator provides detailed breakdowns and visual charts to help you make informed financial decisions.",
                "is_featured": False,
            },
        ]
    },
    {
        "name": "Security & Privacy",
        "slug": "security-and-privacy",
        "icon": "shield",
        "description": "Keep your account safe and understand our privacy practices",
        "order_index": 4,
        "articles": [
            {
                "title": "Two-factor authentication",
                "slug": "two-factor-authentication",
                "content": "Add an extra layer of security to your account with two-factor authentication (2FA).\n\nTo enable 2FA:\n1. Go to Settings > Security\n2. Click 'Enable Two-Factor Authentication'\n3. Scan the QR code with an authenticator app (Google Authenticator, Authy, etc.)\n4. Enter the verification code to confirm\n5. Save your backup codes in a secure location\n\nOnce enabled, you'll need to enter a code from your authenticator app each time you log in.",
                "is_featured": True,
            },
            {
                "title": "Password best practices",
                "slug": "password-best-practices",
                "content": "Keep your account secure with a strong password.\n\nPassword Requirements:\n• Minimum 8 characters\n• At least one uppercase letter\n• At least one number\n• At least one special character\n\nBest Practices:\n• Use a unique password not used on other sites\n• Consider using a password manager\n• Change your password every 3-6 months\n• Never share your password with anyone\n• Use the 'Forgot Password' feature if compromised\n\nTo change your password: Settings > Security > Change Password",
                "is_featured": False,
            },
        ]
    },
]


def seed_glossary():
    """Seed glossary terms into the database"""
    count = 0
    skipped = 0
    now = datetime.utcnow()

    for item in GLOSSARY_TERMS:
        existing = GlossaryTerm.query.filter(
            GlossaryTerm.term.ilike(item['term'])
        ).first()

        if existing:
            skipped += 1
            continue

        term = GlossaryTerm(
            term=item['term'],
            definition=item['definition'],
            category=item['category'],
            related_terms=item.get('related_terms'),
            country_code='GLOBAL',
            created_at=now,
            updated_at=now,
        )
        db.session.add(term)
        count += 1

    db.session.commit()
    print(f"  Glossary: {count} terms seeded, {skipped} skipped (already exist)")


def seed_help_center():
    """Seed help categories and articles"""
    cat_count = 0
    art_count = 0
    now = datetime.utcnow()

    for cat_data in HELP_CATEGORIES:
        existing_cat = HelpCategory.query.filter_by(slug=cat_data['slug']).first()

        if existing_cat:
            category = existing_cat
            print(f"  Category '{cat_data['name']}' already exists, adding missing articles...")
        else:
            category = HelpCategory(
                name=cat_data['name'],
                slug=cat_data['slug'],
                icon=cat_data.get('icon'),
                description=cat_data.get('description'),
                order_index=cat_data.get('order_index', 0),
                is_active=True,
                country_code='GLOBAL',
            )
            db.session.add(category)
            db.session.flush()  # Get ID
            cat_count += 1

        # Seed articles for this category
        for art_data in cat_data.get('articles', []):
            existing_art = HelpArticle.query.filter_by(slug=art_data['slug']).first()
            if existing_art:
                continue

            article = HelpArticle(
                title=art_data['title'],
                slug=art_data['slug'],
                content=art_data['content'],
                category_id=category.id,
                is_featured=art_data.get('is_featured', False),
                view_count=0,
                helpful_count=0,
                is_active=True,
                country_code='GLOBAL',
            )
            db.session.add(article)
            art_count += 1

    db.session.commit()
    print(f"  Help Center: {cat_count} categories, {art_count} articles seeded")


if __name__ == '__main__':
    with app.app_context():
        print("=" * 50)
        print("Seeding Glossary Terms & Help Center Data")
        print("=" * 50)
        print()

        print("[1/2] Seeding glossary terms...")
        seed_glossary()
        print()

        print("[2/2] Seeding help center data...")
        seed_help_center()
        print()

        print("=" * 50)
        print("Done! All data seeded successfully.")
        print("=" * 50)
