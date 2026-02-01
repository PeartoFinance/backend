"""
Portfolio & Trading Models
PeartoFinance Backend
"""
from datetime import datetime, timezone
from .base import db


class UserPortfolio(db.Model):
    """User investment portfolios"""
    __tablename__ = 'user_portfolios'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), default='My Portfolio')
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    total_value = db.Column(db.Numeric(18, 2), default=0)
    total_gain_loss = db.Column(db.Numeric(18, 2), default=0)
    currency = db.Column(db.String(10), default='USD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holdings = db.relationship('PortfolioHolding', backref='portfolio', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'isDefault': self.is_default,
            'totalValue': float(self.total_value) if self.total_value else 0,
            'totalGainLoss': float(self.total_gain_loss) if self.total_gain_loss else 0
        }

# user investments goals and preferences for portfolio health score
class UserInvestmentGoal(db.Model):
    __tablename__ = 'user_investment_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    age = db.Column(db.Integer)

    # Target allocation (percent)
    target_stocks_percent = db.Column(db.Integer, default=60)
    target_bonds_percent = db.Column(db.Integer, default=20)
    target_cash_percent = db.Column(db.Integer, default=10)
    target_crypto_percent = db.Column(db.Integer, default=5)
    target_commodities_percent = db.Column(db.Integer, default=5)

    risk_tolerance = db.Column(
        db.Enum('conservative', 'moderate', 'aggressive'),
        default='moderate'
    )
     # Benchmarks to compare against
    benchmark_symbol = db.Column(db.String(20), default='^GSPC')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PortfolioHolding(db.Model):
    """Portfolio stock/crypto holdings"""
    __tablename__ = 'portfolio_holdings'
    
    id = db.Column(db.String(255), primary_key=True)
    portfolio_id = db.Column(db.String(255), db.ForeignKey('user_portfolios.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    asset_type = db.Column(db.String(20), default='stock')
    shares = db.Column(db.Numeric(18, 8), nullable=False)
    avg_buy_price = db.Column(db.Numeric(18, 4))
    current_price = db.Column(db.Numeric(18, 4))
    current_value = db.Column(db.Numeric(18, 2))
    gain_loss = db.Column(db.Numeric(18, 2))
    gain_loss_percent = db.Column(db.Numeric(10, 4))
    notes = db.Column(db.Text)
    first_buy_date = db.Column(db.Date)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'assetType': self.asset_type,
            'shares': float(self.shares) if self.shares else 0,
            'avgBuyPrice': float(self.avg_buy_price) if self.avg_buy_price else None,
            'currentPrice': float(self.current_price) if self.current_price else None,
            'currentValue': float(self.current_value) if self.current_value else None,
            'gainLoss': float(self.gain_loss) if self.gain_loss else None,
            'gainLossPercent': float(self.gain_loss_percent) if self.gain_loss_percent else None
        }


class PortfolioTransaction(db.Model):
    """Portfolio buy/sell transactions"""
    __tablename__ = 'portfolio_transactions'
    
    id = db.Column(db.String(255), primary_key=True)
    portfolio_id = db.Column(db.String(255), db.ForeignKey('user_portfolios.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    transaction_type = db.Column(db.Enum('buy', 'sell', 'dividend', 'split'), nullable=False)
    shares = db.Column(db.Numeric(18, 8), nullable=False)
    price_per_share = db.Column(db.Numeric(18, 4), nullable=False)
    total_amount = db.Column(db.Numeric(18, 2))
    fees = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text)
    transaction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Watchlist(db.Model):
    """User watchlists"""
    __tablename__ = 'watchlists'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), default='My Watchlist')
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WatchlistItem(db.Model):
    """Watchlist items"""
    __tablename__ = 'watchlist_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    watchlist_id = db.Column(db.String(255), db.ForeignKey('watchlists.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    asset_type = db.Column(db.String(20), default='stock')
    target_price = db.Column(db.Numeric(18, 4))
    notes = db.Column(db.Text)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserWatchlist(db.Model):
    """Simple user-symbol watchlist mapping"""
    __tablename__ = 'user_watchlist'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


