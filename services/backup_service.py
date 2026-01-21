"""
Backup & Restore Service
PeartoFinance Backend

This service handles the logic for exporting user data to a JSON format
and importing it back into the system. It is designed to be:
1. Versioned: To handle future schema changes.
2. Atomic: Uses database transactions to ensure data integrity.
3. Secure: Removes sensitive fields like passwords and internal IDs.

Developer Note: When adding new user-related models, remember to update 
the export_user_data and import_user_data methods here.
"""

import json
from datetime import datetime, timezone
from models import (
    db, User, UserPortfolio, PortfolioHolding, PortfolioTransaction,
    UserWatchlist, UserAlert, UserNotificationPref, UserDashboardConfig
)

class BackupService:
    VERSION = "1.0"

    @staticmethod
    def export_user_data(user_id):
        """
        Gathers all data for a specific user and returns it as a dictionary.
        This dictionary can then be serialized to JSON for the user to download.
        """
        user = User.query.get(user_id)
        if not user:
            return None

        # 1. Profile Data (Basic info, preferences)
        backup = {
            "metadata": {
                "version": BackupService.VERSION,
                "export_date": datetime.now(timezone.utc).isoformat(),
                "app": "Pearto Finance"
            },
            "profile": {
                "name": user.name,
                "email": user.email,  # Included for reference, but import will use current logged-in email
                "currency": user.currency,
                "country_code": user.country_code,
                "language_pref": user.language_pref,
                "tax_residency": user.tax_residency,
                "phone": user.phone
            },
            "notification_prefs": {},
            "dashboard_config": {},
            "portfolios": [],
            "watchlists": [],
            "alerts": []
        }

        # 2. Notification Preferences
        prefs = UserNotificationPref.query.filter_by(user_id=user_id).first()
        if prefs:
            backup["notification_prefs"] = {
                "email_marketing": prefs.email_marketing,
                "email_alerts": prefs.email_alerts,
                "email_news": prefs.email_news,
                "push_alerts": prefs.push_alerts,
                "push_news": prefs.push_news,
                "sms_alerts": prefs.sms_alerts
            }

        # 3. Dashboard Configuration
        dash = UserDashboardConfig.query.filter_by(user_id=user_id).first()
        if dash:
            backup["dashboard_config"] = {
                "layout": dash.layout,
                "widgets": dash.widgets,
                "theme": dash.theme
            }

        # 4. Portfolios, Holdings, and Transactions
        portfolios = UserPortfolio.query.filter_by(user_id=user_id).all()
        for p in portfolios:
            p_data = {
                "name": p.name,
                "description": p.description,
                "is_default": p.is_default,
                "is_public": p.is_public,
                "currency": p.currency,
                "holdings": [],
                "transactions": []
            }

            # Get Holdings for this portfolio
            holdings = PortfolioHolding.query.filter_by(portfolio_id=p.id).all()
            for h in holdings:
                p_data["holdings"].append({
                    "symbol": h.symbol,
                    "asset_type": h.asset_type,
                    "shares": float(h.shares) if h.shares else 0,
                    "avg_buy_price": float(h.avg_buy_price) if h.avg_buy_price else None,
                    "notes": h.notes
                })

            # Get Transactions for this portfolio
            txs = PortfolioTransaction.query.filter_by(portfolio_id=p.id).all()
            for t in txs:
                p_data["transactions"].append({
                    "symbol": t.symbol,
                    "transaction_type": t.transaction_type,
                    "shares": float(t.shares) if t.shares else 0,
                    "price_per_share": float(t.price_per_share) if t.price_per_share else 0,
                    "fees": float(t.fees) if t.fees else 0,
                    "notes": t.notes,
                    "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None
                })
            
            backup["portfolios"].append(p_data)

        # 5. Watchlists (Both simple and advanced)
        # Simple mapping
        user_watchlists = UserWatchlist.query.filter_by(user_id=user_id).all()
        for w in user_watchlists:
            backup["watchlists"].append({
                "symbol": w.symbol,
                "added_at": w.added_at.isoformat() if w.added_at else None,
                "type": "simple"
            })

        # Advanced multiple watchlists
        from models import Watchlist, WatchlistItem
        advanced_watchlists = Watchlist.query.filter_by(user_id=user_id).all()
        for aw in advanced_watchlists:
            items = WatchlistItem.query.filter_by(watchlist_id=aw.id).all()
            backup["watchlists"].append({
                "name": aw.name,
                "is_default": aw.is_default,
                "created_at": aw.created_at.isoformat() if aw.created_at else None,
                "items": [i.symbol for i in items],
                "type": "advanced"
            })

        # 6. Alerts
        alerts = UserAlert.query.filter_by(user_id=user_id).all()
        for a in alerts:
            backup["alerts"].append({
                "symbol": a.symbol,
                "alert_type": a.alert_type,
                "condition": a.condition,
                "target_value": float(a.target_value) if a.target_value else 0,
                "notify_email": a.notify_email,
                "notify_push": a.notify_push
            })

        return backup

    @staticmethod
    def import_user_data(user_id, data):
        """
        Takes a dictionary (parsed from JSON) and restores it for the given user.
        Uses a database transaction to ensure that if any part fails, nothing is saved.
        """
        try:
            # 1. Validation: Check version
            metadata = data.get("metadata", {})
            if metadata.get("version") != BackupService.VERSION:
                # In the future, we would add migration logic here
                pass

            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            # 2. Restore Profile Preferences
            profile = data.get("profile", {})
            if profile:
                user.currency = profile.get("currency", user.currency)
                user.country_code = profile.get("country_code", user.country_code)
                user.language_pref = profile.get("language_pref", user.language_pref)
                user.tax_residency = profile.get("tax_residency", user.tax_residency)
                user.phone = profile.get("phone", user.phone)

            # 3. Restore Notification Prefs
            n_prefs = data.get("notification_prefs")
            if n_prefs:
                # Delete existing and recreate
                UserNotificationPref.query.filter_by(user_id=user_id).delete()
                new_prefs = UserNotificationPref(
                    user_id=user_id,
                    email_marketing=n_prefs.get("email_marketing", True),
                    email_alerts=n_prefs.get("email_alerts", True),
                    email_news=n_prefs.get("email_news", True),
                    push_alerts=n_prefs.get("push_alerts", True),
                    push_news=n_prefs.get("push_news", True),
                    sms_alerts=n_prefs.get("sms_alerts", False)
                )
                db.session.add(new_prefs)

            # 4. Restore Dashboard Config
            d_config = data.get("dashboard_config")
            if d_config:
                UserDashboardConfig.query.filter_by(user_id=user_id).delete()
                new_dash = UserDashboardConfig(
                    user_id=user_id,
                    layout=d_config.get("layout"),
                    widgets=d_config.get("widgets"),
                    theme=d_config.get("theme", "dark")
                )
                db.session.add(new_dash)

            # 5. Restore Portfolios (The most complex part)
            portfolios = data.get("portfolios", [])
            if portfolios:
                existing_portfolios = UserPortfolio.query.filter_by(user_id=user_id).all()
                for ep in existing_portfolios:
                    PortfolioHolding.query.filter_by(portfolio_id=ep.id).delete()
                    PortfolioTransaction.query.filter_by(portfolio_id=ep.id).delete()
                    db.session.delete(ep)

                for p_data in portfolios:
                    import uuid
                    new_p_id = str(uuid.uuid4())
                    new_p = UserPortfolio(
                        id=new_p_id,
                        user_id=user_id,
                        name=p_data.get("name", "Imported Portfolio"),
                        description=p_data.get("description"),
                        is_default=p_data.get("is_default", False),
                        is_public=p_data.get("is_public", False),
                        currency=p_data.get("currency", "USD")
                    )
                    db.session.add(new_p)
                    # Flush to ensure portfolio exists for holdings/transactions
                    db.session.flush()

                    # Restore Holdings
                    for h_data in p_data.get("holdings", []):
                        new_h = PortfolioHolding(
                            id=str(uuid.uuid4()),
                            portfolio_id=new_p_id,
                            symbol=h_data.get("symbol"),
                            asset_type=h_data.get("asset_type", "stock"),
                            shares=h_data.get("shares"),
                            avg_buy_price=h_data.get("avg_buy_price"),
                            notes=h_data.get("notes")
                        )
                        db.session.add(new_h)

                    # Restore Transactions
                    for t_data in p_data.get("transactions", []):
                        t_date = None
                        if t_data.get("transaction_date"):
                            t_date = datetime.fromisoformat(t_data["transaction_date"]).date()
                        
                        new_t = PortfolioTransaction(
                            id=str(uuid.uuid4()),
                            portfolio_id=new_p_id,
                            symbol=t_data.get("symbol"),
                            transaction_type=t_data.get("transaction_type"),
                            shares=t_data.get("shares"),
                            price_per_share=t_data.get("price_per_share"),
                            fees=t_data.get("fees", 0),
                            notes=t_data.get("notes"),
                            transaction_date=t_date
                        )
                        db.session.add(new_t)

            # 6. Restore Watchlists
            watchlists = data.get("watchlists", [])
            if watchlists:
                from models import Watchlist, WatchlistItem
                UserWatchlist.query.filter_by(user_id=user_id).delete()
                
                # Delete advanced watchlists
                adv_ws = Watchlist.query.filter_by(user_id=user_id).all()
                for aw in adv_ws:
                    WatchlistItem.query.filter_by(watchlist_id=aw.id).delete()
                    db.session.delete(aw)

                for w_data in watchlists:
                    if w_data.get("type") == "simple":
                        new_w = UserWatchlist(
                            user_id=user_id,
                            symbol=w_data.get("symbol"),
                            added_at=datetime.fromisoformat(w_data["added_at"]) if w_data.get("added_at") else datetime.now(timezone.utc)
                        )
                        db.session.add(new_w)
                    elif w_data.get("type") == "advanced":
                        import uuid
                        new_aw_id = str(uuid.uuid4())
                        new_aw = Watchlist(
                            id=new_aw_id,
                            user_id=user_id,
                            name=w_data.get("name", "Imported Watchlist"),
                            is_default=w_data.get("is_default", False),
                            created_at=datetime.fromisoformat(w_data["created_at"]) if w_data.get("created_at") else datetime.now(timezone.utc)
                        )
                        db.session.add(new_aw)
                        # Flush to ensure watchlist exists for items
                        db.session.flush()
                        
                        for symbol in w_data.get("items", []):
                            new_wi = WatchlistItem(
                                watchlist_id=new_aw_id,
                                symbol=symbol
                            )
                            db.session.add(new_wi)

            # 7. Restore Alerts
            alerts = data.get("alerts", [])
            if alerts:
                UserAlert.query.filter_by(user_id=user_id).delete()
                for a_data in alerts:
                    import uuid
                    new_a = UserAlert(
                        id=str(uuid.uuid4()),
                        user_id=user_id,
                        symbol=a_data.get("symbol"),
                        alert_type=a_data.get("alert_type"),
                        condition=a_data.get("condition"),
                        target_value=a_data.get("target_value"),
                        notify_email=a_data.get("notify_email", True),
                        notify_push=a_data.get("notify_push", True)
                    )
                    db.session.add(new_a)

            db.session.commit()
            return True, "Data restored successfully"

        except Exception as e:
            db.session.rollback()
            return False, f"Import failed: {str(e)}"
