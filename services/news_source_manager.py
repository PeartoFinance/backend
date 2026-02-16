"""
News Source Manager
Handles RSS feeds and external API connections for news import
"""
import hashlib
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from models import db, NewsItem


# Keyword-based auto-category detection
CATEGORY_KEYWORDS = {
    'technology': [
        'ai', 'artificial intelligence', 'machine learning', 'gpu', 'chip', 'semiconductor',
        'software', 'cloud', 'cybersecurity', 'tech', 'apple', 'google', 'microsoft',
        'nvidia', 'meta', 'amazon web services', 'saas', 'data center', 'quantum',
        'robotics', 'automation', '5g', 'startup', 'silicon valley', 'coding'
    ],
    'markets': [
        'stock market', 's&p 500', 'nasdaq', 'dow jones', 'wall street', 'bull market',
        'bear market', 'ipo', 'stock rally', 'stock surge', 'market cap', 'trading',
        'hedge fund', 'etf', 'mutual fund', 'index fund', 'options', 'short selling',
        'rally', 'selloff', 'correction', 'all-time high', 'record high'
    ],
    'crypto': [
        'bitcoin', 'ethereum', 'crypto', 'blockchain', 'defi', 'nft', 'token',
        'altcoin', 'stablecoin', 'web3', 'mining', 'solana', 'dogecoin', 'binance',
        'coinbase', 'cryptocurrency'
    ],
    'business': [
        'merger', 'acquisition', 'earnings', 'revenue', 'profit', 'ceo', 'layoff',
        'restructuring', 'quarterly results', 'annual report', 'corporate', 'company',
        'startup', 'venture capital', 'private equity', 'bankruptcy', 'ipo filing',
        'sec filing', 'board of directors', 'dividend', 'buyback', 'shareholder'
    ],
    'economy': [
        'inflation', 'interest rate', 'federal reserve', 'fed', 'gdp', 'unemployment',
        'recession', 'economic growth', 'monetary policy', 'fiscal policy', 'tariff',
        'trade war', 'stimulus', 'central bank', 'treasury', 'debt ceiling', 'cpi',
        'consumer spending', 'jobs report', 'labor market', 'rate cut', 'rate hike'
    ],
    'energy': [
        'oil', 'crude', 'natural gas', 'opec', 'renewable', 'solar', 'wind',
        'ev', 'electric vehicle', 'battery', 'clean energy', 'hydrogen', 'nuclear',
        'pipeline', 'fossil fuel', 'carbon', 'emission', 'climate', 'esg'
    ],
    'commodities': [
        'gold', 'silver', 'copper', 'platinum', 'palladium', 'iron ore', 'lithium',
        'wheat', 'corn', 'commodity', 'precious metal', 'base metal', 'mining'
    ],
    'world': [
        'geopolitical', 'sanctions', 'trade deal', 'european union', 'china economy',
        'emerging market', 'brics', 'g7', 'g20', 'world bank', 'imf', 'global economy',
        'forex', 'currency', 'euro', 'yen', 'yuan', 'pound'
    ],
    'healthcare': [
        'pharma', 'biotech', 'fda', 'drug', 'vaccine', 'clinical trial', 'healthcare',
        'hospital', 'insurance', 'medicare', 'medicaid', 'health', 'medical device'
    ],
    'realestate': [
        'real estate', 'housing', 'mortgage', 'reit', 'commercial property',
        'rental', 'homebuilder', 'construction', 'property market'
    ],
}


def detect_category(title, summary=''):
    """Auto-detect category from title and summary using keyword matching."""
    text = f"{title} {summary or ''}".lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[category] = score
    if scores:
        return max(scores, key=scores.get)
    return 'general'


