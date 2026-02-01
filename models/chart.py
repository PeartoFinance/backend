"""
Chart Models - ChartDrawing, ChartTemplate, etc.
PeartoFinance Backend
"""
from datetime import datetime, timezone
from models.base import db


class ChartDrawing(db.Model):
    """User chart drawings persisted per symbol"""
    __tablename__ = 'chart_drawings'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    drawing_type = db.Column(db.String(50), nullable=False)  # trendline, horizontal, fibonacci, shape, etc
    data = db.Column(db.JSON, nullable=False)  # Drawing coordinates and properties
    is_visible = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'drawingType': self.drawing_type,
            'data': self.data,
            'isVisible': self.is_visible,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class ChartTemplate(db.Model):
    """User chart configuration templates"""
    __tablename__ = 'chart_templates'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    config = db.Column(db.JSON, nullable=False)  # Chart type, period, interval, indicators, colors
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'isDefault': self.is_default,
            'config': self.config,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }


class ChartIndicatorSettings(db.Model):
    """User indicator settings per symbol or global"""
    __tablename__ = 'chart_indicator_settings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20))  # NULL for global defaults
    indicator_type = db.Column(db.String(50), nullable=False)  # rsi, macd, bollinger, sma, ema, etc
    params = db.Column(db.JSON, nullable=False)  # Indicator parameters
    is_active = db.Column(db.Boolean, default=True)
    color = db.Column(db.String(20))  # Custom color
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'indicatorType': self.indicator_type,
            'params': self.params,
            'isActive': self.is_active,
            'color': self.color
        }


class DetectedPattern(db.Model):
    """Cached detected technical patterns"""
    __tablename__ = 'detected_patterns'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    pattern_type = db.Column(db.String(50), nullable=False)  # gartley, butterfly, head_shoulders, triangle, etc
    timeframe = db.Column(db.String(20), nullable=False)  # 1D, 1H, etc
    data = db.Column(db.JSON, nullable=False)  # Pattern coordinates, Fibonacci levels
    confidence = db.Column(db.Numeric(5, 2))  # Pattern confidence score 0-100
    direction = db.Column(db.String(10))  # bullish, bearish
    detected_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime)  # Pattern validity expiration
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'patternType': self.pattern_type,
            'timeframe': self.timeframe,
            'data': self.data,
            'confidence': float(self.confidence) if self.confidence else None,
            'direction': self.direction,
            'detectedAt': self.detected_at.isoformat() if self.detected_at else None
        }
