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
from models.misc import FAQ, FAQItem, GlossaryTerm, Job, JobListing, TeamMember, Testimonial, MarketingCampaign
from models.education import Course, CourseModule, Instructor, HelpCategory, HelpArticle
from models.user import User, Role
import bcrypt
from app import create_app
from models.base import db


# Try to import SportsEvent if it exists
try:
    from models.media import SportsEvent
    HAS_SPORTS_EVENT = True
except ImportError:
    HAS_SPORTS_EVENT = False

# def create_app():
#     """Create Flask app for seeding"""
#     app = Flask(__name__)
#     app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     db.init_app(app)
#     return app

def seed_market_data(countries=('US', 'NP')):
    """Create stock market data for given country codes (upserts by symbol+country).

    By default seeds for US and NP so you can test header-scoped responses.
    """
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

    created = 0
    updated = 0
    now = datetime.utcnow()

    for country in countries:
        for stock in stocks:
            # upsert by symbol + country_code
            existing = MarketData.query.filter(
                MarketData.symbol == stock['symbol'],
                MarketData.country_code == country
            ).first()

            base_price = random.uniform(50, 500)
            change = random.uniform(-5, 8)
            change_pct = change / base_price * 100

            if existing:
                existing.name = stock['name']
                existing.price = Decimal(str(round(base_price, 2)))
                existing.change = Decimal(str(round(change, 2)))
                existing.change_percent = Decimal(str(round(change_pct, 2)))
                existing.volume = random.randint(1000000, 50000000)
                existing.market_cap = random.randint(10000000000, 3000000000000)
                existing.currency = 'USD'
                existing.exchange = stock['exchange']
                existing.asset_type = 'stock'
                existing.last_updated = now
                updated += 1
            else:
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
                    last_updated=now,
                    country_code=country
                )
                db.session.add(market_data)
                created += 1

    db.session.commit()
    print(f"✓ Seeded {created} new and updated {updated} existing market stock rows for countries: {', '.join(countries)}")

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
        {'title': 'Fed Signals Potential Rate Cuts in 2024 Amid Cooling Inflation Data', 'summary': 'Federal Reserve officials hint at possible interest rate reductions as inflation shows signs of cooling.', 'source': 'Bloomberg', 'category': 'business', 'featured': True, 'slug': 'fed-signals-rate-cuts-2024', 'country': 'US'},
        {'title': 'Major Merger Announced Between Tech Giants Worth $50 Billion', 'summary': 'Two leading technology companies announce historic merger deal.', 'source': 'Financial Times', 'category': 'business', 'featured': False, 'slug': 'tech-giants-merger-50b', 'country': 'US'},
        {'title': 'Nepal Rastra Bank Issues New Monetary Policy Guidelines', 'summary': 'The central bank of Nepal announces updates to its monetary policy to stabilize the economy.', 'source': 'The Kathmandu Post', 'category': 'business', 'featured': True, 'slug': 'nrb-monetary-policy-2024', 'country': 'NP'},
        {'title': 'India Becomes Third Largest Economy in Terms of Purchasing Power', 'summary': 'India continues its rapid economic growth, reaching a new milestone in global rankings.', 'source': 'The Economic Times', 'category': 'business', 'featured': True, 'slug': 'india-economy-milestone', 'country': 'IN'},
        {'title': 'Kathmandu Stock Exchange (NEPSE) Hits All-Time High', 'summary': 'Investors cheer as the Nepalese stock market reaches new heights.', 'source': 'MyRepublica', 'category': 'markets', 'featured': True, 'slug': 'nepse-all-time-high', 'country': 'NP'},
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
                country_code=item.get('country', 'US')
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
        # Cricket Events
        {'name': 'India vs Australia - 3rd Test', 'sport_type': 'cricket', 'league': 'Border-Gavaskar Trophy', 'status': 'live', 'venue': 'Melbourne Cricket Ground', 'team_home': 'India', 'team_away': 'Australia', 'score_home': '250/6', 'score_away': '474', 'country_code': 'GLOBAL', 'is_live': True},
        {'name': 'Nepal vs UAE - T20', 'sport_type': 'cricket', 'league': 'ACC Premier Cup', 'status': 'scheduled', 'venue': 'TU Cricket Ground', 'team_home': 'Nepal', 'team_away': 'UAE', 'country_code': 'NP', 'is_live': False},
        {'name': 'England vs New Zealand - ODI', 'sport_type': 'cricket', 'league': 'ODI Series', 'status': 'scheduled', 'venue': 'Lords Cricket Ground', 'team_home': 'England', 'team_away': 'New Zealand', 'country_code': 'GB', 'is_live': False},
        {'name': 'Pakistan vs South Africa - Test', 'sport_type': 'cricket', 'league': 'Test Championship', 'status': 'completed', 'venue': 'National Stadium Karachi', 'team_home': 'Pakistan', 'team_away': 'South Africa', 'score_home': '320', 'score_away': '295', 'country_code': 'GLOBAL', 'is_live': False},
        
        # Football Events
        {'name': 'Manchester United vs Liverpool', 'sport_type': 'football', 'league': 'Premier League', 'status': 'scheduled', 'venue': 'Old Trafford', 'team_home': 'Manchester United', 'team_away': 'Liverpool', 'country_code': 'GB', 'is_live': False},
        {'name': 'Real Madrid vs Barcelona', 'sport_type': 'football', 'league': 'La Liga', 'status': 'scheduled', 'venue': 'Santiago Bernabéu', 'team_home': 'Real Madrid', 'team_away': 'Barcelona', 'country_code': 'ES', 'is_live': False},
        {'name': 'Bayern Munich vs Dortmund', 'sport_type': 'football', 'league': 'Bundesliga', 'status': 'live', 'venue': 'Allianz Arena', 'team_home': 'Bayern Munich', 'team_away': 'Borussia Dortmund', 'score_home': '2', 'score_away': '1', 'country_code': 'DE', 'is_live': True},
        {'name': 'PSG vs Marseille', 'sport_type': 'football', 'league': 'Ligue 1', 'status': 'scheduled', 'venue': 'Parc des Princes', 'team_home': 'Paris Saint-Germain', 'team_away': 'Olympique Marseille', 'country_code': 'FR', 'is_live': False},
        {'name': 'Inter Milan vs AC Milan', 'sport_type': 'football', 'league': 'Serie A', 'status': 'completed', 'venue': 'San Siro', 'team_home': 'Inter Milan', 'team_away': 'AC Milan', 'score_home': '3', 'score_away': '2', 'country_code': 'IT', 'is_live': False},
        
        # Basketball Events
        {'name': 'Lakers vs Warriors', 'sport_type': 'basketball', 'league': 'NBA', 'status': 'live', 'venue': 'Crypto.com Arena', 'team_home': 'Los Angeles Lakers', 'team_away': 'Golden State Warriors', 'score_home': '87', 'score_away': '92', 'country_code': 'US', 'is_live': True},
        {'name': 'Celtics vs Bucks', 'sport_type': 'basketball', 'league': 'NBA', 'status': 'scheduled', 'venue': 'TD Garden', 'team_home': 'Boston Celtics', 'team_away': 'Milwaukee Bucks', 'country_code': 'US', 'is_live': False},
        {'name': 'Bulls vs 76ers', 'sport_type': 'basketball', 'league': 'NBA', 'status': 'completed', 'venue': 'United Center', 'team_home': 'Chicago Bulls', 'team_away': 'Philadelphia 76ers', 'score_home': '105', 'score_away': '112', 'country_code': 'US', 'is_live': False},
        
        # Tennis Events
        {'name': 'Australian Open - Mens Final', 'sport_type': 'tennis', 'league': 'Grand Slam', 'status': 'scheduled', 'venue': 'Rod Laver Arena', 'team_home': 'Djokovic', 'team_away': 'Sinner', 'country_code': 'GLOBAL', 'is_live': False},
        {'name': 'Wimbledon - Womens Semifinal', 'sport_type': 'tennis', 'league': 'Grand Slam', 'status': 'completed', 'venue': 'Centre Court', 'team_home': 'Swiatek', 'team_away': 'Sabalenka', 'score_home': '6-4, 6-3', 'score_away': '-', 'country_code': 'GLOBAL', 'is_live': False},
        
        # Hockey Events
        {'name': 'India vs Pakistan - Asia Cup', 'sport_type': 'hockey', 'league': 'Asia Cup', 'status': 'scheduled', 'venue': 'Dhaka Hockey Stadium', 'team_home': 'India', 'team_away': 'Pakistan', 'country_code': 'GLOBAL', 'is_live': False},
        
        # Rugby Events
        {'name': 'New Zealand vs Australia', 'sport_type': 'rugby', 'league': 'Bledisloe Cup', 'status': 'scheduled', 'venue': 'Eden Park', 'team_home': 'All Blacks', 'team_away': 'Wallabies', 'country_code': 'GLOBAL', 'is_live': False},
    ]
    
    count = 0
    for event in events:
        existing = SportsEvent.query.filter_by(name=event['name']).first()
        if not existing:
            sports_event = SportsEvent(
                name=event['name'],
                sport_type=event.get('sport_type'),
                league=event.get('league'),
                status=event.get('status', 'scheduled'),
                venue=event.get('venue'),
                team_home=event.get('team_home'),
                team_away=event.get('team_away'),
                score_home=event.get('score_home'),
                score_away=event.get('score_away'),
                is_active=True,
                is_live=event.get('is_live', False),
                event_date=datetime.now() + timedelta(days=random.randint(-2, 7)),
                country_code=event.get('country_code', 'GLOBAL')
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
        {'title': 'Senior Software Engineer', 'department': 'Engineering', 'location': 'Remote', 'type': 'full-time', 'description': 'We are looking for experienced engineers to build our next-generation financial platform.', 'country': 'US'},
        {'title': 'Product Manager', 'department': 'Product', 'location': 'San Francisco', 'type': 'full-time', 'description': 'Lead product development for our investment tools and user experience.', 'country': 'US'},
        {'title': 'Financial Analyst', 'department': 'Finance', 'location': 'Kathmandu', 'type': 'full-time', 'description': 'Analyze Nepalese market trends and investment opportunities.', 'country': 'NP'},
        {'title': 'Marketing Specialist', 'department': 'Marketing', 'location': 'Mumbai', 'type': 'full-time', 'description': 'Drive growth and brand awareness in the Indian market.', 'country': 'IN'},
    ]
    
    count = 0
    for item in jobs:
        existing = JobListing.query.filter_by(title=item['title']).first()
        if not existing:
            job = JobListing(
                title=item['title'],
                department=item['department'],
                location=item['location'],
                type=item['type'],
                description=item['description'],
                is_active=True,
                country_code=item['country'],
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(job)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} jobs")

