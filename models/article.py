"""
Article/News/Content Models
PeartoFinance Backend
"""
from datetime import datetime
from .base import db


class Article(db.Model):
    """Main articles table"""
    __tablename__ = 'articles'
    
    id = db.Column(db.String(255), primary_key=True)
    slug = db.Column(db.String(255), nullable=False)
    title = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    metaDescription = db.Column(db.Text)
    keywords = db.Column(db.Text)
    json = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'slug': self.slug,
            'title': self.title,
            'category': self.category,
            'metaDescription': self.metaDescription,
            'keywords': self.keywords,
            'createdAt': self.createdAt.isoformat() if self.createdAt else None
        }


class Post(db.Model):
    """Blog posts"""
    __tablename__ = 'posts'
    
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(255))
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('post_categories.id'))
    author_id = db.Column(db.Integer)
    status = db.Column(db.Enum('draft', 'published', 'archived'), default='draft')
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    tags = db.Column(db.JSON)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    country_code = db.Column(db.String(10))
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'featuredImage': self.featured_image,
            'status': self.status,
            'isFeatured': self.is_featured,
            'viewCount': self.view_count,
            'publishedAt': self.published_at.isoformat() if self.published_at else None
        }


class PostCategory(db.Model):
    """Post categories"""
    __tablename__ = 'post_categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100))
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_categories.id'))
    icon = db.Column(db.String(50))
    color = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class NewsItem(db.Model):
    """News items - matches actual pearto.news_items table"""
    __tablename__ = 'news_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source = db.Column(db.String(50))
    source_url = db.Column(db.Text)
    canonical_url = db.Column(db.Text)
    title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    raw = db.Column(db.Text)
    hash = db.Column(db.String(64))
    simhash = db.Column(db.String(32))
    status = db.Column(db.String(20), default='queued')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    image = db.Column(db.Text)
    featured = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50))
    curated_status = db.Column(db.String(20), default='draft')
    updated_at = db.Column(db.DateTime)
    source_type = db.Column(db.String(20), default='rss')
    full_content = db.Column(db.Text)
    author = db.Column(db.String(255))
    slug = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    country_code = db.Column(db.String(2))
    related_symbol = db.Column(db.String(20))  # Stock symbol this news relates to
    
    # Business Profile Link (Added to filter news by specific company)
    related_symbol = db.Column(db.String(20), index=True, nullable=True)

    __table_args__ = (
        db.Index('idx_news_feed', 'status', 'published_at'),
        db.Index('idx_news_category', 'status', 'category', 'published_at'),
        db.Index('idx_news_source', 'source_type', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'description': self.summary,
            'link': self.canonical_url or (f'/news/{self.slug}' if self.slug else '#'),
            'url': self.canonical_url,
            'image': self.image or '/placeholder.svg',
            'source': self.source or ('Pearto' if self.source_type == 'admin' else 'News'),
            'category': self.category or 'general',
            'featured': self.featured,
            'slug': self.slug,
            'author': self.author,
            'publishedAt': self.published_at.isoformat() if self.published_at else None,
            'isInternal': bool(not self.canonical_url and self.slug),
            'country': self.country_code,
            'relatedSymbol': self.related_symbol
        }


class RssFeed(db.Model):
    """RSS feed sources"""
    __tablename__ = 'rss_feeds'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    last_fetched = db.Column(db.DateTime)
    fetch_interval = db.Column(db.Integer, default=300)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RssItem(db.Model):
    """RSS feed items"""
    __tablename__ = 'rss_items'
    
    id = db.Column(db.String(255), primary_key=True)
    feed_id = db.Column(db.String(255), db.ForeignKey('rss_feeds.id'))
    title = db.Column(db.String(500))
    link = db.Column(db.Text)
    description = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)
    guid = db.Column(db.String(500))
    image_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContentProvider(db.Model):
    """Content providers/sources"""
    __tablename__ = 'content_providers'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50))
    base_url = db.Column(db.Text)
    logo_url = db.Column(db.Text)
    is_premium = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
