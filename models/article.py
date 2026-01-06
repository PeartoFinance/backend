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
    
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    summary = db.Column(db.Text)
    url = db.Column(db.Text)
    image_url = db.Column(db.Text)
    source = db.Column(db.String(100))
    source_url = db.Column(db.Text)
    category = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    sentiment = db.Column(db.String(20))
    relevance_score = db.Column(db.Numeric(5, 2))
    symbols = db.Column(db.JSON)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'url': self.url,
            'imageUrl': self.image_url,
            'source': self.source,
            'category': self.category,
            'publishedAt': self.published_at.isoformat() if self.published_at else None
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
