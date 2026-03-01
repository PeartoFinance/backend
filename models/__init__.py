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
    AdminUser,
    NewsPreference,
    NewsNotification,
    FinancialGoalNotification,
    DailySummaryNotification,
)

from .cron_job import CronJob, JobStatus

from .market import (
    MarketData,
    MarketIndices,
    MarketCache,
    MarketSentiment,
    CryptoMarketData,
    CommodityData,
    EconomicEvent,
    StockOffer,
    StockPriceHistory,
    EarningsCalendar,
    AnalystRecommendation,
    EarningsEstimate,
    RecommendationHistory,
    StockSplit,
    Dividend,
    BulkTransaction,
    CompanyFinancials,
    MarketIssue,
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
    UserEnrollment,
    CoursePurchase,
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
    UserInvestmentGoal,
    FinancialGoal,
)

# Chart models
from .chart import (
    ChartDrawing,
    ChartTemplate,
    ChartIndicatorSettings,
    DetectedPattern,
    TradeJournal,
    TradeReview,
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
    MarketHours,
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

from .vendor_data import VendorReview, VendorHistory

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

# Social/Community models
from .social import (
    UserProfile,
    UserFollow,
    Conversation,
    ConversationParticipant,
    Message,
    TradingIdea,
    IdeaLike,
    IdeaComment,
    DiscussionGroup,
    GroupMember,
    GroupPost,
    Badge,
    UserBadge,
    CopyTradingLink,
    CopyTradeExecution,
)

# Subscription models
from .subscription import (
    SubscriptionPlan,
    SubscriptionCoupon,
    UserSubscription,
    PaymentTransaction,
)

# Feature Usage tracking
from .feature_usage import UserFeatureUsage

# API Keys
from .api_key import ApiKey, ApiUsageLog

# All models list for migrations
__all__ = [
    'db',
    'init_db',
    # User
    'User', 'PasswordResetToken', 'UserSession', 'UserDevice', 'UserActivity',
    'UserAlert', 'UserNotificationPref', 'UserDashboardConfig', 'UserDocument',
    'UserSavedTerm', 'UserEconomicEvent', 'LoginEvent', 'Role', 'AdminUser','NewsPreference', 'NewsNotification','FinancialGoalNotification', 'DailySummaryNotification',
    # Cron
    'CronJob',
    # Market
    'MarketData', 'MarketIndices', 'MarketCache', 'MarketSentiment',
    'CryptoMarketData', 'CommodityData', 'EconomicEvent', 'StockOffer',
    'StockPriceHistory', 'EarningsCalendar', 'AnalystRecommendation',
    'EarningsEstimate', 'RecommendationHistory', 'StockSplit',
    'Dividend', 'BulkTransaction', 'CompanyFinancials', 'MarketIssue',
    # Article
    'Article', 'Post', 'PostCategory', 'NewsItem', 'RssFeed', 'RssItem', 'ContentProvider',
    # Education
    'Instructor', 'Course', 'CourseModule', 'Quiz', 'QuizQuestion',
    'QuizAnswer', 'QuizAttempt', 'Webinar', 'WebinarAttendance', 'HelpCategory', 'HelpArticle',
    'UserEnrollment', 'CoursePurchase',
    # Portfolio
    'UserPortfolio', 'PortfolioHolding', 'PortfolioTransaction', 'Watchlist',
    'WatchlistItem', 'UserWatchlist', 'PaperTradingAccount', 'PaperHolding',
    'PaperTransaction', 'WealthState', 'Transaction', 'Deposit', 'Withdrawal', 'Order', 'OrderItem','UserInvestmentGoal','FinancialGoal',
    # Chart
    'ChartDrawing', 'ChartTemplate', 'ChartIndicatorSettings', 'DetectedPattern',
    # Settings
    'Settings', 'Appearance', 'Country', 'APIRegistry', 'ToolSettings',
    'NavigationItem', 'Page', 'EmailTemplate', 'Pricing', 'Service', 'ServiceFeature', 'Product', 'MarketHours',
    # Media
    'TVChannel', 'RadioStation', 'ForexRate', 'TrendingTopic', 'SportsEvent',
    # Admin
    'Vendor', 'VendorAPIKey', 'VendorCustomAPI', 'Seller', 'SellerApplication',
    'SellerCategory', 'Provider', 'AuditEvent', 'AnalyticsEvent', 'NavMetrics',
    'AgentRun', 'AIGenerationRun', 'AIPostDraft', 'Task',
    # Misc
    'FAQ', 'FAQItem', 'GlossaryTerm', 'ContactMessage', 'Subscriber',
    'Testimonial', 'TeamMember', 'Job', 'JobListing', 'Affiliate',
    'MarketingCampaign', 'ChatMessage', 'Booking',
    # Social
    'UserProfile', 'UserFollow', 'Conversation', 'ConversationParticipant', 'Message',
    'TradingIdea', 'IdeaLike', 'IdeaComment', 'DiscussionGroup', 'GroupMember', 'GroupPost',
    'Badge', 'UserBadge', 'CopyTradingLink', 'CopyTradeExecution',
    # Subscription
    'SubscriptionPlan', 'SubscriptionCoupon', 'UserSubscription', 'PaymentTransaction',
    # Feature Usage
    'UserFeatureUsage',
    # API Keys
    'ApiKey', 'ApiUsageLog',
]

