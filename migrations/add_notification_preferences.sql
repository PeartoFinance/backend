-- Migration: Add granular notification preferences
-- Date: 2026-01-25
-- Description: Expands user_notification_prefs table with granular notification controls
-- NOTE: Removed IF NOT EXISTS for broader MySQL compatibility. Python runner handles duplication errors.

-- Email preferences
ALTER TABLE `user_notification_prefs` ADD COLUMN `email_security` BOOLEAN DEFAULT TRUE COMMENT 'Login alerts, password changes';
ALTER TABLE `user_notification_prefs` ADD COLUMN `email_account` BOOLEAN DEFAULT TRUE COMMENT 'Account updates, profile changes';
ALTER TABLE `user_notification_prefs` ADD COLUMN `email_price_alerts` BOOLEAN DEFAULT TRUE COMMENT 'Price target notifications';
ALTER TABLE `user_notification_prefs` ADD COLUMN `email_daily_digest` BOOLEAN DEFAULT TRUE COMMENT 'Daily market summary';
ALTER TABLE `user_notification_prefs` ADD COLUMN `email_earnings` BOOLEAN DEFAULT TRUE COMMENT 'Earnings reminders';
ALTER TABLE `user_notification_prefs` ADD COLUMN `email_newsletter` BOOLEAN DEFAULT TRUE COMMENT 'Weekly newsletter';

-- Push notification preferences
ALTER TABLE `user_notification_prefs` ADD COLUMN `push_security` BOOLEAN DEFAULT TRUE COMMENT 'Push security alerts';
ALTER TABLE `user_notification_prefs` ADD COLUMN `push_price_alerts` BOOLEAN DEFAULT TRUE COMMENT 'Push price alerts';
ALTER TABLE `user_notification_prefs` ADD COLUMN `push_earnings` BOOLEAN DEFAULT TRUE COMMENT 'Push earnings reminders';

-- SMS notification preferences
ALTER TABLE `user_notification_prefs` ADD COLUMN `sms_security` BOOLEAN DEFAULT FALSE COMMENT 'SMS security alerts';
ALTER TABLE `user_notification_prefs` ADD COLUMN `sms_price_alerts` BOOLEAN DEFAULT FALSE COMMENT 'SMS price alerts';

-- Quiet hours
ALTER TABLE `user_notification_prefs` ADD COLUMN `quiet_hours_enabled` BOOLEAN DEFAULT FALSE;
ALTER TABLE `user_notification_prefs` ADD COLUMN `quiet_hours_start` TIME NULL COMMENT 'Quiet hours start time';
ALTER TABLE `user_notification_prefs` ADD COLUMN `quiet_hours_end` TIME NULL COMMENT 'Quiet hours end time';

-- Migrate existing data
UPDATE `user_notification_prefs` SET `email_price_alerts` = `email_alerts` WHERE `email_alerts` IS NOT NULL;
UPDATE `user_notification_prefs` SET `push_price_alerts` = `push_alerts` WHERE `push_alerts` IS NOT NULL;
UPDATE `user_notification_prefs` SET `sms_price_alerts` = `sms_alerts` WHERE `sms_alerts` IS NOT NULL;

-- Index
CREATE INDEX `idx_user_notification_prefs_user` ON `user_notification_prefs` (`user_id`);
