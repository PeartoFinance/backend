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
from models.market import MarketData, MarketIndices, CommodityData, StockOffer, CryptoMarketData
from models.media import TVChannel, RadioStation, TrendingTopic, ForexRate
from models.article import NewsItem
from models.settings import ToolSettings, Country
from models.misc import FAQ, FAQItem, GlossaryTerm, Job, TeamMember, Testimonial, MarketingCampaign
from models.education import Course, CourseModule, Instructor, HelpCategory, HelpArticle

# Try to import SportsEvent if it exists
try:
    from models.media import SportsEvent
    HAS_SPORTS_EVENT = True
except ImportError:
    HAS_SPORTS_EVENT = False

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

def seed_forex_rates():
    """Create forex exchange rates"""
    rates = [
        {'base': 'EUR', 'target': 'USD', 'rate': 1.0850},
        {'base': 'GBP', 'target': 'USD', 'rate': 1.2650},
        {'base': 'USD', 'target': 'JPY', 'rate': 155.50},
        {'base': 'USD', 'target': 'CHF', 'rate': 0.8920},
        {'base': 'AUD', 'target': 'USD', 'rate': 0.6350},
        {'base': 'USD', 'target': 'CAD', 'rate': 1.4350},
        {'base': 'NZD', 'target': 'USD', 'rate': 0.5650},
        {'base': 'USD', 'target': 'NPR', 'rate': 136.50},
        {'base': 'USD', 'target': 'INR', 'rate': 86.25},
        {'base': 'EUR', 'target': 'GBP', 'rate': 0.8580},
    ]
    
    count = 0
    for fx in rates:
        existing = ForexRate.query.filter_by(base_currency=fx['base'], target_currency=fx['target']).first()
        if not existing:
            change_pct = random.uniform(-0.5, 0.5)
            change = fx['rate'] * change_pct / 100
            
            forex = ForexRate(
                base_currency=fx['base'],
                target_currency=fx['target'],
                rate=Decimal(str(round(fx['rate'], 6))),
                change=Decimal(str(round(change, 6))),
                change_percent=Decimal(str(round(change_pct, 4))),
            )
            db.session.add(forex)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} forex rates")

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
        {'title': 'Fed Signals Potential Rate Cuts in 2024 Amid Cooling Inflation Data', 'summary': 'Federal Reserve officials hint at possible interest rate reductions as inflation shows signs of cooling.', 'source': 'Bloomberg', 'category': 'business', 'featured': True, 'slug': 'fed-signals-rate-cuts-2024'},
        {'title': 'Major Merger Announced Between Tech Giants Worth $50 Billion', 'summary': 'Two leading technology companies announce historic merger deal.', 'source': 'Financial Times', 'category': 'business', 'featured': False, 'slug': 'tech-giants-merger-50b'},
        {'title': 'Tech Stocks Rally on Strong Q4 Earnings Reports', 'summary': 'Major technology companies exceed earnings expectations.', 'source': 'CNBC', 'category': 'markets', 'featured': True, 'slug': 'tech-stocks-rally-q4'},
        {'title': 'Bitcoin Surges Past $90,000 on ETF Momentum', 'summary': 'Cryptocurrency markets rally as institutional adoption grows.', 'source': 'CoinDesk', 'category': 'crypto', 'featured': True, 'slug': 'bitcoin-surges-90k-etf'},
        {'title': 'NVIDIA Announces Next-Gen AI Chips at CES', 'summary': 'Chip giant reveals breakthrough GPU architecture for AI applications.', 'source': 'TechCrunch', 'category': 'technology', 'featured': True, 'slug': 'nvidia-next-gen-ai-chips-ces'},
        {'title': 'Oil Prices Surge Amid Middle East Tensions', 'summary': 'Crude oil prices rise sharply as geopolitical concerns affect supply.', 'source': 'Reuters', 'category': 'energy', 'featured': True, 'slug': 'oil-prices-surge-middle-east'},
        {'title': 'Renewable Energy Investment Hits Record $500 Billion', 'summary': 'Global investment in solar and wind power reaches new highs.', 'source': 'Bloomberg Green', 'category': 'energy', 'featured': False, 'slug': 'renewable-energy-record-500b'},
        {'title': 'Electric Vehicle Sales Double Year Over Year', 'summary': 'EV adoption accelerates globally as prices fall.', 'source': 'Electrek', 'category': 'auto', 'featured': False, 'slug': 'ev-sales-double-yoy'},
        {'title': 'S&P 500 Hits Record High as Investors Eye Rate Cuts', 'summary': 'Stock market reaches new all-time highs.', 'source': 'Wall Street Journal', 'category': 'markets', 'featured': False, 'slug': 'sp500-record-high-rate-cuts'},
        {'title': 'Global Trade Tensions Ease as New Agreements Signed', 'summary': 'Major economies reach new trade deals.', 'source': 'Reuters', 'category': 'world', 'featured': True, 'slug': 'global-trade-tensions-ease'},
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
        {'id': 'bloomberg', 'name': 'Bloomberg TV', 'category': 'Finance', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Bloomberg_Television_logo.svg/512px-Bloomberg_Television_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/dp8PhLsUcFE', 'country': 'US'},
        {'id': 'cnbc', 'name': 'CNBC', 'category': 'Finance', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/CNBC_logo.svg/512px-CNBC_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/9wTn9EzrLzk', 'country': 'US'},
        {'id': 'cnn', 'name': 'CNN', 'category': 'News', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/CNN.svg/512px-CNN.svg.png', 'stream_url': 'https://www.youtube.com/embed/5anLPw0Efmo', 'country': 'US'},
        {'id': 'bbcworld', 'name': 'BBC World News', 'category': 'News', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/BBC_World_News_logo.svg/512px-BBC_World_News_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/t8yg8sVoXzU', 'country': 'UK'},
        {'id': 'skynews', 'name': 'Sky News', 'category': 'News', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b5/Sky_News.svg/512px-Sky_News.svg.png', 'stream_url': 'https://www.youtube.com/embed/9Auq9mYxFEE', 'country': 'UK'},
        {'id': 'aljazeera', 'name': 'Al Jazeera English', 'category': 'News', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/bc/Al_Jazeera_English_logo.svg/512px-Al_Jazeera_English_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/bNyUyrR0PHo', 'country': 'QA'},
        {'id': 'ndtv', 'name': 'NDTV', 'category': 'News', 'language': 'English', 'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/NDTV_logo.svg/512px-NDTV_logo.svg.png', 'stream_url': 'https://www.youtube.com/embed/WB9GjZSkSB8', 'country': 'IN'},
        {'id': 'ntv_nepal', 'name': 'NTV Nepal', 'category': 'News', 'language': 'Nepali', 'logo_url': 'https://i.ytimg.com/vi/h6jqbz_5h5E/maxresdefault.jpg', 'stream_url': 'https://www.youtube.com/embed/h6jqbz_5h5E', 'country': 'NP'},
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
                country_code=ch['country']
            )
            db.session.add(channel)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} TV channels")

def seed_radio_stations():
    """Create radio station data"""
    stations = [
        {'name': 'BBC Nepali', 'stream_url': 'https://stream.live.vc.bbcmedia.co.uk/bbc_nepali_radio', 'country': 'Nepal', 'genre': 'news', 'language': 'Nepali', 'logo_url': 'https://static.files.bbci.co.uk/ws/simorgh-assets/public/nepali/images/icons/icon-128x128.png', 'country_code': 'NP'},
        {'name': "America's Country", 'stream_url': 'https://ais-sa2.cdnstream1.com/1976_128.mp3', 'country': 'United States', 'genre': 'country', 'language': 'English', 'logo_url': 'https://marinifamily.files.wordpress.com/2015/08/favicon.png', 'country_code': 'US'},
        {'name': 'NetTalk America', 'stream_url': 'https://stream-162.zeno.fm/st9bhqvgvceuv', 'country': 'United States', 'genre': 'talk', 'language': 'English', 'logo_url': 'https://img1.wsimg.com/isteam/ip/6e7215c5-5ca4-45c2-b61c-24421c4a5003/74cfc8bf-f67f-4e7d-ad46-0ac09ca2d362.gif.png', 'country_code': 'US'},
        {'name': 'BBC Nepali 103 MHz', 'stream_url': 'https://stream.live.vc.bbcmedia.co.uk/bbc_nepali_radio', 'country': 'Nepal', 'genre': 'news', 'language': 'Nepali', 'logo_url': 'https://static.files.bbci.co.uk/ws/simorgh-assets/public/nepali/images/icons/icon-128x128.png', 'country_code': 'NP'},
        {'name': 'Radio Panamericana', 'stream_url': 'https://stream-146.zeno.fm/pnwpbyfambruv', 'country': 'Bolivia', 'genre': 'culture', 'language': 'Spanish', 'logo_url': 'https://graph.facebook.com/NoticiasPanamericana/picture?width=200&height=200', 'country_code': 'BO'},
        {'name': 'Radio America 94.7', 'stream_url': 'http://26563.live.streamtheworld.com/AMERICA_SC', 'country': 'Honduras', 'genre': 'news', 'language': 'Spanish', 'logo_url': 'https://d9hhnadinot6y.cloudfront.net/imag/2023/08/cropped-cropped-favico-192x192-1-180x180.png', 'country_code': 'HN'},
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
                country_code=st['country_code']
            )
            db.session.add(station)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} radio stations")

def seed_sports_events():
    """Create sports events data"""
    if not HAS_SPORTS_EVENT:
        print("⚠ SportsEvent model not available, skipping")
        return
    
    events = [
        {'name': 'India vs Australia - 3rd Test', 'description': 'Border-Gavaskar Trophy 2024-25', 'category': 'Cricket', 'status': 'Live', 'venue': 'Melbourne Cricket Ground', 'team_home': 'India', 'team_away': 'Australia', 'series': 'Border-Gavaskar Trophy'},
        {'name': 'Manchester United vs Liverpool', 'description': 'Premier League 2024-25', 'category': 'Football', 'status': 'Upcoming', 'venue': 'Old Trafford', 'team_home': 'Manchester United', 'team_away': 'Liverpool', 'match_type': 'League'},
        {'name': 'Nepal vs UAE - T20', 'description': 'ACC Premier Cup 2024', 'category': 'Cricket', 'status': 'Upcoming', 'venue': 'TU Cricket Ground', 'team_home': 'Nepal', 'team_away': 'UAE', 'series': 'ACC Premier Cup'},
        {'name': 'Real Madrid vs Barcelona', 'description': 'La Liga 2024-25', 'category': 'Football', 'status': 'Upcoming', 'venue': 'Santiago Bernabéu', 'team_home': 'Real Madrid', 'team_away': 'Barcelona', 'match_type': 'League'},
        {'name': 'NBA: Lakers vs Warriors', 'description': 'NBA Regular Season', 'category': 'Basketball', 'status': 'Live', 'venue': 'Crypto.com Arena', 'team_home': 'Lakers', 'team_away': 'Warriors', 'match_type': 'Regular'},
        {'name': 'Australian Open Finals', 'description': 'Grand Slam 2024', 'category': 'Tennis', 'status': 'Upcoming', 'venue': 'Rod Laver Arena', 'match_type': 'Final'},
    ]
    
    count = 0
    for event in events:
        existing = SportsEvent.query.filter_by(name=event['name']).first()
        if not existing:
            sports_event = SportsEvent(
                name=event['name'],
                description=event['description'],
                category=event['category'],
                status=event['status'],
                venue=event.get('venue'),
                team_home=event.get('team_home'),
                team_away=event.get('team_away'),
                series=event.get('series'),
                match_type=event.get('match_type'),
                is_active=True,
                event_date=datetime.now() + timedelta(days=random.randint(-2, 7)),
                country_code='GLOBAL'
            )
            db.session.add(sports_event)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} sports events")

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
        print(f"⚠ Trending topics error: {e}")
        db.session.rollback()

def seed_countries():
    """Create country configuration data"""
    countries = [
        {'code': 'US', 'name': 'United States', 'currency': 'USD', 'symbol': '$', 'flag': '🇺🇸', 'active': True},
        {'code': 'NP', 'name': 'Nepal', 'currency': 'NPR', 'symbol': 'Rs.', 'flag': '🇳🇵', 'active': True},
        {'code': 'IN', 'name': 'India', 'currency': 'INR', 'symbol': '₹', 'flag': '🇮🇳', 'active': True},
        {'code': 'UK', 'name': 'United Kingdom', 'currency': 'GBP', 'symbol': '£', 'flag': '🇬🇧', 'active': True},
        {'code': 'AU', 'name': 'Australia', 'currency': 'AUD', 'symbol': 'A$', 'flag': '🇦🇺', 'active': True},
        {'code': 'CA', 'name': 'Canada', 'currency': 'CAD', 'symbol': 'C$', 'flag': '🇨🇦', 'active': True},
        {'code': 'JP', 'name': 'Japan', 'currency': 'JPY', 'symbol': '¥', 'flag': '🇯🇵', 'active': True},
        {'code': 'DE', 'name': 'Germany', 'currency': 'EUR', 'symbol': '€', 'flag': '🇩🇪', 'active': True},
        {'code': 'SG', 'name': 'Singapore', 'currency': 'SGD', 'symbol': 'S$', 'flag': '🇸🇬', 'active': True},
        {'code': 'AE', 'name': 'UAE', 'currency': 'AED', 'symbol': 'د.إ', 'flag': '🇦🇪', 'active': True},
    ]
    
    count = 0
    for c in countries:
        existing = Country.query.filter_by(code=c['code']).first()
        if not existing:
            country = Country(
                code=c['code'],
                name=c['name'],
                currency_code=c['currency'],
                currency_symbol=c['symbol'],
                flag_emoji=c['flag'],
                is_active=c['active']
            )
            db.session.add(country)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} countries")

def seed_faq():
    """Create FAQ data"""
    faqs = [
        {'question': 'How do I create an account?', 'answer': 'Click on the Sign Up button and fill in your details. You can also sign up using Google or Apple.', 'category': 'Account'},
        {'question': 'How do I reset my password?', 'answer': 'Click on Forgot Password on the login page and enter your email. We will send you a reset link.', 'category': 'Account'},
        {'question': 'What payment methods do you accept?', 'answer': 'We accept all major credit cards, PayPal, and bank transfers. In Nepal, we also accept eSewa and Khalti.', 'category': 'Payments'},
        {'question': 'Is my data secure?', 'answer': 'Yes, we use industry-standard encryption and security practices to protect your personal and financial data.', 'category': 'Security'},
        {'question': 'How often is market data updated?', 'answer': 'Market data is updated in real-time during trading hours. Some data may have a 15-minute delay depending on your subscription.', 'category': 'Data'},
        {'question': 'Can I use PeartoFinance on mobile?', 'answer': 'Yes! Our platform is fully responsive and works on all devices. Mobile apps are coming soon.', 'category': 'General'},
    ]
    
    count = 0
    for item in faqs:
        existing = FAQItem.query.filter_by(question=item['question']).first()
        if not existing:
            faq = FAQItem(
                question=item['question'],
                answer=item['answer'],
                category=item['category'],
                is_published=True,
                order_index=count
            )
            db.session.add(faq)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} FAQ items")

def seed_glossary():
    """Create glossary terms"""
    terms = [
        {'term': 'IPO', 'definition': 'Initial Public Offering - When a private company offers shares to the public for the first time.', 'category': 'Investing'},
        {'term': 'ETF', 'definition': 'Exchange-Traded Fund - A type of fund that trades on stock exchanges like individual stocks.', 'category': 'Investing'},
        {'term': 'P/E Ratio', 'definition': 'Price-to-Earnings Ratio - A valuation metric comparing stock price to earnings per share.', 'category': 'Analysis'},
        {'term': 'Market Cap', 'definition': 'Market Capitalization - Total value of a company calculated by multiplying shares by price.', 'category': 'Analysis'},
        {'term': 'Dividend', 'definition': 'A portion of company profits paid to shareholders, usually quarterly.', 'category': 'Investing'},
        {'term': 'Bull Market', 'definition': 'A market condition where prices are rising or expected to rise.', 'category': 'Markets'},
        {'term': 'Bear Market', 'definition': 'A market condition where prices are falling or expected to fall.', 'category': 'Markets'},
        {'term': 'Volatility', 'definition': 'A statistical measure of the dispersion of returns for a security or market index.', 'category': 'Trading'},
        {'term': 'Liquidity', 'definition': 'The degree to which an asset can be quickly bought or sold without affecting its price.', 'category': 'Trading'},
        {'term': 'SIP', 'definition': 'Systematic Investment Plan - A method of investing fixed amounts regularly in mutual funds.', 'category': 'Investing'},
    ]
    
    count = 0
    for item in terms:
        existing = GlossaryTerm.query.filter_by(term=item['term']).first()
        if not existing:
            term = GlossaryTerm(
                term=item['term'],
                definition=item['definition'],
                category=item['category'],
                is_published=True
            )
            db.session.add(term)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} glossary terms")