class PaperTradingAccount(db.Model):
    """Paper trading accounts"""
    __tablename__ = 'paper_trading_accounts'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), default='Paper Trading')
    initial_balance = db.Column(db.Numeric(18, 2), default=100000)
    current_balance = db.Column(db.Numeric(18, 2), default=100000)
    total_value = db.Column(db.Numeric(18, 2), default=100000)
    total_gain_loss = db.Column(db.Numeric(18, 2), default=0)
    currency = db.Column(db.String(10), default='USD')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaperHolding(db.Model):
    """Paper trading holdings"""
    __tablename__ = 'paper_holdings'
    
    id = db.Column(db.String(255), primary_key=True)
    account_id = db.Column(db.String(255), db.ForeignKey('paper_trading_accounts.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    shares = db.Column(db.Numeric(18, 8), nullable=False)
    avg_price = db.Column(db.Numeric(18, 4))
    current_price = db.Column(db.Numeric(18, 4))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaperTransaction(db.Model):
    """Paper trading transactions"""
    __tablename__ = 'paper_transactions'
    
    id = db.Column(db.String(255), primary_key=True)
    account_id = db.Column(db.String(255), db.ForeignKey('paper_trading_accounts.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    transaction_type = db.Column(db.Enum('buy', 'sell'), nullable=False)
    shares = db.Column(db.Numeric(18, 8), nullable=False)
    price = db.Column(db.Numeric(18, 4), nullable=False)
    total_amount = db.Column(db.Numeric(18, 2))
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)


class WealthState(db.Model):
    """User wealth tracking over time"""
    __tablename__ = 'wealth_state'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_portfolio_value = db.Column(db.Numeric(18, 2))
    total_cash = db.Column(db.Numeric(18, 2))
    total_investments = db.Column(db.Numeric(18, 2))
    daily_change = db.Column(db.Numeric(18, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Transaction(db.Model):
    """General transactions"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.Enum('pending', 'completed', 'failed', 'cancelled'), default='pending')
    reference = db.Column(db.String(255))
    description = db.Column(db.Text)
    meta_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Deposit(db.Model):
    """User deposits"""
    __tablename__ = 'deposits'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    payment_method = db.Column(db.String(50))
    status = db.Column(db.Enum('pending', 'completed', 'failed'), default='pending')
    transaction_ref = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Withdrawal(db.Model):
    """User withdrawals"""
    __tablename__ = 'withdrawals'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(18, 2), nullable=False)
    currency = db.Column(db.String(10), default='USD')
    payment_method = db.Column(db.String(50))
    account_details = db.Column(db.JSON)
    status = db.Column(db.Enum('pending', 'approved', 'processing', 'completed', 'rejected'), default='pending')
    approved_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)


class Order(db.Model):
    """General orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.Enum('pending', 'confirmed', 'shipped', 'delivered', 'cancelled'), default='pending')
    total_amount = db.Column(db.Numeric(18, 2))
    currency = db.Column(db.String(10), default='USD')
    shipping_address = db.Column(db.JSON)
    billing_address = db.Column(db.JSON)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrderItem(db.Model):
    """Order line items"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(255), db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.String(255))
    product_name = db.Column(db.String(255))
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Numeric(18, 2))
    total_price = db.Column(db.Numeric(18, 2))


# Financial Goals Model

class FinancialGoal(db.Model):
    """
    User financial goals (portfolio target-based)
    """
    __tablename__ = 'financial_goals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )

    # Optional: support multi-portfolio in future
    portfolio_id = db.Column(
        db.String(255),
        db.ForeignKey('user_portfolios.id'),
        nullable=True
    )


    # Goal definition
    name = db.Column(db.String(255), nullable=True)  # Optional goal name
    target_amount = db.Column(db.Numeric(18, 2), nullable=False)
    start_amount = db.Column(db.Numeric(18, 2), nullable=False)
    target_date = db.Column(db.Date, nullable=False)

    # Goal state
    status = db.Column(
        db.Enum('active', 'achieved', 'expired'),
        default='active',
        index=True
    )

    # User preference
    notify_on_reach = db.Column(db.Boolean, default=True)

    # Cron visibility / debugging
    last_checked_at = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )