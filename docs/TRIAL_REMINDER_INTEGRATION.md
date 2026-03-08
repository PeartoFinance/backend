# Subscription Trial Reminder Feature

This feature adds automated email notifications when a user's subscription free trial is about to end (specifically in the next 48 hours).

## Backend Implementation Summary

1.  **Job System**: A new background job `check_trial_expirations` has been added.
2.  **Scheduler**: This job is scheduled to run daily at **10:00 AM**.
3.  **Idempotency**: A new table `trial_notifications` tracks which users have already been notified for which subscription to prevent duplicate emails.
4.  **External Trigger**: A manual trigger route has been added for cPanel cron or external services.

## Integration for Frontend / Ops

### 1. Manual Trigger Route
To manually trigger the trial reminder checks (e.g., from a cPanel cron job), use the following endpoint:

- **URL**: `https://apipearto.ashlya.com/api/cron/trial-reminders`
- **Method**: `GET` or `POST`
- **Auth**: Requires `X-Cron-Token` header or `token` query parameter.

**Example cURL**:
```bash
curl -X POST "https://apipearto.ashlya.com/api/cron/trial-reminders?token=YOUR_CRON_SECRET"
```

### 2. Email Template
The system now uses a new email template: `trial_ending_soon`.
- **Subject**: `Your Pearto Finance Free Trial is Ending Soon! ⏳`
- **Variables**:
  - `user_name`: Name of the user.
  - `plan_name`: Name of the trial plan (e.g., "Pro Plan").
  - `expiry_date`: Format `YYYY-MM-DD`.
  - `billing_url`: Link to the subscription management page.

### 3. Database Changes
A new table `trial_notifications` was added to track notifications.
- Fields: `id`, `user_id`, `subscription_id`, `notification_type`, `sent_at`.
- This ensures that if the cron runs multiple times a day, the user only gets ONE email for their expiring trial.

### 4. Logic
- The job looks for subscriptions where `status == 'trialing'`.
- It calculates if `current_period_end` is between "Now" and "Now + 48 hours".
- Reminders are currently only sent for the `24h_before` notification type.

---
**Note**: Ensure the `CRON_SECRET` in the backend settings matches the token used in external calls.