def seed_jobs():
    """Create job listings"""
    jobs = [
        {'title': 'Senior Software Engineer', 'department': 'Engineering', 'location': 'Remote', 'type': 'Full-time', 'description': 'We are looking for experienced engineers to build our next-generation financial platform.'},
        {'title': 'Product Manager', 'department': 'Product', 'location': 'San Francisco', 'type': 'Full-time', 'description': 'Lead product development for our investment tools and user experience.'},
        {'title': 'Data Scientist', 'department': 'Data', 'location': 'Remote', 'type': 'Full-time', 'description': 'Build ML models to power market predictions and personalized recommendations.'},
        {'title': 'UX Designer', 'department': 'Design', 'location': 'New York', 'type': 'Full-time', 'description': 'Design beautiful, intuitive interfaces for complex financial data.'},
        {'title': 'Content Writer', 'department': 'Marketing', 'location': 'Remote', 'type': 'Part-time', 'description': 'Create engaging financial education content for our blog and social channels.'},
    ]
    
    count = 0
    for item in jobs:
        existing = Job.query.filter_by(title=item['title']).first()
        if not existing:
            job = Job(
                title=item['title'],
                department=item['department'],
                location=item['location'],
                employment_type=item['type'],
                description=item['description'],
                is_active=True,
                posted_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(job)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} jobs")