class NewsSourceManager:
    """Manages news fetching from RSS feeds and external APIs"""
    
    # Expanded RSS queries mapped to categories
    RSS_QUERIES = [
        # Markets & Stocks
        ('stock market today', 'markets'),
        ('stock market rally selloff', 'markets'),
        ('S&P 500 Nasdaq Dow Jones', 'markets'),
        ('IPO stock listing', 'markets'),
        ('ETF mutual fund investing', 'markets'),
        # Business & Earnings
        ('corporate earnings quarterly results', 'business'),
        ('merger acquisition deal', 'business'),
        ('CEO company layoffs restructuring', 'business'),
        # Economy & Policy
        ('Federal Reserve interest rate', 'economy'),
        ('inflation GDP economy outlook', 'economy'),
        ('unemployment jobs report labor', 'economy'),
        # Technology
        ('AI artificial intelligence tech stocks', 'technology'),
        ('cloud computing software SaaS', 'technology'),
        ('semiconductor chip shortage', 'technology'),
        # Crypto
        ('bitcoin cryptocurrency ethereum', 'crypto'),
        # Energy
        ('oil prices OPEC energy market', 'energy'),
        ('renewable energy solar wind EV', 'energy'),
        # Commodities
        ('gold silver commodity prices', 'commodities'),
        # World / Macro
        ('global trade tariff sanctions', 'world'),
        ('emerging markets BRICS economy', 'world'),
        # Healthcare
        ('biotech pharma FDA drug approval', 'healthcare'),
        # Real Estate
        ('real estate housing market mortgage rates', 'realestate'),
        # Personal Finance
        ('personal finance retirement investing', 'business'),
    ]
    
    MAX_PER_PULL = 100
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; PeartoBot/1.0)'
        }
    
    def pull_all_sources(self):
        """Pull news from all configured sources"""
        print('[NewsSourceManager] Starting news pull from all sources...')
        results = []
        
        # Pull from Google News RSS for each query
        for query_info in self.RSS_QUERIES:
            query, default_category = query_info
            try:
                print(f'[NewsSourceManager] Fetching RSS: "{query}" (category: {default_category})')
                items = self.pull_rss_feed(query, default_category)
                print(f'[NewsSourceManager] RSS "{query}" returned {len(items)} items')
                results.extend(items)
            except Exception as e:
                print(f'[NewsSourceManager] RSS pull failed for "{query}": {str(e)}')
        
        # Process and deduplicate
        print(f'[NewsSourceManager] Total raw items: {len(results)}')
        processed = self.process_and_dedupe(results)
        
        print(f'[NewsSourceManager] New items added: {len(processed)}')
        return processed
    
    def pull_rss_feed(self, query, default_category='general'):
        """Fetch news from Google News RSS"""
        encoded_query = requests.utils.quote(query)
        rss_url = f'https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en'
        
        response = requests.get(rss_url, headers=self.headers, timeout=30)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        items = []
        
        channel = root.find('channel')
        if channel is None:
            return items
        
        for item in channel.findall('item')[:50]:  # Limit to 50 per query
            title = item.find('title')
            link = item.find('link')
            description = item.find('description')
            pub_date = item.find('pubDate')
            
            if title is None or link is None:
                continue
            
            title_text = title.text or ''
            summary_text = description.text if description is not None else title_text
            
            # Auto-detect category from content, fallback to query's default
            detected = detect_category(title_text, summary_text)
            category = detected if detected != 'general' else default_category
            
            items.append({
                'source': 'rss_google_news',
                'source_url': link.text,
                'canonical_url': self.extract_canonical_url(link.text),
                'title': title_text,
                'summary': summary_text,
                'published_at': self.parse_pub_date(pub_date.text if pub_date is not None else None),
                'category': category,
                'query': query
            })
        
        return items
    
    def extract_canonical_url(self, google_news_url):
        """Extract the original article URL from Google News redirect"""
        try:
            # Google News uses redirects, try to extract actual URL
            if 'url=' in google_news_url:
                import urllib.parse
                parsed = urllib.parse.urlparse(google_news_url)
                params = urllib.parse.parse_qs(parsed.query)
                if 'url' in params:
                    return params['url'][0]
            return google_news_url
        except:
            return google_news_url
    
    def parse_pub_date(self, date_str):
        """Parse RSS pubDate to datetime"""
        if not date_str:
            return datetime.utcnow()
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            return datetime.utcnow()
    
    def generate_hash(self, text):
        """Generate SHA256 hash for deduplication"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def generate_simhash(self, text):
        """Generate simple hash for near-duplicate detection"""
        import re
        words = re.sub(r'[^\w\s]', '', text.lower()).split()
        hash_val = 0
        for word in words:
            word_hash = 0
            for char in word:
                word_hash = ((word_hash << 5) - word_hash) + ord(char)
                word_hash = word_hash & 0xFFFFFFFF
            hash_val ^= word_hash
        return hex(hash_val)[2:]
    
    def process_and_dedupe(self, items):
        """Process items and filter duplicates"""
        processed = []
        duplicates = 0
        errors = 0
        
        for item in items:
            try:
                # Generate hash for deduplication
                hash_input = f"{item['canonical_url']}|{item['title']}"
                item_hash = self.generate_hash(hash_input)
                simhash = self.generate_simhash(item['title'] + ' ' + (item['summary'] or ''))
                
                # Check if already exists
                existing = NewsItem.query.filter_by(hash=item_hash).first()
                if existing:
                    duplicates += 1
                    continue
                
                # Check for near-duplicates by simhash
                near_dup = NewsItem.query.filter_by(simhash=simhash).first()
                if near_dup:
                    duplicates += 1
                    continue
                
                # Insert new item
                news_item = NewsItem(
                    source=item['source'],
                    source_url=item['source_url'],
                    canonical_url=item['canonical_url'],
                    title=item['title'],
                    summary=item['summary'],
                    published_at=item['published_at'],
                    hash=item_hash,
                    simhash=simhash,
                    status='queued',
                    curated_status='published',
                    source_type='rss',
                    category=item.get('category', 'general'),
                    created_at=datetime.utcnow()
                )
                
                db.session.add(news_item)
                processed.append(news_item)
                
            except Exception as e:
                errors += 1
                print(f'[NewsSourceManager] Error processing item: {str(e)}')
        
        # Commit all at once
        if processed:
            db.session.commit()
        
        print(f'[NewsSourceManager] Duplicates skipped: {duplicates}, Errors: {errors}')
        return processed


# Global instance
news_source_manager = NewsSourceManager()
