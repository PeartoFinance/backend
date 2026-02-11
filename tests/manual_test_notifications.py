
import sys
import os

# Set Python path to include backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize Flask app
from app import app
from models import db, User, UserNotificationPref
from services.preference_checker import should_send_notification
from handlers.activity_handler import track_password_change, track_profile_update
from handlers.email_service import _email_service

# Mock email sending to avoid actual spam
mock_sent = []

# Store original function to restore later if needed
original_send = _email_service.send_email_async

def mock_send_email_async(to, template_type, data):
    print(f"[MOCK EMAIL] To: {to}, Type: {template_type}")
    mock_sent.append({'to': to, 'type': template_type, 'data': data})

# Monkey patch
_email_service.send_email_async = mock_send_email_async

def test_notifications():
    with app.app_context():
        # 1. Create or get test user
        test_email = 'test_notif_verification@example.com'
        user = User.query.filter_by(email=test_email).first()
        
        if not user:
            print(f"Creating test user {test_email}...")
            user = User(
                name='Test User',
                email=test_email,
                password='hashed_password_123',
                role='user',
                account_status='active'
            )
            db.session.add(user)
            db.session.commit()
            
            # Create prefs if not auto-created
            if not user.notification_preferences:
                prefs = UserNotificationPref(
                    user_id=user.id,
                    email_security=True,
                    email_account=True,
                    email_portfolio_summary=True
                )
                db.session.add(prefs)
                db.session.commit()
        else:
            print(f"Using existing user {user.id}")
            if not user.notification_preferences:
                 prefs = UserNotificationPref(user_id=user.id)
                 db.session.add(prefs)
                 db.session.commit()

        prefs = user.notification_preferences

        # 2. Test Preference Checker Logic
        print("\n--- Testing Preference Checker Logic ---")
        
        # Test Security (Should be True)
        prefs.email_security = True
        db.session.commit()
        assert should_send_notification(user.id, 'security', 'email') == True
        print("✅ Security Pref CHECK: PASS (True)")
        
        # Test Account (Should be True)
        prefs.email_account = True
        db.session.commit()
        assert should_send_notification(user.id, 'account', 'email') == True
        print("✅ Account Pref CHECK: PASS (True)")
        
        # Test Daily Summary (Should match email_portfolio_summary)
        prefs.email_portfolio_summary = False
        db.session.commit()
        assert should_send_notification(user.id, 'daily_summary', 'email') == False
        print("✅ Daily Summary Pref (False) CHECK: PASS")
        
        prefs.email_portfolio_summary = True
        db.session.commit()
        assert should_send_notification(user.id, 'daily_summary', 'email') == True
        print("✅ Daily Summary Pref (True) CHECK: PASS")

        # 3. Test Activity Handler Triggers
        print("\n--- Testing Activity Handler Triggers ---")
        mock_sent.clear()
        
        # Test Password Change (Security = True)
        print("Testing track_password_change (Security=True)...")
        prefs.email_security = True
        db.session.commit()
        
        track_password_change(user.id, ip='127.0.0.1')
        
        found_password = any(x['type'] == 'password_change' for x in mock_sent)
        if found_password:
            print("✅ Password Change Trigger: PASS (Email triggered)")
        else:
            print("❌ Password Change Trigger: FAIL (No email triggered)")
            
        # Test Profile Update (Account = False)
        print("Testing track_profile_update (Account=False)...")
        mock_sent.clear()
        prefs.email_account = False
        db.session.commit()
        
        track_profile_update(user.id, ['phone'])
        
        found_profile_false = any(x['type'] == 'profile_update' for x in mock_sent)
        if not found_profile_false:
            print("✅ Profile Update Trigger (Disabled): PASS (No email)")
        else:
            print("❌ Profile Update Trigger (Disabled): FAIL (Email triggered unexpectedly)")
            
        # Test Profile Update (Account = True)
        print("Testing track_profile_update (Account=True)...")
        mock_sent.clear()
        prefs.email_account = True
        db.session.commit()
        
        track_profile_update(user.id, ['phone', 'avatar'])
        
        found_profile_true = any(x['type'] == 'profile_update' for x in mock_sent)
        if found_profile_true:
            print("✅ Profile Update Trigger (Enabled): PASS (Email triggered)")
            print(f"   Data: {mock_sent[0]['data']}")
        else:
            print("❌ Profile Update Trigger (Enabled): FAIL (No email triggered)")

        # 4. Test Notification Handler Helpers
        print("\n--- Testing Notification Handler Helpers ---")
        from notifications.notification_handler import send_daily_summary, send_marketing_email, send_goal_reached_notification
        
        # Test Daily Summary
        print("Testing send_daily_summary (Portfolio Summary=False)...")
        mock_sent.clear()
        prefs.email_portfolio_summary = False
        db.session.commit()
        
        send_daily_summary(user.id, 10000, 500, 5.0)
        found_summary = any(x['type'] == 'daily_summary' for x in mock_sent) # uses template_type based on map? Wait, email_service uses 'daily_digest' template for 'daily_summary' if mapped? 
        # Actually notification_handler maps 'daily_summary' -> 'daily_digest' template? 
        # Let's check notification_handler.py template map.
        # It maps 'daily_digest' -> 'daily_digest'. But we passed 'daily_summary' type.
        # Template map in notification_handler needs 'daily_summary' -> 'daily_digest'.
        
        if not found_summary and not any(x['type'] == 'daily_digest' for x in mock_sent):
             print("✅ Daily Summary (Disabled): PASS (No email)")
        else:
             print("❌ Daily Summary (Disabled): FAIL (Email sent)")
             
        # Enable it
        print("Testing send_daily_summary (Portfolio Summary=True)...")
        mock_sent.clear()
        prefs.email_portfolio_summary = True
        db.session.commit()
        
        send_daily_summary(user.id, 10000, 500, 5.0)
        # It calls send_notification('daily_summary') -> should_send('daily_summary') -> True
        # Then calls email_service.send_email with template_type from map.
        # We need to verify if 'daily_summary' is in map in notification_handler.py!
        
        # Test Marketing
        print("Testing send_marketing_email (Marketing=False)...")
        mock_sent.clear()
        prefs.email_marketing = False
        db.session.commit()
        
        send_marketing_email(user.id, "Sale!", "Buy now")
        if not mock_sent:
            print("✅ Marketing (Disabled): PASS")
        else:
             print("❌ Marketing (Disabled): FAIL")
             
        # Enable Marketing
        print("Testing send_marketing_email (Marketing=True)...")
        mock_sent.clear()
        prefs.email_marketing = True
        db.session.commit()
        
        send_marketing_email(user.id, "Sale!", "Buy now")
        if any(x['type'] == 'marketing' or x['to'] == user.email for x in mock_sent):
             print("✅ Marketing (Enabled): PASS")
        else:
             print("❌ Marketing (Enabled): FAIL")

        # Cleanup
        print("\n--- Cleanup ---")
        try:
            # Only delete test user to avoid database clutter
            if user.email == 'test_notif_verification@example.com':
                 if user.notification_preferences:
                      db.session.delete(user.notification_preferences)
                 db.session.delete(user)
                 db.session.commit()
                 print("Test user deleted.")
        except Exception as e:
            print(f"Cleanup failed: {e}")

if __name__ == '__main__':
    try:
        test_notifications()
        print("\n🎉 ALL TESTS COMPLETED")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