def seed_team():
    """Create team member data"""
    team = [
        {'name': 'John Smith', 'role': 'CEO & Co-founder', 'bio': 'Former Goldman Sachs, 15 years in fintech.', 'image': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400'},
        {'name': 'Sarah Johnson', 'role': 'CTO', 'bio': 'Ex-Google engineer, AI/ML specialist.', 'image': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400'},
        {'name': 'Michael Chen', 'role': 'Head of Product', 'bio': 'Product leader from Robinhood and Coinbase.', 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400'},
        {'name': 'Emily Davis', 'role': 'Head of Design', 'bio': 'Award-winning designer, formerly at Apple.', 'image': 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400'},
        {'name': 'David Kim', 'role': 'Head of Data', 'bio': 'Data scientist with experience at hedge funds.', 'image': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400'},
    ]
    
    count = 0
    for member in team:
        existing = TeamMember.query.filter_by(name=member['name']).first()
        if not existing:
            tm = TeamMember(
                name=member['name'],
                role=member['role'],
                bio=member['bio'],
                image_url=member['image'],
                is_active=True,
                order_index=count
            )
            db.session.add(tm)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} team members")

def seed_testimonials():
    """Create testimonial data"""
    testimonials = [
        {'name': 'Alex Thompson', 'role': 'Day Trader', 'content': 'PeartoFinance has transformed how I analyze markets. The AI insights are incredibly accurate.', 'rating': 5},
        {'name': 'Priya Sharma', 'role': 'Investor', 'content': 'The portfolio tracking tools are exceptional. I love the clean interface and real-time updates.', 'rating': 5},
        {'name': 'James Wilson', 'role': 'Financial Advisor', 'content': 'I recommend this platform to all my clients. The educational content is top-notch.', 'rating': 4},
        {'name': 'Maria Garcia', 'role': 'Beginner Investor', 'content': 'As someone new to investing, the learning resources helped me get started with confidence.', 'rating': 5},
    ]
    
    count = 0
    for item in testimonials:
        existing = Testimonial.query.filter_by(name=item['name']).first()
        if not existing:
            testimonial = Testimonial(
                name=item['name'],
                role=item['role'],
                content=item['content'],
                rating=item['rating'],
                is_featured=True,
                is_approved=True
            )
            db.session.add(testimonial)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} testimonials")

def seed_tool_settings():
    """Create tool settings data"""
    tools = [
        {'slug': 'sip', 'name': 'SIP Calculator', 'category': 'Investing', 'implemented': True},
        {'slug': 'compound', 'name': 'Compound Interest Calculator', 'category': 'Investing', 'implemented': True},
        {'slug': 'emi', 'name': 'Loan EMI Calculator', 'category': 'Finance & Loans', 'implemented': True},
        {'slug': 'goal-planner', 'name': 'Goal Planner', 'category': 'Investing', 'implemented': False},
        {'slug': 'lumpsum', 'name': 'Lumpsum Calculator', 'category': 'Investing', 'implemented': False},
        {'slug': 'home-loan', 'name': 'Home Loan EMI', 'category': 'Finance & Loans', 'implemented': False},
        {'slug': 'income-tax', 'name': 'Income Tax Calculator', 'category': 'Taxation', 'implemented': False},
        {'slug': 'retirement', 'name': 'Retirement Calculator', 'category': 'Retirement', 'implemented': False},
        {'slug': 'life-insurance', 'name': 'Life Insurance Needs', 'category': 'Insurance', 'implemented': False},
        {'slug': 'budget-planner', 'name': 'Budget Planner', 'category': 'Personal Finance', 'implemented': False},
        {'slug': 'bmi', 'name': 'BMI Calculator', 'category': 'Health & Fitness', 'implemented': False},
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
                country_code='GLOBAL'
            )
            db.session.add(tool_setting)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} tool settings")

def seed_courses():
    """Create course data"""
    courses = [
        {'title': 'Investing 101: Getting Started', 'description': 'Learn the basics of investing, from stocks to mutual funds.', 'level': 'Beginner', 'duration': 2, 'category': 'Investing'},
        {'title': 'Technical Analysis Masterclass', 'description': 'Master chart patterns, indicators, and trading strategies.', 'level': 'Intermediate', 'duration': 5, 'category': 'Trading'},
        {'title': 'Cryptocurrency Fundamentals', 'description': 'Understand blockchain, Bitcoin, and the crypto ecosystem.', 'level': 'Beginner', 'duration': 3, 'category': 'Crypto'},
        {'title': 'Options Trading Strategies', 'description': 'Advanced options strategies for income and hedging.', 'level': 'Advanced', 'duration': 4, 'category': 'Trading'},
        {'title': 'Personal Finance Basics', 'description': 'Budgeting, saving, and building wealth from scratch.', 'level': 'Beginner', 'duration': 2, 'category': 'Finance'},
    ]
    
    count = 0
    for item in courses:
        existing = Course.query.filter_by(title=item['title']).first()
        if not existing:
            course = Course(
                title=item['title'],
                slug=item['title'].lower().replace(' ', '-').replace(':', ''),
                description=item['description'],
                level=item['level'],
                category=item['category'],
                duration_hours=item['duration'],
                is_published=True,
                is_free=True
            )
            db.session.add(course)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} courses")

def seed_help_articles():
    """Create help center articles"""
    articles = [
        {'title': 'Getting Started with PeartoFinance', 'content': 'Welcome to PeartoFinance! This guide will help you get started...', 'category': 'Getting Started'},
        {'title': 'How to Read Stock Charts', 'content': 'Understanding stock charts is essential for making informed decisions...', 'category': 'Education'},
        {'title': 'Setting Up Price Alerts', 'content': 'Never miss a price movement. Learn how to set up alerts...', 'category': 'Features'},
        {'title': 'Understanding Your Portfolio', 'content': 'Your portfolio dashboard shows all your investments...', 'category': 'Features'},
        {'title': 'Security Best Practices', 'content': 'Keep your account secure with these tips...', 'category': 'Security'},
    ]
    
    # First create help categories
    categories_created = 0
    for article in articles:
        cat = article['category']
        existing = HelpCategory.query.filter_by(name=cat).first()
        if not existing:
            help_cat = HelpCategory(
                name=cat,
                slug=cat.lower().replace(' ', '-'),
                description=f'Help articles about {cat}',
                order_index=categories_created
            )
            db.session.add(help_cat)
            categories_created += 1
    
    db.session.commit()
    
    # Then create articles
    count = 0
    for item in articles:
        existing = HelpArticle.query.filter_by(title=item['title']).first()
        if not existing:
            cat = HelpCategory.query.filter_by(name=item['category']).first()
            article = HelpArticle(
                title=item['title'],
                content=item['content'],
                slug=item['title'].lower().replace(' ', '-').replace("'", ''),
                category_id=cat.id if cat else None,
                is_published=True
            )
            db.session.add(article)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {categories_created} help categories and {count} help articles")

def run_seed():
    """Run all seed functions"""
    app = create_app()
    with app.app_context():
        print("\n🌱 Starting comprehensive database seeding...\n")
        
        try:
            # Market Data
            seed_market_data()
            seed_forex_rates()
            seed_market_indices()
            seed_commodities()
            seed_stock_offers()
            
            # Content
            seed_news()
            seed_trending_topics()
            
            # Media
            seed_tv_channels()
            seed_radio_stations()
            
            # Settings & Config
            seed_countries()
            seed_tool_settings()
            
            # Education
            seed_courses()
            
            print("\n✅ Comprehensive database seeding completed successfully!\n")
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    run_seed()