def seed_team():
    """Create team member data"""
    team = [
        {'name': 'John Smith', 'role': 'CEO & Co-founder', 'bio': 'Former Goldman Sachs, 15 years in fintech.', 'image': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=400', 'country': 'US'},
        {'name': 'Sarah Johnson', 'role': 'CTO', 'bio': 'Ex-Google engineer, AI/ML specialist.', 'image': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400', 'country': 'US'},
        {'name': 'Binod Adhikari', 'role': 'Country Manager - Nepal', 'bio': 'Expert in Nepalese financial markets and regulations.', 'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400', 'country': 'NP'},
        {'name': 'Rajesh Kumar', 'role': 'Head of Operations - India', 'bio': 'Experienced operations leader in the Indian fintech space.', 'image': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400', 'country': 'IN'},
    ]
    
    count = 0
    for member in team:
        existing = TeamMember.query.filter_by(name=member['name']).first()
        if not existing:
            tm = TeamMember(
                name=member['name'],
                title=member['role'],
                bio=member['bio'],
                photo_url=member['image'],
                is_active=True,
                sort_order=count,
                country_code=member['country']
            )
            db.session.add(tm)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} team members")

def seed_testimonials():
    """Create testimonial data"""
    testimonials = [
        {'name': 'Alex Thompson', 'role': 'Day Trader', 'content': 'PeartoFinance has transformed how I analyze markets. The AI insights are incredibly accurate.', 'rating': 5, 'country': 'US'},
        {'name': 'Priya Sharma', 'role': 'Investor', 'content': 'The portfolio tracking tools are exceptional. I love the clean interface and real-time updates.', 'rating': 5, 'country': 'IN'},
        {'name': 'Suman Gurung', 'role': 'Local Trader', 'content': 'Finally a platform that understands the Nepalese market context. Very helpful!', 'rating': 5, 'country': 'NP'},
    ]
    
    count = 0
    for item in testimonials:
        existing = Testimonial.query.filter_by(name=item['name']).first()
        if not existing:
            testimonial = Testimonial(
                name=item['name'],
                title=item['role'],
                content=item['content'],
                rating=item['rating'],
                is_featured=True,
                is_active=True,
                country_code=item['country']
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

def seed_instructors():
    """Create instructor data"""
    from models.education import Instructor
    
    instructors = [
        {'name': 'Dr. Sarah Chen', 'title': 'Investment Strategist', 'bio': 'Former Goldman Sachs portfolio manager with 15+ years of experience in equity research and portfolio management.', 'expertise': 'Stocks, ETFs, Portfolio Management'},
        {'name': 'Michael Rodriguez', 'title': 'Trading Expert', 'bio': 'Professional day trader and technical analyst. Has trained over 5,000 students worldwide.', 'expertise': 'Technical Analysis, Day Trading'},
        {'name': 'Emma Thompson', 'title': 'Crypto Educator', 'bio': 'Early Bitcoin adopter and blockchain consultant. Former lead at Coinbase education team.', 'expertise': 'Cryptocurrency, DeFi, Blockchain'},
        {'name': 'James Wilson', 'title': 'Financial Planner', 'bio': 'Certified Financial Planner (CFP) with expertise in retirement planning and wealth management.', 'expertise': 'Personal Finance, Retirement'},
    ]
    
    count = 0
    for item in instructors:
        existing = Instructor.query.filter_by(name=item['name']).first()
        if not existing:
            instructor = Instructor(
                name=item['name'],
                title=item['title'],
                bio=item['bio'],
                expertise=item['expertise'],
                is_active=True,
                rating=4.5 + random.random() * 0.5,
                students_taught=random.randint(500, 5000),
                courses_count=random.randint(2, 8)
            )
            db.session.add(instructor)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} instructors")

def seed_courses():
    """Create course data"""
    from models.education import Instructor
    
    courses = [
        {'title': 'Investing 101: Getting Started', 'description': 'Learn the basics of investing, from stocks to mutual funds. This comprehensive course covers everything you need to know to start your investment journey.', 'level': 'Beginner', 'duration': 4, 'category': 'Investing', 'free': True},
        {'title': 'Technical Analysis Masterclass', 'description': 'Master chart patterns, indicators, and trading strategies used by professional traders.', 'level': 'Intermediate', 'duration': 8, 'category': 'Trading', 'free': False, 'price': 99},
        {'title': 'Cryptocurrency Fundamentals', 'description': 'Understand blockchain technology, Bitcoin, Ethereum, and the entire crypto ecosystem.', 'level': 'Beginner', 'duration': 5, 'category': 'Crypto', 'free': True},
        {'title': 'Options Trading Strategies', 'description': 'Advanced options strategies for income generation and portfolio hedging.', 'level': 'Advanced', 'duration': 10, 'category': 'Trading', 'free': False, 'price': 149},
        {'title': 'Personal Finance Basics', 'description': 'Master budgeting, saving, and building wealth from scratch with practical strategies.', 'level': 'Beginner', 'duration': 3, 'category': 'Finance', 'free': True},
        {'title': 'Stock Market Fundamentals', 'description': 'Deep dive into how the stock market works, valuation methods, and stock picking.', 'level': 'Beginner', 'duration': 6, 'category': 'Investing', 'free': True},
        {'title': 'Forex Trading Essentials', 'description': 'Learn currency trading, pip calculations, and forex market dynamics.', 'level': 'Intermediate', 'duration': 7, 'category': 'Trading', 'free': False, 'price': 79},
        {'title': 'Retirement Planning Guide', 'description': 'Plan for a secure retirement with strategies for 401k, IRA, and pension optimization.', 'level': 'Intermediate', 'duration': 4, 'category': 'Finance', 'free': True},
        {'title': 'DeFi & Web3 Deep Dive', 'description': 'Explore decentralized finance, smart contracts, and the future of web3.', 'level': 'Advanced', 'duration': 8, 'category': 'Crypto', 'free': False, 'price': 129},
        {'title': 'Value Investing Like Warren Buffett', 'description': 'Learn the principles of value investing from the greatest investor of all time.', 'level': 'Intermediate', 'duration': 6, 'category': 'Investing', 'free': False, 'price': 89},
    ]
    
    # Get first instructor for assigning
    first_instructor = Instructor.query.first()
    instructor_id = first_instructor.id if first_instructor else None
    
    count = 0
    for item in courses:
        existing = Course.query.filter_by(title=item['title']).first()
        if not existing:
            course = Course(
                title=item['title'],
                slug=item['title'].lower().replace(' ', '-').replace(':', '').replace("'", ''),
                description=item['description'],
                level=item['level'],
                category=item['category'],
                duration_hours=item['duration'],
                is_published=True,
                is_free=item.get('free', True),
                price=item.get('price', 0),
                instructor_id=instructor_id,
                enrollment_count=random.randint(100, 2000),
                rating=4.0 + random.random() * 1.0,
                rating_count=random.randint(20, 200)
            )
            db.session.add(course)
            count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} courses")


def seed_course_modules():
    """Create course modules for curriculum"""
    from models.education import CourseModule
    
    # Get all courses
    courses = Course.query.all()
    
    module_templates = [
        {'title': 'Introduction & Overview', 'description': 'Get started with the fundamentals and understand the course structure.', 'duration': 30, 'free': True},
        {'title': 'Core Concepts', 'description': 'Deep dive into the essential concepts you need to master.', 'duration': 45, 'free': False},
        {'title': 'Practical Application', 'description': 'Apply what you learned through hands-on exercises.', 'duration': 60, 'free': False},
        {'title': 'Advanced Strategies', 'description': 'Take your skills to the next level with advanced techniques.', 'duration': 55, 'free': False},
        {'title': 'Real-World Case Studies', 'description': 'Learn from real examples and case studies.', 'duration': 40, 'free': False},
        {'title': 'Final Project & Assessment', 'description': 'Complete your learning with a comprehensive project.', 'duration': 50, 'free': False},
    ]
    
    count = 0
    for course in courses:
        # Check if course already has modules
        existing = CourseModule.query.filter_by(course_id=course.id).first()
        if not existing:
            for idx, template in enumerate(module_templates):
                module = CourseModule(
                    course_id=course.id,
                    title=template['title'],
                    description=template['description'],
                    order_index=idx,
                    duration_minutes=template['duration'],
                    is_free=template['free']
                )
                db.session.add(module)
                count += 1
    
    db.session.commit()
    print(f"✓ Seeded {count} course modules")

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
    db.session.commit()
    print(f"✓ Seeded {categories_created} help categories and {count} help articles")

def seed_roles():
    """Create user roles"""
    roles = [
        {'name': 'admin', 'description': 'Administrator with full access', 'is_system': True, 'permissions': {'all': True}},
        {'name': 'user', 'description': 'Standard user', 'is_system': True, 'permissions': {'read': True}},
        {'name': 'editor', 'description': 'Content editor', 'is_system': False, 'permissions': {'read': True, 'write': True}},
    ]
    
    count = 0
    for r in roles:
        existing = Role.query.filter_by(name=r['name']).first()
        if not existing:
            role = Role(
                name=r['name'],
                description=r['description'],
                is_system=r['is_system'],
                permissions=r['permissions']
            )
            db.session.add(role)
            count += 1
            
    db.session.commit()
    print(f"✓ Seeded {count} roles")

def seed_users():
    """Create initial users"""
    # Default password for all seeded users: 'password123'
    # Admin password: 'admin123'
    
    users = [
        {'name': 'Admin User', 'email': 'admin@pearto.com', 'password': 'admin123', 'role': 'admin', 'country': 'US'},
        {'name': 'John Doe', 'email': 'john@example.com', 'password': 'password123', 'role': 'user', 'country': 'US'},
        {'name': 'Jane Smith', 'email': 'jane@example.com', 'password': 'password123', 'role': 'user', 'country': 'UK'},
        {'name': 'Rahul Sharma', 'email': 'rahul@example.com', 'password': 'password123', 'role': 'user', 'country': 'IN'},
    ]
    
    count = 0
    for u in users:
        existing = User.query.filter_by(email=u['email']).first()
        if not existing:
            # Hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(u['password'].encode('utf-8'), salt).decode('utf-8')
            
            user = User(
                name=u['name'],
                email=u['email'],
                password=hashed,
                role=u['role'],
                country_code=u['country'],
                active=1,
                email_verified=True
            )
            db.session.add(user)
            count += 1
            
    db.session.commit()
    print(f"✓ Seeded {count} users")

def run_seed():
    """Run all seed functions"""
    app = create_app()
    with app.app_context():
        print("\n🌱 Starting comprehensive database seeding...\n")
        
        try:
            # Market Data
            try:
                seed_market_data()
            except Exception as e:
                print(f"❌ Market Data failed: {e}")
                
            try:
                seed_forex_rates()
            except Exception as e:
                print(f"❌ Forex Rates failed: {e}")

            try:
                seed_market_indices()
            except Exception as e:
                print(f"❌ Market Indices failed: {e}")

            try:
                seed_commodities()
            except Exception as e:
                print(f"❌ Commodities failed: {e}")

            try:
                seed_stock_offers()
            except Exception as e:
                print(f"❌ Stock Offers failed: {e}")
            
            # Content
            try:
                seed_news()
            except Exception as e:
                print(f"❌ News failed: {e}")

            try:
                seed_trending_topics()
            except Exception as e:
                print(f"❌ Trending Topics failed: {e}")
            
            # Media
            try:
                seed_tv_channels()
            except Exception as e:
                print(f"❌ TV Channels failed: {e}")

            try:
                seed_radio_stations()
            except Exception as e:
                print(f"❌ Radio Stations failed: {e}")

            try:
                seed_sports_events()
            except Exception as e:
                print(f"❌ Sports Events failed: {e}")
            
            # Settings & Config
            try:
                seed_countries()
            except Exception as e:
                print(f"❌ Countries failed: {e}")

            try:
                seed_tool_settings()
            except Exception as e:
                print(f"❌ Tool Settings failed: {e}")
            
            # Education
            try:
                seed_instructors()
            except Exception as e:
                print(f"❌ Instructors failed: {e}")

            try:
                seed_courses()
            except Exception as e:
                print(f"❌ Courses failed: {e}")

            try:
                seed_course_modules()
            except Exception as e:
                print(f"❌ Course Modules failed: {e}")
            
            try:
                seed_help_articles()
            except Exception as e:
                print(f"❌ Help Articles failed: {e}")
            
            # Users & Roles
            try:
                seed_roles()
            except Exception as e:
                print(f"❌ Roles failed: {e}")

            try:
                seed_users()
            except Exception as e:
                print(f"❌ Users failed: {e}")
            
            print("\n✅ Seeding process finished!")
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    run_seed()
