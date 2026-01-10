"""
PeartoFinance Database Models
Exports all models from domain-specific files
"""

# Base SQLAlchemy instance
from .base import db, init_db

# User models
from .user import (
    User,
    PasswordResetToken,
    UserSession,
    UserDevice,
    UserActivity,
    UserAlert,
    UserNotificationPref,
    UserDashboardConfig,
    UserDocument,
    UserSavedTerm,
    UserEconomicEvent,
    LoginEvent,
    Role,
)

# Market data models
from .market import (
    MarketData,
    MarketIndices,
    MarketCache,
    MarketSentiment,
    CryptoMarketData,
    CommodityData,
    EconomicEvent,
    StockOffer,
)

# Article/News models
from .article import (
    Article,
    Post,
    PostCategory,
    NewsItem,
    RssFeed,
    RssItem,
    ContentProvider,
)

# Education models
from .education import (
    Instructor,
    Course,
    CourseModule,
    Quiz,
    QuizQuestion,
    QuizAnswer,
    QuizAttempt,
    Webinar,
    WebinarAttendance,
    HelpCategory,
    HelpArticle,
)

# Portfolio/Trading models
from .portfolio import (
    UserPortfolio,
    PortfolioHolding,
    PortfolioTransaction,
    Watchlist,
    WatchlistItem,
    UserWatchlist,
    PaperTradingAccount,
    PaperHolding,
    PaperTransaction,
    WealthState,
    Transaction,
    Deposit,
    Withdrawal,
    Order,
    OrderItem,
)

# Settings/Config models
from .settings import (
    Settings,
    Appearance,
    Country,
    APIRegistry,
    ToolSettings,
    NavigationItem,
    Page,
    EmailTemplate,
    Pricing,
    Service,
    ServiceFeature,
    Product,
)

# Media models
from .media import (
    TVChannel,
    RadioStation,
    ForexRate,
    TrendingTopic,
    SportsEvent,
)

# Admin/Vendor models
from .admin import (
    Vendor,
    VendorAPIKey,
    VendorCustomAPI,
    Seller,
    SellerApplication,
    SellerCategory,
    Provider,
    AuditEvent,
    AnalyticsEvent,
    NavMetrics,
    AgentRun,
    AIGenerationRun,
    AIPostDraft,
    Task,
)

# Misc models
from .misc import (
    FAQ,
    FAQItem,
    GlossaryTerm,
    ContactMessage,
    Subscriber,
    Testimonial,
    TeamMember,
    Job,
    JobListing,
    Affiliate,
    MarketingCampaign,
    ChatMessage,
    Booking,
)

# All models list for migrations
__all__ = [
    'db',
    'init_db',
    # User
    'User', 'PasswordResetToken', 'UserSession', 'UserDevice', 'UserActivity',
    'UserAlert', 'UserNotificationPref', 'UserDashboardConfig', 'UserDocument',
    'UserSavedTerm', 'UserEconomicEvent', 'LoginEvent', 'Role',
    # Market
    'MarketData', 'MarketIndices', 'MarketCache', 'MarketSentiment',
    'CryptoMarketData', 'CommodityData', 'EconomicEvent', 'StockOffer',
    # Article
    'Article', 'Post', 'PostCategory', 'NewsItem', 'RssFeed', 'RssItem', 'ContentProvider',
    # Education
    'Instructor', 'Course', 'CourseModule', 'Quiz', 'QuizQuestion',
    'QuizAnswer', 'QuizAttempt', 'Webinar', 'WebinarAttendance', 'HelpCategory', 'HelpArticle',
    # Portfolio
    'UserPortfolio', 'PortfolioHolding', 'PortfolioTransaction', 'Watchlist',
    'WatchlistItem', 'UserWatchlist', 'PaperTradingAccount', 'PaperHolding',
    'PaperTransaction', 'WealthState', 'Transaction', 'Deposit', 'Withdrawal', 'Order', 'OrderItem',
    # Settings
    'Settings', 'Appearance', 'Country', 'APIRegistry', 'ToolSettings',
    'NavigationItem', 'Page', 'EmailTemplate', 'Pricing', 'Service', 'ServiceFeature', 'Product',
    # Media
    'TVChannel', 'RadioStation', 'ForexRate', 'TrendingTopic',
    # Admin
    'Vendor', 'VendorAPIKey', 'VendorCustomAPI', 'Seller', 'SellerApplication',
    'SellerCategory', 'Provider', 'AuditEvent', 'AnalyticsEvent', 'NavMetrics',
    'AgentRun', 'AIGenerationRun', 'AIPostDraft', 'Task',
    # Misc
    'FAQ', 'FAQItem', 'GlossaryTerm', 'ContactMessage', 'Subscriber',
    'Testimonial', 'TeamMember', 'Job', 'JobListing', 'Affiliate',
    'MarketingCampaign', 'ChatMessage', 'Booking',
]
