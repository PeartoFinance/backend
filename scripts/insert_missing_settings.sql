-- SQL Migration: Add missing settings keys to the database
-- Use these to complete the migration from .env to secure DB settings

INSERT INTO `settings` (`id`, `key`, `value`, `type`, `category`, `is_public`, `country_code`, `is_encrypted`, `updated_at`) VALUES
-- Redis Configuration
('redis_password', 'REDIS_PASSWORD', '', 'string', 'infrastructure', 0, 'GLOBAL', 1, NOW()),
('redis_host', 'REDIS_HOST', '127.0.0.1', 'string', 'infrastructure', 0, 'GLOBAL', 0, NOW()),
('redis_port', 'REDIS_PORT', '38469', 'integer', 'infrastructure', 0, 'GLOBAL', 0, NOW()),
('redis_limiter_db', 'REDIS_LIMITER_DB', '0', 'integer', 'infrastructure', 0, 'GLOBAL', 0, NOW()),
('redis_cache_db', 'REDIS_CACHE_DB', '1', 'integer', 'infrastructure', 0, 'GLOBAL', 0, NOW()),
('redis_socket_path', 'REDIS_SOCKET_PATH', '/home2/ashlya/.redis/redis.sock', 'string', 'infrastructure', 0, 'GLOBAL', 0, NOW()),
('redis_use_socket', 'REDIS_USE_SOCKET', 'false', 'boolean', 'infrastructure', 0, 'GLOBAL', 0, NOW()),

-- Background Job Intervals (Minutes)
('job_stocks_interval', 'JOB_STOCKS_INTERVAL', '15', 'integer', 'background_jobs', 0, 'GLOBAL', 0, NOW()),
('job_crypto_interval', 'JOB_CRYPTO_INTERVAL', '5', 'integer', 'background_jobs', 0, 'GLOBAL', 0, NOW()),
('job_indices_interval', 'JOB_INDICES_INTERVAL', '5', 'integer', 'background_jobs', 0, 'GLOBAL', 0, NOW()),
('job_commodities_interval', 'JOB_COMMODITIES_INTERVAL', '15', 'integer', 'background_jobs', 0, 'GLOBAL', 0, NOW()),
('job_watchlist_interval', 'JOB_WATCHLIST_INTERVAL', '60', 'integer', 'background_jobs', 0, 'GLOBAL', 0, NOW()),
('job_calendar_hour', 'JOB_CALENDAR_HOUR', '6', 'integer', 'background_jobs', 0, 'GLOBAL', 0, NOW()),

-- System Control
('cron_mode', 'CRON_MODE', 'parallel', 'string', 'general', 0, 'GLOBAL', 0, NOW()),
('enable_scheduler', 'ENABLE_SCHEDULER', 'true', 'boolean', 'general', 0, 'GLOBAL', 0, NOW()),
('upload_folder', 'UPLOAD_FOLDER', 'uploads/documents', 'string', 'general', 0, 'GLOBAL', 0, NOW()),

-- Email Identity
('email_from_name', 'EMAIL_FROM_NAME', 'Pearto Finance', 'string', 'email', 0, 'GLOBAL', 0, NOW()),
('email_from_address', 'EMAIL_FROM_ADDRESS', 'noreply@pearto.com', 'string', 'email', 0, 'GLOBAL', 0, NOW()),
('smtp_secure', 'SMTP_SECURE', 'false', 'boolean', 'email', 0, 'GLOBAL', 0, NOW())
ON DUPLICATE KEY UPDATE `updated_at` = NOW();
