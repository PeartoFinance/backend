"""
Settings & Configuration Models
PeartoFinance Backend
"""
from datetime import datetime
from .base import db


class Settings(db.Model):
    """System settings"""
    __tablename__ = 'settings'
    
    id = db.Column(db.String(255), primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text)
    type = db.Column(db.String(50), default='string')
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    country_code = db.Column(db.String(10))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Appearance(db.Model):
    """Appearance/theme settings"""
    __tablename__ = 'appearance'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    theme = db.Column(db.String(100))
    primaryColor = db.Column(db.String(50))
    secondaryColor = db.Column(db.String(50))
    active = db.Column(db.Integer, default=0)
    country_code = db.Column(db.String(10), default='US')
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)


class Country(db.Model):
    """Supported countries"""
    __tablename__ = 'countries'
    
    code = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    native_name = db.Column(db.String(100))
    currency_code = db.Column(db.String(3))
    currency_symbol = db.Column(db.String(10))
    currency_name = db.Column(db.String(50))
    default_market_index = db.Column(db.String(50))
    timezone = db.Column(db.String(50))
    flag_emoji = db.Column(db.String(10))
    phone_code = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'nativeName': self.native_name,
            'currencyCode': self.currency_code,
            'currencySymbol': self.currency_symbol,
            'flagEmoji': self.flag_emoji,
            'defaultMarketIndex': self.default_market_index
        }


class APIRegistry(db.Model):
    """Registered external APIs"""
    __tablename__ = 'api_registry'
    
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    baseUrl = db.Column(db.String(500))
    docsUrl = db.Column(db.String(500))
    authType = db.Column(db.String(100))
    enabled = db.Column(db.SmallInteger, default=1)
    description = db.Column(db.Text)
    createdAt = db.Column(db.String(40), nullable=False)
    updatedAt = db.Column(db.String(40), nullable=False)


class ToolSettings(db.Model):
    """Tool settings for calculators/tools"""
    __tablename__ = 'tool_settings'
    
    tool_slug = db.Column(db.String(100), primary_key=True)
    tool_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    enabled = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer, default=0)
    is_implemented = db.Column(db.Boolean, default=False)
    country_code = db.Column(db.String(10), default='US')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'tool_slug': self.tool_slug,
            'tool_name': self.tool_name,
            'category': self.category,
            'enabled': self.enabled,
            'order_index': self.order_index,
            'is_implemented': self.is_implemented,
            'country_code': self.country_code
        }


class NavigationItem(db.Model):
    """Navigation menu items"""
    __tablename__ = 'navigation_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    parent_id = db.Column(db.Integer, db.ForeignKey('navigation_items.id'))
    position = db.Column(db.String(50))
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    requires_auth = db.Column(db.Boolean, default=False)
    roles_allowed = db.Column(db.JSON)
    country_code = db.Column(db.String(10))


class Page(db.Model):
    """CMS pages"""
    __tablename__ = 'pages'
    
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True)
    content = db.Column(db.Text)
    meta_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    template = db.Column(db.String(100))
    status = db.Column(db.Enum('draft', 'published'), default='draft')
    is_homepage = db.Column(db.Boolean, default=False)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmailTemplate(db.Model):
    """Email templates"""
    __tablename__ = 'email_templates'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255))
    body_html = db.Column(db.Text)
    body_text = db.Column(db.Text)
    variables = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Pricing(db.Model):
    """Pricing plans"""
    __tablename__ = 'pricing'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_monthly = db.Column(db.Numeric(10, 2))
    price_yearly = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(10), default='USD')
    features = db.Column(db.JSON)
    is_popular = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Service(db.Model):
    """Services offered"""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2))
    is_active = db.Column(db.Boolean, default=True)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ServiceFeature(db.Model):
    """Service features"""
    __tablename__ = 'service_features'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    feature = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)


class Product(db.Model):
    """Products"""
    __tablename__ = 'products'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    discount_price = db.Column(db.Numeric(10, 2))
    category = db.Column(db.String(100))
    image_url = db.Column(db.Text)
    stock_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
