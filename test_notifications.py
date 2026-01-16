"""
Notification System Test Script
Run this to debug email, push, and alert notifications
"""
import logging
import sys

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def test_smtp_connection():
    """Test SMTP connection"""
    print("\n" + "="*60)
    print("TEST 1: SMTP Connection")
    print("="*60)
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from notifications.email_service import EmailService
        
        email_service = EmailService()
        
        print(f"SMTP Host: {email_service.config.get('host')}")
        print(f"SMTP Port: {email_service.config.get('port')}")
        print(f"SMTP User: {email_service.config.get('user', '')[:20]}...")
        print(f"Configured: {email_service.is_configured}")
        
        if not email_service.is_configured:
            print("❌ SMTP not configured! Set SMTP_USER and SMTP_PASS in .env")
            return False
        
        result = email_service.verify_connection()
        if result.get('configured'):
            print("✅ SMTP connection successful!")
            return True
        else:
            print(f"❌ SMTP connection failed: {result.get('message')}")
            return False


def test_send_email():
    """Test sending a test email"""
    print("\n" + "="*60)
    print("TEST 2: Send Test Email")
    print("="*60)
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from notifications.email_service import EmailService
        
        email_service = EmailService()
        
        # Get test user email
        test_email = input("Enter test email address (or press Enter to skip): ").strip()
        if not test_email:
            print("⏭️  Skipped email test")
            return None
        
        try:
            result = email_service.send_email(
                to=test_email,
                template_type='signup',
                data={
                    'user_name': 'Test User',
                    'user_email': test_email,
                }
            )
            if result:
                print(f"✅ Test email sent to {test_email}")
                return True
            else:
                print("❌ Email sending returned False")
                return False
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False


def test_user_alerts():
    """Check UserAlert records in database"""
    print("\n" + "="*60)
    print("TEST 3: UserAlert Records")
    print("="*60)
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from models import UserAlert, MarketData
        
        # Check active alerts
        active_alerts = UserAlert.query.filter_by(
            is_active=True,
            is_triggered=False
        ).all()
        
        print(f"Active alerts: {len(active_alerts)}")
        
        for alert in active_alerts[:5]:  # Show first 5
            market_data = MarketData.query.filter_by(symbol=alert.symbol).first()
            current_price = float(market_data.price) if market_data else None
            
            print(f"  - {alert.symbol}: target ${alert.target_value} ({alert.condition})")
            print(f"    Current price: ${current_price if current_price else 'N/A'}")
            print(f"    User ID: {alert.user_id}")
            print()
        
        if len(active_alerts) == 0:
            print("⚠️  No active alerts found - create one in the frontend first!")
            
        return len(active_alerts)


def test_watchlist_check():
    """Run the watchlist alert check job"""
    print("\n" + "="*60)
    print("TEST 4: Run Watchlist Alert Check")
    print("="*60)
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from jobs.notification_jobs import check_watchlist_alerts
        
        print("Running check_watchlist_alerts()...")
        result = check_watchlist_alerts()
        
        print(f"Result: {result}")
        
        if result.get('status') == 'ok':
            print(f"✅ Alerts sent: {result.get('alerts_sent', 0)}")
            return True
        else:
            print(f"❌ Error: {result.get('error')}")
            return False


def test_notification_prefs():
    """Check user notification preferences"""
    print("\n" + "="*60)
    print("TEST 5: User Notification Preferences")
    print("="*60)
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from models import User, UserNotificationPref
        
        # Get users with notification prefs
        users_with_prefs = UserNotificationPref.query.all()
        
        print(f"Users with notification prefs: {len(users_with_prefs)}")
        
        for pref in users_with_prefs[:5]:
            user = User.query.get(pref.user_id)
            print(f"  - User {pref.user_id} ({user.email if user else 'N/A'}):")
            print(f"    Email: {pref.email_enabled}, Push: {pref.push_enabled}, SMS: {pref.sms_enabled}")
        
        if len(users_with_prefs) == 0:
            print("⚠️  No users have notification preferences set!")
            
        return len(users_with_prefs)


def create_test_alert():
    """Create a test alert that should trigger immediately"""
    print("\n" + "="*60)
    print("TEST 6: Create Test Alert (will trigger immediately)")
    print("="*60)
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        from models import db, UserAlert, MarketData, User
        from datetime import datetime
        
        # Get first user
        user = User.query.first()
        if not user:
            print("❌ No users found")
            return False
        
        print(f"Using user: {user.email} (ID: {user.id})")
        
        # Get a stock with current price
        market_data = MarketData.query.filter(MarketData.price.isnot(None)).first()
        if not market_data:
            print("❌ No market data found")
            return False
        
        current_price = float(market_data.price)
        target_price = current_price * 1.001  # 0.1% above - should trigger
        
        print(f"Creating alert for {market_data.symbol}:")
        print(f"  Current: ${current_price:.2f}")
        print(f"  Target: ${target_price:.2f} (below)")
        
        # Create alert
        alert = UserAlert(
            user_id=user.id,
            symbol=market_data.symbol,
            condition='below',  # below target means current >= target triggers
            target_value=target_price,
            is_active=True,
            is_triggered=False,
            created_at=datetime.utcnow()
        )
        db.session.add(alert)
        db.session.commit()
        
        print(f"✅ Created alert ID: {alert.id}")
        print("Now running watchlist check...")
        
        from jobs.notification_jobs import check_watchlist_alerts
        result = check_watchlist_alerts()
        
        print(f"Result: {result}")
        return result.get('alerts_sent', 0) > 0


if __name__ == '__main__':
    print("\n" + "="*60)
    print("PEARTO FINANCE - NOTIFICATION SYSTEM DEBUG")
    print("="*60)
    
    # Run all tests
    tests = [
        ("SMTP Connection", test_smtp_connection),
        ("Send Email", test_send_email),
        ("User Alerts", test_user_alerts),
        ("Watchlist Check", test_watchlist_check),
        ("Notification Prefs", test_notification_prefs),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results[name] = f"Error: {e}"
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, result in results.items():
        status = "✅" if result is True else ("⚠️" if result else "❌")
        print(f"{status} {name}: {result}")
    
    # Offer to create test alert
    create_test = input("\nCreate a test alert that triggers immediately? (y/n): ").strip().lower()
    if create_test == 'y':
        create_test_alert()
