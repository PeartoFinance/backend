-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Feb 21, 2026 at 04:56 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pearto`
--

-- --------------------------------------------------------

--
-- Table structure for table `settings`
--

CREATE TABLE `settings` (
  `id` varchar(255) NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` text DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `is_public` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `is_encrypted` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `settings`
--

INSERT INTO `settings` (`id`, `key`, `value`, `type`, `category`, `description`, `is_public`, `country_code`, `updated_at`, `is_encrypted`) VALUES
('5486ed9e-60e8-4e0d-af97-906d57d4cccc', 'ai_widgets_enabled', 'false', 'boolean', 'feature_flags', 'Feature flag: ai_widgets_enabled', 1, 'GLOBAL', '2026-02-04 13:03:00', 0),
('89fc173d-a479-479a-b689-069d36ee691c', 'ai_analysis_enabled', 'false', 'boolean', 'feature_flags', 'Feature flag: ai_analysis_enabled', 1, 'GLOBAL', '2026-02-04 13:02:59', 0),
('active_payment_gateway', 'ACTIVE_PAYMENT_GATEWAY', 'paypal', 'string', 'payment', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('api_sports_key', 'API_SPORTS_KEY', 'gAAAAABpmc3ji8xrWGWN4Tzch0_TJJCzKFDnIDsl_6ZMs-5d6sSXjKHS-AphVhMr2SAu4ATv7825TMVU34YHGS_PhkGApS_nXzJrQ0dUY5lZtDgqTYHSiAV2ec23OWNUm3MjnCdgWw-NY6IAkFWl9cj1WV77Ldj30TYmbjSwvBW6jmkxB50nzj4oCZBj82LzGk7I6PVXaAKas_LxcRdfmoQHI7uhloPFgWMr0Lf9iTNzBAPeHpLB0U1iyW58wTKqAjz5LKIbeKRs', 'string', 'api_keys', NULL, 0, 'GLOBAL', '2026-02-21 15:23:15', 1),
('app_url', 'APP_URL', 'https://pearto.com', 'string', 'general', NULL, 1, 'GLOBAL', '2026-02-21 21:02:23', 0),
('cron_mode', 'CRON_MODE', 'parallel', 'string', 'general', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('cron_secret', 'CRON_SECRET', '123456789', 'string', 'general', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('email_from_address', 'EMAIL_FROM_ADDRESS', 'noreply@pearto.com', 'string', 'email', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('email_from_name', 'EMAIL_FROM_NAME', 'Pearto Finance', 'string', 'email', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('enable_scheduler', 'ENABLE_SCHEDULER', 'true', 'boolean', 'general', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('firebase_project_id', 'FIREBASE_PROJECT_ID', 'pearto-app', 'string', 'general', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('job_calendar_hour', 'JOB_CALENDAR_HOUR', '6', 'integer', 'background_jobs', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('job_commodities_interval', 'JOB_COMMODITIES_INTERVAL', '15', 'integer', 'background_jobs', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('job_crypto_interval', 'JOB_CRYPTO_INTERVAL', '5', 'integer', 'background_jobs', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('job_indices_interval', 'JOB_INDICES_INTERVAL', '5', 'integer', 'background_jobs', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('job_stocks_interval', 'JOB_STOCKS_INTERVAL', '15', 'integer', 'background_jobs', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('job_watchlist_interval', 'JOB_WATCHLIST_INTERVAL', '60', 'integer', 'background_jobs', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('jwt_secret', 'JWT_SECRET', 'your-super-secret-jwt-key-change-in-production', 'string', 'general', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('onesignal_api_key', 'ONESIGNAL_API_KEY', '6butqfh3re4cffnas2yylq5e5', 'string', 'general', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('onesignal_app_id', 'ONESIGNAL_APP_ID', 'a0176d46-b5c9-425a-83a9-8af1a0a67ad8', 'string', 'general', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('paypal_client_id', 'PAYPAL_CLIENT_ID', 'AR4Qn-XzeD_YCS_8fNbIhV9P6xcohctG9vEaNFrrjoYotjg9oLQmfQJkhZmmLZsk5bIpu7mkkVPdlDUu', 'string', 'payment', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('paypal_mode', 'PAYPAL_MODE', 'sandbox', 'string', 'payment', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('paypal_secret', 'PAYPAL_SECRET', 'EFqQfxdKow-h-wBYBcgtffeb7wwi5fAozOq1NA9BZoqEQ8nOG5nViv-qC76ngm_0xmw_y7lZQL6PFjzV', 'string', 'payment', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('redis_cache_db', 'REDIS_CACHE_DB', '1', 'integer', 'infrastructure', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('redis_host', 'REDIS_HOST', '127.0.0.1', 'string', 'infrastructure', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('redis_limiter_db', 'REDIS_LIMITER_DB', '0', 'integer', 'infrastructure', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('redis_password', 'REDIS_PASSWORD', '', 'string', 'infrastructure', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 1),
('redis_port', 'REDIS_PORT', '38469', 'integer', 'infrastructure', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('redis_socket_path', 'REDIS_SOCKET_PATH', '/home2/ashlya/.redis/redis.sock', 'string', 'infrastructure', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('redis_use_socket', 'REDIS_USE_SOCKET', 'false', 'boolean', 'infrastructure', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('smtp_host', 'SMTP_HOST', 'mail.pearto.com', 'string', 'email', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('smtp_pass', 'SMTP_PASS', '0987@7890@Noreply', 'string', 'email', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('smtp_port', 'SMTP_PORT', '465', 'integer', 'email', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('smtp_secure', 'SMTP_SECURE', 'false', 'boolean', 'email', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0),
('smtp_user', 'SMTP_USER', 'noreply@pearto.com', 'string', 'email', NULL, 0, 'GLOBAL', '2026-02-21 21:02:23', 0),
('stripe_secret_key', 'STRIPE_SECRET_KEY', 'gAAAAABpmdWPamcjHKyG5CyNzqRvQLKAfhsuuDcfxrdKfgOQB3EaCvzAyWQuQlTVVutMcdjdOGBFLOwE0-SMp5PGBDSPQCdeQLb0VN5olah3LZTgzrtLEUCUpgQQhJ-21MwQj6n56ku04jEPeiUUyALy0ZjlVu9pcCndYh4VJzCOlOcQT-0u3HBFii7dKvsOoTrvW_9bekOpaKGpe927KCqwrRqvOiRMRg==', 'string', 'payment', NULL, 0, 'GLOBAL', '2026-02-21 15:55:59', 1),
('upload_folder', 'UPLOAD_FOLDER', 'uploads/documents', 'string', 'general', NULL, 0, 'GLOBAL', '2026-02-21 21:17:24', 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `settings`
--
ALTER TABLE `settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `key` (`key`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
