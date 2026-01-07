"""
Demo Data Seed Script for PeartoFinance
Creates realistic market data for development and testing
"""

from datetime import datetime, timedelta
from decimal import Decimal
import random
import uuid
from flask import Flask
from config import config
from models.base import db
from models.market import MarketData, MarketIndices, CommodityData, StockOffer
from models.media import TVChannel, RadioStation, TrendingTopic
from models.article import NewsItem
from models.settings import ToolSettings

def create_app():
    """Create Flask app for seeding"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def seed_market_data():
    """Create stock market data"""
    stocks = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'exchange': 'NASDAQ'},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'exchange': 'NASDAQ'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'exchange': 'NYSE'},
        {'symbol': 'BAC', 'name': 'Bank of America Corp.', 'exchange': 'NYSE'},
        {'symbol': 'GS', 'name': 'Goldman Sachs Group', 'exchange': 'NYSE'},
        {'symbol': 'V', 'name': 'Visa Inc.', 'exchange': 'NYSE'},
        {'symbol': 'MA', 'name': 'Mastercard Inc.', 'exchange': 'NYSE'},
        {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'exchange': 'NYSE'},
        {'symbol': 'PFE', 'name': 'Pfizer Inc.', 'exchange': 'NYSE'},
        {'symbol': 'UNH', 'name': 'UnitedHealth Group', 'exchange': 'NYSE'},
        {'symbol': 'XOM', 'name': 'Exxon Mobil Corp.', 'exchange': 'NYSE'},
        {'symbol': 'CVX', 'name': 'Chevron Corporation', 'exchange': 'NYSE'},
        {'symbol': 'WMT', 'name': 'Walmart Inc.', 'exchange': 'NYSE'},
        {'symbol': 'KO', 'name': 'Coca-Cola Company', 'exchange': 'NYSE'},
        {'symbol': 'PEP', 'name': 'PepsiCo Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'MCD', 'name': "McDonald's Corp.", 'exchange': 'NYSE'},
        {'symbol': 'BA', 'name': 'Boeing Company', 'exchange': 'NYSE'},
        {'symbol': 'CAT', 'name': 'Caterpillar Inc.', 'exchange': 'NYSE'},
        {'symbol': 'DIS', 'name': 'Walt Disney Company', 'exchange': 'NYSE'},
    ]
    
    count = 0
    for stock in stocks:
        existing = MarketData.query.filter_by(symbol=stock['symbol']).first()
        if not existing:
            base_price = random.uniform(50, 500)
            change = random.uniform(-5, 8)
            change_pct = change / base_price * 100
            
            market_data = MarketData(
                symbol=stock['symbol'],
                name=stock['name'],
                price=Decimal(str(round(base_price, 2))),
                change=Decimal(str(round(change, 2))),
                change_percent=Decimal(str(round(change_pct, 2))),
                volume=random.randint(1000000, 50000000),
                market_cap=random.randint(10000000000, 3000000000000),
                currency='USD',
                exchange=stock['exchange'],
                asset_type='stock',
                country_code='US'
            )
            db.session.add(market_data)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} market stocks")

def seed_market_indices():
    """Create market indices"""
    indices = [
        {'symbol': '^GSPC', 'name': 'S&P 500', 'base': 5998.74},
        {'symbol': '^DJI', 'name': 'Dow Jones Industrial Average', 'base': 42732.85},
        {'symbol': '^IXIC', 'name': 'NASDAQ Composite', 'base': 19621.45},
        {'symbol': '^RUT', 'name': 'Russell 2000', 'base': 2285.67},
        {'symbol': '^VIX', 'name': 'CBOE Volatility Index', 'base': 14.25},
        {'symbol': '^NDX', 'name': 'NASDAQ 100', 'base': 21542.78},
    ]
    
    count = 0
    for idx in indices:
        existing = MarketIndices.query.filter_by(symbol=idx['symbol']).first()
        if not existing:
            change = random.uniform(-50, 80)
            change_pct = change / idx['base'] * 100
            
            market_idx = MarketIndices(
                symbol=idx['symbol'],
                name=idx['name'],
                price=Decimal(str(round(idx['base'], 4))),
                change_amount=Decimal(str(round(change, 4))),
                change_percent=Decimal(str(round(change_pct, 4))),
                previous_close=Decimal(str(round(idx['base'] - change, 4))),
                day_high=Decimal(str(round(idx['base'] * 1.01, 4))),
                day_low=Decimal(str(round(idx['base'] * 0.99, 4))),
                year_high=Decimal(str(round(idx['base'] * 1.15, 4))),
                year_low=Decimal(str(round(idx['base'] * 0.85, 4))),
                market_status='closed',
                country_code='US'
            )
            db.session.add(market_idx)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} market indices")

def seed_commodities():
    """Create commodity data"""
    commodities = [
        {'symbol': 'GC', 'name': 'Gold', 'unit': 'oz', 'base': 2340},
        {'symbol': 'SI', 'name': 'Silver', 'unit': 'oz', 'base': 28.50},
        {'symbol': 'CL', 'name': 'Crude Oil WTI', 'unit': 'barrel', 'base': 78},
        {'symbol': 'BZ', 'name': 'Brent Crude', 'unit': 'barrel', 'base': 82},
        {'symbol': 'NG', 'name': 'Natural Gas', 'unit': 'MMBtu', 'base': 2.80},
        {'symbol': 'HG', 'name': 'Copper', 'unit': 'lb', 'base': 4.20},
    ]
    
    count = 0
    for comm in commodities:
        existing = CommodityData.query.filter_by(symbol=comm['symbol']).first()
        if not existing:
            change_pct = random.uniform(-2, 3)
            change = comm['base'] * change_pct / 100
            
            commodity = CommodityData(
                symbol=comm['symbol'],
                name=comm['name'],
                price=Decimal(str(round(comm['base'], 6))),
                change=Decimal(str(round(change, 6))),
                change_percent=Decimal(str(round(change_pct, 4))),
                day_high=Decimal(str(round(comm['base'] * 1.02, 6))),
                day_low=Decimal(str(round(comm['base'] * 0.98, 6))),
                unit=comm['unit'],
                currency='USD'
            )
            db.session.add(commodity)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} commodities")

def seed_stock_offers():
    """Create IPO/FPO data"""
    offers = [
        {'symbol': 'RDDT', 'name': 'Reddit Inc.', 'type': 'ipo', 'status': 'listed', 'price': '31-34'},
        {'symbol': 'XYZCO', 'name': 'XYZ Technologies', 'type': 'ipo', 'status': 'open', 'price': '18-22'},
        {'symbol': 'NEWENERGY', 'name': 'NewEnergy Corp.', 'type': 'ipo', 'status': 'upcoming', 'price': '25-30'},
    ]
    
    count = 0
    for offer in offers:
        existing = StockOffer.query.filter_by(symbol=offer['symbol']).first()
        if not existing:
            stock_offer = StockOffer(
                id=f"offer_{offer['symbol'].lower()}_{random.randint(1000,9999)}",
                symbol=offer['symbol'],
                company_name=offer['name'],
                offer_type=offer['type'],
                price_range=offer['price'],
                open_date=(datetime.now() - timedelta(days=random.randint(0, 30))).date(),
                close_date=(datetime.now() + timedelta(days=random.randint(1, 14))).date(),
                status=offer['status'],
                country_code='US'
            )
            db.session.add(stock_offer)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} stock offers")

def seed_news():
    """Create news items for all categories"""
    news_items = [
        # Business
        {
            'title': 'Fed Signals Potential Rate Cuts in 2024 Amid Cooling Inflation Data',
            'summary': 'Federal Reserve officials hint at possible interest rate reductions as inflation shows signs of cooling. Markets respond positively to dovish signals.',
            'source': 'Bloomberg',
            'category': 'business',
            'image': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600',
            'featured': True,
            'slug': 'fed-signals-rate-cuts-2024'
        },
        {
            'title': 'Major Merger Announced Between Tech Giants Worth $50 Billion',
            'summary': 'Two leading technology companies announce historic merger deal, reshaping the industry landscape.',
            'source': 'Financial Times',
            'category': 'business',
            'image': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600',
            'featured': False,
            'slug': 'tech-giants-merger-50b'
        },
        {
            'title': 'Q4 Earnings Season Kicks Off With Strong Corporate Results',
            'summary': 'Early reports show companies exceeding analyst expectations across multiple sectors.',
            'source': 'CNBC',
            'category': 'business',
            'image': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=600',
            'featured': False,
            'slug': 'q4-earnings-strong-results'
        },
        # Markets
        {
            'title': 'Tech Stocks Rally on Strong Q4 Earnings Reports',
            'summary': 'Major technology companies exceed earnings expectations, driving market gains. NASDAQ reaches new highs.',
            'source': 'CNBC',
            'category': 'markets',
            'image': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600',
            'featured': True,
            'slug': 'tech-stocks-rally-q4'
        },
        {
            'title': 'Bitcoin Surges Past $90,000 on ETF Momentum',
            'summary': 'Cryptocurrency markets rally as institutional adoption continues to grow with new ETF approvals.',
            'source': 'CoinDesk',
            'category': 'markets',
            'image': 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=800&h=600',
            'featured': False,
            'slug': 'bitcoin-surges-90k-etf'
        },
        {
            'title': 'S&P 500 Hits Record High as Investors Eye Rate Cuts',
            'summary': 'Stock market reaches new all-time highs as optimism grows about monetary policy easing.',
            'source': 'Wall Street Journal',
            'category': 'markets',
            'image': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600',
            'featured': False,
            'slug': 'sp500-record-high-rate-cuts'
        },
        # Technology
        {
            'title': 'NVIDIA Announces Next-Gen AI Chips at CES',
            'summary': 'Chip giant reveals breakthrough GPU architecture for AI applications, promising 10x performance gains.',
            'source': 'TechCrunch',
            'category': 'technology',
            'image': 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=600',
            'featured': True,
            'slug': 'nvidia-next-gen-ai-chips-ces'
        },
        {
            'title': 'AI Breakthrough: New Language Models Show Human-Level Reasoning',
            'summary': 'Latest research demonstrates significant advances in artificial intelligence reasoning capabilities.',
            'source': 'MIT Technology Review',
            'category': 'technology',
            'image': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600',
            'featured': False,
            'slug': 'ai-breakthrough-human-reasoning'
        },
        {
            'title': 'Cloud Computing Market Expected to Reach $1 Trillion by 2028',
            'summary': 'Industry analysts project continued strong growth in cloud infrastructure spending.',
            'source': 'Gartner',
            'category': 'technology',
            'image': 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&h=600',
            'featured': False,
            'slug': 'cloud-computing-trillion-2028'
        },
        # World
        {
            'title': 'Global Trade Tensions Ease as New Agreements Signed',
            'summary': 'Major economies reach new trade deals, reducing tariff concerns and boosting market confidence.',
            'source': 'Reuters',
            'category': 'world',
            'image': 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&h=600',
            'featured': True,
            'slug': 'global-trade-tensions-ease'
        },
        {
            'title': 'European Central Bank Maintains Steady Interest Rates',
            'summary': 'ECB holds rates unchanged while signaling cautious approach to monetary policy.',
            'source': 'Financial Times',
            'category': 'world',
            'image': 'https://images.unsplash.com/photo-1569025743873-ea3a9ber5f1c?w=800&h=600',
            'featured': False,
            'slug': 'ecb-steady-interest-rates'
        },
        # Energy
        {
            'title': 'Oil Prices Surge Amid Middle East Tensions',
            'summary': 'Crude oil prices rise sharply as geopolitical concerns affect global supply outlook.',
            'source': 'Reuters',
            'category': 'energy',
            'image': 'https://images.unsplash.com/photo-1513828583688-c52646db42da?w=800&h=600',
            'featured': True,
            'slug': 'oil-prices-surge-middle-east'
        },
        {
            'title': 'Renewable Energy Investment Hits Record $500 Billion',
            'summary': 'Global investment in solar and wind power reaches new highs as clean energy transition accelerates.',
            'source': 'Bloomberg Green',
            'category': 'energy',
            'image': 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&h=600',
            'featured': False,
            'slug': 'renewable-energy-record-500b'
        },
        {
            'title': 'Electric Vehicle Sales Double Year Over Year',
            'summary': 'EV adoption accelerates globally as prices fall and charging infrastructure expands.',
            'source': 'Electrek',
            'category': 'energy',
            'image': 'https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=800&h=600',
            'featured': False,
            'slug': 'ev-sales-double-yoy'
        },
    ]
    
    count = 0
    for item in news_items:
        existing = NewsItem.query.filter_by(slug=item['slug']).first()
        if not existing:
            news = NewsItem(
                title=item['title'],
                summary=item['summary'],
                source=item['source'],
                category=item['category'],
                image=item['image'],
                featured=item.get('featured', False),
                slug=item['slug'],
                curated_status='published',
                source_type='admin',
                published_at=datetime.now() - timedelta(hours=random.randint(1, 72)),
                country_code='US'
            )
            db.session.add(news)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} news items")

def seed_tv_channels():
    """Create TV channel data"""
    channels = [
        {'id': 'bloomberg', 'name': 'Bloomberg TV', 'category': 'Finance', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Bloomberg_Television_logo.svg/512px-Bloomberg_Television_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/dp8PhLsUcFE'},
        {'id': 'cnbc', 'name': 'CNBC', 'category': 'Finance', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/CNBC_logo.svg/512px-CNBC_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/9wTn9EzrLzk'},
        {'id': 'cnn', 'name': 'CNN', 'category': 'News', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/CNN.svg/512px-CNN.svg.png', 'stream_url': 'https://www.youtube.com/embed/5anLPw0Efmo'},
        {'id': 'abcnews', 'name': 'ABC News', 'category': 'News', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/ABC_News_logo.svg/512px-ABC_News_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/vC-ky5VumJI'},
        {'id': 'espn', 'name': 'ESPN', 'category': 'Sports', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/ESPN_wordmark.svg/512px-ESPN_wordmark.svg.png', 'stream_url': 'https://www.youtube.com/embed/DTvS9lvRxZ8'},
        {'id': 'techcrunch', 'name': 'TechCrunch', 'category': 'Technology', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/TechCrunch_logo.svg/512px-TechCrunch_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/pMbvxlNB_zs'},
    ]
    
    count = 0
    for ch in channels:
        existing = TVChannel.query.filter_by(id=ch['id']).first()
        if not existing:
            channel = TVChannel(
                id=ch['id'],
                name=ch['name'],
                category=ch['category'],
                language=ch['language'],
                logo_url=ch['logo_url'],
                stream_url=ch['stream_url'],
                is_active=True,
                is_live=True,
                country_code='US'
            )
            db.session.add(channel)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} TV channels")

def seed_radio_stations():
    """Create radio station data"""
    stations = [
        {'name': 'BBC Nepali', 'stream_url': 'https://stream.live.vc.bbcmedia.co.uk/bbc_nepali_radio', 'country': 'Nepal', 'genre': 'news', 'language': 'Nepali', 'logo_url': 'https://static.files.bbci.co.uk/ws/simorgh-assets/public/nepali/images/icons/icon-128x128.png'},
        {'name': "America's Country", 'stream_url': 'https://ais-sa2.cdnstream1.com/1976_128.mp3', 'country': 'United States', 'genre': 'country', 'language': 'English', 'logo_url': 'https://marinifamily.files.wordpress.com/2015/08/favicon.png'},
        {'name': 'NetTalk America', 'stream_url': 'https://stream-162.zeno.fm/st9bhqvgvceuv', 'country': 'United States', 'genre': 'talk', 'language': 'English', 'logo_url': 'https://img1.wsimg.com/isteam/ip/6e7215c5-5ca4-45c2-b61c-24421c4a5003/74cfc8bf-f67f-4e7d-ad46-0ac09ca2d362.gif.png'},
        {'name': 'Radio Panamericana', 'stream_url': 'https://stream-146.zeno.fm/pnwpbyfambruv', 'country': 'Bolivia', 'genre': 'culture', 'language': 'Spanish', 'logo_url': 'https://graph.facebook.com/NoticiasPanamericana/picture?width=200&height=200'},
        {'name': 'Panamericana Retro Rock', 'stream_url': 'https://us-b4-p-e-pb13-audio.cdn.mdstrm.com/live-audio', 'country': 'Peru', 'genre': 'rock', 'language': 'English', 'logo_url': 'https://static-media.streema.com/media/cache/88/74/8874c7e02e56f56b4d18607b234c95ba.jpg'},
        {'name': 'Radio America 94.7', 'stream_url': 'http://26563.live.streamtheworld.com/AMERICA_SC', 'country': 'Honduras', 'genre': 'news', 'language': 'Spanish', 'logo_url': 'https://d9hhnadinot6y.cloudfront.net/imag/2023/08/cropped-cropped-favico-192x192-1-180x180.png'},
    ]
    
    count = 0
    for st in stations:
        existing = RadioStation.query.filter_by(name=st['name']).first()
        if not existing:
            station = RadioStation(
                name=st['name'],
                stream_url=st['stream_url'],
                country=st['country'],
                genre=st['genre'],
                language=st['language'],
                logo_url=st['logo_url'],
                is_active=True,
                country_code='US'
            )
            db.session.add(station)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} radio stations")

def seed_trending_topics():
    """Create trending topics"""
    topics = [
        {'title': 'NVIDIA earnings beat expectations', 'category': 'Tech', 'rank': 1},
        {'title': 'Bitcoin ETF approval speculation', 'category': 'Crypto', 'rank': 2},
        {'title': 'Fed rate decision impact', 'category': 'Economy', 'rank': 3},
        {'title': 'Tesla Cybertruck deliveries begin', 'category': 'Auto', 'rank': 4},
        {'title': 'Oil prices surge on OPEC cuts', 'category': 'Energy', 'rank': 5},
    ]
    
    count = 0
    try:
        for topic in topics:
            existing = TrendingTopic.query.filter_by(title=topic['title']).first()
            if not existing:
                t = TrendingTopic(
                    title=topic['title'],
                    category=topic['category'],
                    rank=topic['rank'],
                    country_code='US'
                )
                db.session.add(t)
                count += 1
        db.session.commit()
        print(f"✓ Seeded {count} trending topics")
    except Exception as e:
        print(f"⚠ Trending topics table may not exist yet: {e}")
        db.session.rollback()

def seed_tool_settings():
    """Create tool settings data"""
    tools = [
        # Investing Category
        {'slug': 'sip', 'name': 'SIP Calculator', 'category': 'Investing', 'implemented': True},
        {'slug': 'compound', 'name': 'Compound Interest Calculator', 'category': 'Investing', 'implemented': True},
        {'slug': 'goal-planner', 'name': 'Goal Planner', 'category': 'Investing', 'implemented': False},
        {'slug': 'lumpsum', 'name': 'Lumpsum Calculator', 'category': 'Investing', 'implemented': False},
        {'slug': 'step-up-sip', 'name': 'Step-up SIP Calculator', 'category': 'Investing', 'implemented': False},
        {'slug': 'mutual-fund-returns', 'name': 'Mutual Fund Returns', 'category': 'Investing', 'implemented': False},
        {'slug': 'dividend-yield', 'name': 'Dividend Yield Calculator', 'category': 'Investing', 'implemented': False},
        
        # Finance & Loans
        {'slug': 'emi', 'name': 'Loan EMI Calculator', 'category': 'Finance & Loans', 'implemented': True},
        {'slug': 'home-loan', 'name': 'Home Loan EMI', 'category': 'Finance & Loans', 'implemented': False},
        {'slug': 'car-loan', 'name': 'Car Loan EMI', 'category': 'Finance & Loans', 'implemented': False},
        {'slug': 'personal-loan', 'name': 'Personal Loan EMI', 'category': 'Finance & Loans', 'implemented': False},
        {'slug': 'loan-eligibility', 'name': 'Loan Eligibility', 'category': 'Finance & Loans', 'implemented': False},
        {'slug': 'prepayment-calculator', 'name': 'Loan Prepayment', 'category': 'Finance & Loans', 'implemented': False},
        
        # Taxation
        {'slug': 'income-tax', 'name': 'Income Tax Calculator', 'category': 'Taxation', 'implemented': False},
        {'slug': 'hra-exemption', 'name': 'HRA Exemption Calculator', 'category': 'Taxation', 'implemented': False},
        {'slug': 'capital-gains', 'name': 'Capital Gains Tax', 'category': 'Taxation', 'implemented': False},
        {'slug': 'tax-regime-comparison', 'name': 'Old vs New Tax Regime', 'category': 'Taxation', 'implemented': False},
        
        # Retirement
        {'slug': 'retirement', 'name': 'Retirement Calculator', 'category': 'Retirement', 'implemented': False},
        {'slug': 'pension', 'name': 'Pension Calculator', 'category': 'Retirement', 'implemented': False},
        {'slug': 'nps', 'name': 'NPS Calculator', 'category': 'Retirement', 'implemented': False},
        {'slug': 'epf', 'name': 'EPF Calculator', 'category': 'Retirement', 'implemented': False},
        
        # Insurance
        {'slug': 'life-insurance', 'name': 'Life Insurance Needs', 'category': 'Insurance', 'implemented': False},
        {'slug': 'term-insurance', 'name': 'Term Insurance Planner', 'category': 'Insurance', 'implemented': False},
        {'slug': 'health-premium', 'name': 'Health Premium Estimator', 'category': 'Insurance', 'implemented': False},
        {'slug': 'car-insurance', 'name': 'Car Insurance Calculator', 'category': 'Insurance', 'implemented': False},
        
        # Personal Finance
        {'slug': 'budget-planner', 'name': 'Budget Planner', 'category': 'Personal Finance', 'implemented': False},
        {'slug': 'emergency-fund', 'name': 'Emergency Fund Calculator', 'category': 'Personal Finance', 'implemented': False},
        {'slug': 'net-worth', 'name': 'Net Worth Calculator', 'category': 'Personal Finance', 'implemented': False},
        {'slug': 'inflation', 'name': 'Inflation Calculator', 'category': 'Personal Finance', 'implemented': False},
        
        # Debt
        {'slug': 'credit-card-payoff', 'name': 'Credit Card Payoff', 'category': 'Debt', 'implemented': False},
        {'slug': 'debt-snowball', 'name': 'Debt Snowball Calculator', 'category': 'Debt', 'implemented': False},
        {'slug': 'debt-avalanche', 'name': 'Debt Avalanche Calculator', 'category': 'Debt', 'implemented': False},
        
        # Real Estate
        {'slug': 'rent-vs-buy', 'name': 'Rent vs Buy Calculator', 'category': 'Real Estate', 'implemented': False},
        {'slug': 'stamp-duty', 'name': 'Stamp Duty Calculator', 'category': 'Real Estate', 'implemented': False},
        
        # Health & Fitness
        {'slug': 'bmi', 'name': 'BMI Calculator', 'category': 'Health & Fitness', 'implemented': False},
        {'slug': 'calorie-calculator', 'name': 'Calorie Calculator', 'category': 'Health & Fitness', 'implemented': False},
    ]
    
    count = 0
    for idx, tool in enumerate(tools):
        existing = ToolSettings.query.filter_by(tool_slug=tool['slug']).first()
        if not existing:
            tool_setting = ToolSettings(
                tool_slug=tool['slug'],
                tool_name=tool['name'],
                category=tool['category'],
                enabled=True,
                order_index=idx,
                is_implemented=tool['implemented'],
                country_code='GLOBAL'  # Available globally
            )
            db.session.add(tool_setting)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} tool settings")

def run_seed():
    """Run all seed functions"""
    app = create_app()
    with app.app_context():
        print("\n🌱 Starting database seeding...\n")
        
        try:
            seed_market_data()
            seed_market_indices()
            seed_commodities()
            seed_stock_offers()
            seed_news()
            seed_tv_channels()
            seed_radio_stations()
            seed_trending_topics()
            seed_tool_settings()
            
            print("\n✅ Database seeding completed successfully!\n")
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    run_seed()
