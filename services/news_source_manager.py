"""
News Source Manager
Handles RSS feeds and external API connections for news import
"""
import hashlib
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from models import db, NewsItem


class NewsSourceManager:
    """Manages news fetching from RSS feeds and external APIs"""
    
    # Default RSS queries for finance news
    RSS_QUERIES = [
        'personal finance',
        'investing stocks',
        'cryptocurrency bitcoin',
        'Federal Reserve economy',
        'stock market news'
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
        for query in self.RSS_QUERIES:
            try:
                print(f'[NewsSourceManager] Fetching RSS: "{query}"')
                items = self.pull_rss_feed(query)
                print(f'[NewsSourceManager] RSS "{query}" returned {len(items)} items')
                results.extend(items)
            except Exception as e:
                print(f'[NewsSourceManager] RSS pull failed for "{query}": {str(e)}')
        
        # Process and deduplicate
        print(f'[NewsSourceManager] Total raw items: {len(results)}')
        processed = self.process_and_dedupe(results)
        
        print(f'[NewsSourceManager] New items added: {len(processed)}')
        return processed
    
    def pull_rss_feed(self, query):
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
            
            items.append({
                'source': 'rss_google_news',
                'source_url': link.text,
                'canonical_url': self.extract_canonical_url(link.text),
                'title': title.text,
                'summary': description.text if description is not None else title.text,
                'published_at': self.parse_pub_date(pub_date.text if pub_date is not None else None),
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
                    curated_status='draft',
                    source_type='rss',
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
