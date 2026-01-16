-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jan 16, 2026 at 09:19 AM
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
-- Table structure for table `affiliates`
--

CREATE TABLE `affiliates` (
  `id` varchar(255) NOT NULL,
  `providerId` text NOT NULL,
  `category` text NOT NULL,
  `affiliateUrl` text NOT NULL,
  `linkName` text DEFAULT NULL,
  `calculators` text DEFAULT NULL,
  `priority` int(11) DEFAULT NULL,
  `updatedAt` text NOT NULL,
  `active` int(11) DEFAULT NULL,
  `country_code` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `agent_runs`
--

CREATE TABLE `agent_runs` (
  `id` varchar(255) NOT NULL,
  `topic` text NOT NULL,
  `symbols` text DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  `steps` text DEFAULT NULL,
  `articleId` varchar(255) DEFAULT NULL,
  `error` text DEFAULT NULL,
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ai_generation_runs`
--

CREATE TABLE `ai_generation_runs` (
  `id` varchar(255) NOT NULL,
  `topic` text DEFAULT NULL,
  `symbols` text DEFAULT NULL,
  `articleId` varchar(255) DEFAULT NULL,
  `createdAt` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ai_post_drafts`
--

CREATE TABLE `ai_post_drafts` (
  `id` varchar(255) NOT NULL,
  `topic` varchar(255) NOT NULL,
  `outline` text NOT NULL,
  `draft` text NOT NULL,
  `createdAt` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `analyst_recommendations`
--

CREATE TABLE `analyst_recommendations` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `firm` varchar(100) DEFAULT NULL,
  `to_grade` varchar(50) DEFAULT NULL,
  `from_grade` varchar(50) DEFAULT NULL,
  `action` varchar(50) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `target_high` decimal(18,6) DEFAULT NULL,
  `target_low` decimal(18,6) DEFAULT NULL,
  `target_mean` decimal(18,6) DEFAULT NULL,
  `target_median` decimal(18,6) DEFAULT NULL,
  `current_price` decimal(18,6) DEFAULT NULL,
  `strong_buy` int(11) DEFAULT 0,
  `buy` int(11) DEFAULT 0,
  `hold` int(11) DEFAULT 0,
  `sell` int(11) DEFAULT 0,
  `strong_sell` int(11) DEFAULT 0,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `analytics_events`
--

CREATE TABLE `analytics_events` (
  `id` varchar(64) NOT NULL,
  `ts` varchar(40) NOT NULL,
  `type` varchar(100) NOT NULL,
  `page` varchar(255) DEFAULT NULL,
  `userId` varchar(64) DEFAULT NULL,
  `sessionId` varchar(64) DEFAULT NULL,
  `meta` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `api_registry`
--

CREATE TABLE `api_registry` (
  `id` varchar(64) NOT NULL,
  `name` varchar(255) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `baseUrl` varchar(500) DEFAULT NULL,
  `docsUrl` varchar(500) DEFAULT NULL,
  `authType` varchar(100) DEFAULT NULL,
  `enabled` smallint(6) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `createdAt` varchar(40) NOT NULL,
  `updatedAt` varchar(40) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `appearance`
--

CREATE TABLE `appearance` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `theme` varchar(100) DEFAULT NULL,
  `primaryColor` varchar(50) DEFAULT NULL,
  `secondaryColor` varchar(50) DEFAULT NULL,
  `active` int(11) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `articles`
--

CREATE TABLE `articles` (
  `id` varchar(255) NOT NULL,
  `slug` varchar(255) NOT NULL,
  `title` text NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `metaDescription` text DEFAULT NULL,
  `keywords` text DEFAULT NULL,
  `json` text NOT NULL,
  `createdAt` datetime NOT NULL,
  `updatedAt` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `audit_events`
--

CREATE TABLE `audit_events` (
  `id` varchar(255) NOT NULL,
  `ts` datetime NOT NULL,
  `actor` varchar(255) DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `entity` varchar(100) DEFAULT NULL,
  `entityId` varchar(255) DEFAULT NULL,
  `meta` text DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` varchar(64) NOT NULL,
  `country_code` varchar(2) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `firstName` varchar(100) DEFAULT NULL,
  `lastName` varchar(100) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `service` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `time` varchar(20) DEFAULT NULL,
  `status` enum('pending','confirmed','cancelled','completed') DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `bulk_transactions`
--

CREATE TABLE `bulk_transactions` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `transaction_date` datetime DEFAULT NULL,
  `buyer_broker` int(11) DEFAULT NULL,
  `seller_broker` int(11) DEFAULT NULL,
  `quantity` bigint(20) DEFAULT NULL,
  `price` decimal(18,6) DEFAULT NULL,
  `amount` decimal(20,2) DEFAULT NULL,
  `change_percent` decimal(10,4) DEFAULT NULL,
  `transaction_type` enum('bulk','block','cross') DEFAULT NULL,
  `exchange` varchar(50) DEFAULT NULL,
  `country_code` varchar(5) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `chat_messages`
--

CREATE TABLE `chat_messages` (
  `id` varchar(255) NOT NULL,
  `conversation_id` varchar(255) DEFAULT NULL,
  `sender_id` int(11) DEFAULT NULL,
  `sender_type` enum('user','agent','bot') DEFAULT NULL,
  `message` text NOT NULL,
  `attachments` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`attachments`)),
  `is_read` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `commodities_data`
--

CREATE TABLE `commodities_data` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `price` decimal(18,6) DEFAULT NULL,
  `change` decimal(18,6) DEFAULT NULL,
  `change_percent` decimal(10,4) DEFAULT NULL,
  `day_high` decimal(18,6) DEFAULT NULL,
  `day_low` decimal(18,6) DEFAULT NULL,
  `year_high` decimal(18,6) DEFAULT NULL,
  `year_low` decimal(18,6) DEFAULT NULL,
  `unit` varchar(20) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `commodities_data`
--

INSERT INTO `commodities_data` (`id`, `symbol`, `name`, `price`, `change`, `change_percent`, `day_high`, `day_low`, `year_high`, `year_low`, `unit`, `currency`, `last_updated`) VALUES
(1, 'GC', 'Gold', 2340.000000, -36.238040, -1.5486, 2386.800000, 2293.200000, NULL, NULL, 'oz', 'USD', '2026-01-07 11:48:09'),
(2, 'SI', 'Silver', 28.500000, 0.682324, 2.3941, 29.070000, 27.930000, NULL, NULL, 'oz', 'USD', '2026-01-07 11:48:09'),
(3, 'CL', 'Crude Oil WTI', 78.000000, -1.406513, -1.8032, 79.560000, 76.440000, NULL, NULL, 'barrel', 'USD', '2026-01-07 11:48:09'),
(4, 'BZ', 'Brent Crude', 82.000000, 1.118881, 1.3645, 83.640000, 80.360000, NULL, NULL, 'barrel', 'USD', '2026-01-07 11:48:09'),
(5, 'NG', 'Natural Gas', 2.800000, 0.048673, 1.7383, 2.856000, 2.744000, NULL, NULL, 'MMBtu', 'USD', '2026-01-07 11:48:09'),
(6, 'HG', 'Copper', 4.200000, -0.040186, -0.9568, 4.284000, 4.116000, NULL, NULL, 'lb', 'USD', '2026-01-07 11:48:09'),
(7, 'GC=F', 'Gold', 4600.800000, -22.900390, -0.4953, 4625.500000, 4597.800000, 4635.000000, 2724.800000, 'oz', 'USD', '2026-01-16 02:44:01'),
(8, 'SI=F', 'Silver', 89.925000, -2.421997, -2.6227, 92.645000, 89.670000, 93.000000, 28.310000, 'oz', 'USD', '2026-01-16 02:44:02'),
(9, 'PL=F', 'Platinum', 2357.500000, -52.399902, -2.1744, 2430.500000, 2351.100000, 2467.700000, 884.500000, 'oz', 'USD', '2026-01-16 02:44:03'),
(10, 'PA=F', 'Palladium', 1804.000000, -71.800050, -3.8277, 1877.500000, 1802.500000, 1984.700000, 876.600000, 'oz', 'USD', '2026-01-16 02:44:03'),
(11, 'HG=F', 'Copper', 5.938000, -0.053500, -0.8928, 6.024500, 5.934500, 6.024500, 4.098500, 'lb', 'USD', '2026-01-16 02:44:03'),
(12, 'CL=F', 'Crude Oil WTI', 59.020000, -0.060001, -0.1016, 59.300000, 58.980000, 79.440000, 54.980000, 'barrel', 'USD', '2026-01-16 02:44:04'),
(13, 'BZ=F', 'Brent Crude', 63.630000, -0.129997, -0.2039, 63.920000, 63.620000, 81.930000, 58.390000, 'barrel', 'USD', '2026-01-16 02:44:04'),
(14, 'NG=F', 'Natural Gas', 3.148000, 0.020000, 0.6394, 3.159000, 3.140000, 5.496000, 2.622000, 'MMBtu', 'USD', '2026-01-16 02:44:05'),
(15, 'RB=F', 'RBOB Gasoline', 1.808000, -0.002300, -0.1271, 1.816800, 1.808000, 2.414100, 1.665600, 'gallon', 'USD', '2026-01-16 02:44:05'),
(16, 'HO=F', 'Heating Oil', 2.187800, -0.007900, -0.3598, 2.196500, 2.185500, 2.740000, 1.933800, 'gallon', 'USD', '2026-01-16 02:44:05'),
(17, 'ZC=F', 'Corn', 420.250000, 0.000000, 0.0000, 421.500000, 420.000000, 504.500000, 368.750000, 'bushel', 'USX', '2026-01-16 02:44:06'),
(18, 'ZW=F', 'Wheat', 510.750000, 0.250000, 0.0490, 512.000000, 510.250000, 609.000000, 492.250000, 'bushel', 'USX', '2026-01-16 02:44:06'),
(19, 'ZS=F', 'Soybeans', 1053.250000, 0.250000, 0.0237, 1056.250000, 1051.750000, 1169.500000, 960.750000, 'bushel', 'USX', '2026-01-16 02:44:06'),
(20, 'KC=F', 'Coffee', 358.800000, 0.699982, 0.1955, 359.000000, 350.600000, 440.850000, 283.650000, 'lb', 'USX', '2026-01-16 02:44:07'),
(21, 'SB=F', 'Sugar', 14.590000, 0.020000, 0.1373, 14.680000, 14.570000, 21.570000, 14.040000, 'lb', 'USX', '2026-01-16 02:44:07'),
(22, 'CC=F', 'Cocoa', 4979.000000, 13.000000, 0.2618, 5083.000000, 4839.000000, 11789.000000, 4839.000000, 'metric ton', 'USD', '2026-01-16 02:44:07'),
(23, 'CT=F', 'Cotton', 64.990000, 0.000000, 0.0000, 63.700000, 63.150000, 73.500000, 60.790000, 'lb', 'USX', '2026-01-16 02:44:08'),
(24, 'LE=F', 'Live Cattle', 236.075000, 0.925003, 0.3934, 236.200000, 234.950000, 246.775000, 189.500000, 'lb', 'USX', '2026-01-16 02:44:08'),
(25, 'HE=F', 'Lean Hogs', 87.800000, 2.100006, 2.4504, 87.900000, 85.600000, 113.700000, 77.350000, 'lb', 'USX', '2026-01-16 02:44:08');

-- --------------------------------------------------------

--
-- Table structure for table `contact_messages`
--

CREATE TABLE `contact_messages` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `message` text NOT NULL,
  `status` enum('new','read','replied','closed') DEFAULT NULL,
  `replied_by` int(11) DEFAULT NULL,
  `replied_at` datetime DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `content_providers`
--

CREATE TABLE `content_providers` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `base_url` text DEFAULT NULL,
  `logo_url` text DEFAULT NULL,
  `is_premium` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `countries`
--

CREATE TABLE `countries` (
  `code` varchar(2) NOT NULL,
  `name` varchar(100) NOT NULL,
  `native_name` varchar(100) DEFAULT NULL,
  `currency_code` varchar(3) DEFAULT NULL,
  `currency_symbol` varchar(10) DEFAULT NULL,
  `currency_name` varchar(50) DEFAULT NULL,
  `default_market_index` varchar(50) DEFAULT NULL,
  `timezone` varchar(50) DEFAULT NULL,
  `flag_emoji` varchar(10) DEFAULT NULL,
  `phone_code` varchar(10) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `sort_order` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `countries`
--

INSERT INTO `countries` (`code`, `name`, `native_name`, `currency_code`, `currency_symbol`, `currency_name`, `default_market_index`, `timezone`, `flag_emoji`, `phone_code`, `is_active`, `sort_order`) VALUES
('AE', 'UAE', NULL, 'AED', 'د.إ', NULL, NULL, NULL, '🇦🇪', NULL, 1, 0),
('AU', 'Australia', NULL, 'AUD', 'A$', NULL, NULL, NULL, '🇦🇺', NULL, 1, 0),
('CA', 'Canada', NULL, 'CAD', 'C$', NULL, NULL, NULL, '🇨🇦', NULL, 1, 0),
('DE', 'Germany', NULL, 'EUR', '€', NULL, NULL, NULL, '🇩🇪', NULL, 1, 0),
('IN', 'India', NULL, 'INR', '₹', NULL, NULL, NULL, '🇮🇳', NULL, 1, 0),
('JP', 'Japan', NULL, 'JPY', '¥', NULL, NULL, NULL, '🇯🇵', NULL, 1, 0),
('NP', 'Nepal', NULL, 'NPR', 'Rs.', NULL, NULL, NULL, '🇳🇵', NULL, 1, 0),
('SG', 'Singapore', NULL, 'SGD', 'S$', NULL, NULL, NULL, '🇸🇬', NULL, 1, 0),
('UK', 'United Kingdom', NULL, 'GBP', '£', NULL, NULL, NULL, '🇬🇧', NULL, 1, 0),
('US', 'United States', NULL, 'USD', '$', NULL, NULL, NULL, '🇺🇸', NULL, 1, 0);

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `long_description` text DEFAULT NULL,
  `instructor_id` int(11) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `level` enum('Beginner','Intermediate','Advanced') DEFAULT NULL,
  `duration_hours` int(11) DEFAULT NULL,
  `duration_weeks` int(11) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `discount_price` decimal(10,2) DEFAULT NULL,
  `thumbnail_url` text DEFAULT NULL,
  `video_url` text DEFAULT NULL,
  `is_published` tinyint(1) DEFAULT NULL,
  `is_free` tinyint(1) DEFAULT NULL,
  `enrollment_count` int(11) DEFAULT NULL,
  `rating` decimal(2,1) DEFAULT NULL,
  `rating_count` int(11) DEFAULT NULL,
  `requirements` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`requirements`)),
  `what_you_learn` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`what_you_learn`)),
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`id`, `title`, `slug`, `description`, `long_description`, `instructor_id`, `category`, `level`, `duration_hours`, `duration_weeks`, `price`, `discount_price`, `thumbnail_url`, `video_url`, `is_published`, `is_free`, `enrollment_count`, `rating`, `rating_count`, `requirements`, `what_you_learn`, `country_code`, `created_at`, `updated_at`) VALUES
(1, 'Investing 101: Getting Started', 'investing-101-getting-started', 'Learn the basics of investing, from stocks to mutual funds.', NULL, NULL, 'Investing', 'Beginner', 2, NULL, NULL, NULL, NULL, NULL, 1, 1, 0, 0.0, 0, NULL, NULL, 'GLOBAL', '2026-01-08 12:29:02', '2026-01-14 22:04:50'),
(2, 'Technical Analysis Masterclass', 'technical-analysis-masterclass', 'Master chart patterns, indicators, and trading strategies.', NULL, NULL, 'Trading', 'Intermediate', 5, NULL, NULL, NULL, NULL, NULL, 1, 1, 0, 0.0, 0, NULL, NULL, 'GLOBAL', '2026-01-08 12:29:02', '2026-01-14 22:04:50'),
(3, 'Cryptocurrency Fundamentals', 'cryptocurrency-fundamentals', 'Understand blockchain, Bitcoin, and the crypto ecosystem.', NULL, NULL, 'Crypto', 'Beginner', 3, NULL, NULL, NULL, NULL, NULL, 1, 1, 0, 0.0, 0, NULL, NULL, 'GLOBAL', '2026-01-08 12:29:02', '2026-01-14 22:04:50'),
(4, 'Options Trading Strategies', 'options-trading-strategies', 'Advanced options strategies for income and hedging.', NULL, NULL, 'Trading', 'Advanced', 4, NULL, NULL, NULL, NULL, NULL, 1, 1, 0, 0.0, 0, NULL, NULL, 'GLOBAL', '2026-01-08 12:29:02', '2026-01-14 22:04:50'),
(5, 'Personal Finance Basics', 'personal-finance-basics', 'Budgeting, saving, and building wealth from scratch.', NULL, NULL, 'Finance', 'Beginner', 2, NULL, NULL, NULL, NULL, NULL, 1, 1, 0, 0.0, 0, NULL, NULL, 'GLOBAL', '2026-01-08 12:29:02', '2026-01-14 22:04:50'),
(6, 'Stock Market Fundamentals', 'stock-market-fundamentals', 'Deep dive into how the stock market works, valuation methods, and stock picking.', NULL, 1, 'Investing', 'Beginner', 6, NULL, 0.00, NULL, NULL, NULL, 1, 1, 1351, 4.2, 46, NULL, NULL, 'GLOBAL', '2026-01-09 11:29:35', '2026-01-14 22:04:50'),
(7, 'Forex Trading Essentials', 'forex-trading-essentials', 'Learn currency trading, pip calculations, and forex market dynamics.', NULL, 1, 'Trading', 'Intermediate', 7, NULL, 79.00, NULL, NULL, NULL, 1, 0, 1173, 4.8, 27, NULL, NULL, 'GLOBAL', '2026-01-09 11:29:35', '2026-01-14 22:04:50'),
(8, 'Retirement Planning Guide', 'retirement-planning-guide', 'Plan for a secure retirement with strategies for 401k, IRA, and pension optimization.', NULL, 1, 'Finance', 'Intermediate', 4, NULL, 0.00, NULL, NULL, NULL, 1, 1, 149, 4.9, 129, NULL, NULL, 'GLOBAL', '2026-01-09 11:29:35', '2026-01-14 22:04:50'),
(9, 'DeFi & Web3 Deep Dive', 'defi-&-web3-deep-dive', 'Explore decentralized finance, smart contracts, and the future of web3.', NULL, 1, 'Crypto', 'Advanced', 8, NULL, 129.00, NULL, NULL, NULL, 1, 0, 1350, 4.1, 118, NULL, NULL, 'GLOBAL', '2026-01-09 11:29:35', '2026-01-14 22:04:50'),
(10, 'Value Investing Like Warren Buffett', 'value-investing-like-warren-buffett', 'Learn the principles of value investing from the greatest investor of all time.', NULL, 1, 'Investing', 'Intermediate', 6, NULL, 89.00, NULL, NULL, NULL, 1, 0, 218, 4.5, 102, NULL, NULL, 'GLOBAL', '2026-01-09 11:29:35', '2026-01-14 22:04:50');

-- --------------------------------------------------------

--
-- Table structure for table `course_modules`
--

CREATE TABLE `course_modules` (
  `id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `video_url` text DEFAULT NULL,
  `content` text DEFAULT NULL,
  `is_free` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `course_modules`
--

INSERT INTO `course_modules` (`id`, `course_id`, `title`, `description`, `order_index`, `duration_minutes`, `video_url`, `content`, `is_free`, `created_at`) VALUES
(1, 1, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(2, 1, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(3, 1, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(4, 1, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(5, 1, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(6, 1, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(7, 2, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(8, 2, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(9, 2, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(10, 2, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(11, 2, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(12, 2, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(13, 3, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(14, 3, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(15, 3, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(16, 3, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(17, 3, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(18, 3, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(19, 4, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(20, 4, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(21, 4, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(22, 4, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(23, 4, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(24, 4, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(25, 5, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(26, 5, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(27, 5, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(28, 5, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(29, 5, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(30, 5, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(31, 6, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(32, 6, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(33, 6, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(34, 6, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(35, 6, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(36, 6, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(37, 7, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(38, 7, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(39, 7, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(40, 7, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(41, 7, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(42, 7, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(43, 8, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(44, 8, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(45, 8, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(46, 8, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(47, 8, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(48, 8, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(49, 9, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(50, 9, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(51, 9, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(52, 9, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(53, 9, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(54, 9, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05'),
(55, 10, 'Introduction & Overview', 'Get started with the fundamentals and understand the course structure.', 0, 30, NULL, NULL, 1, '2026-01-09 11:44:05'),
(56, 10, 'Core Concepts', 'Deep dive into the essential concepts you need to master.', 1, 45, NULL, NULL, 0, '2026-01-09 11:44:05'),
(57, 10, 'Practical Application', 'Apply what you learned through hands-on exercises.', 2, 60, NULL, NULL, 0, '2026-01-09 11:44:05'),
(58, 10, 'Advanced Strategies', 'Take your skills to the next level with advanced techniques.', 3, 55, NULL, NULL, 0, '2026-01-09 11:44:05'),
(59, 10, 'Real-World Case Studies', 'Learn from real examples and case studies.', 4, 40, NULL, NULL, 0, '2026-01-09 11:44:05'),
(60, 10, 'Final Project & Assessment', 'Complete your learning with a comprehensive project.', 5, 50, NULL, NULL, 0, '2026-01-09 11:44:05');

-- --------------------------------------------------------

--
-- Table structure for table `crypto_market_data`
--

CREATE TABLE `crypto_market_data` (
  `id` int(11) NOT NULL,
  `total_market_cap` decimal(20,2) DEFAULT NULL,
  `total_volume_24h` decimal(20,2) DEFAULT NULL,
  `btc_dominance` decimal(10,4) DEFAULT NULL,
  `eth_dominance` decimal(10,4) DEFAULT NULL,
  `active_cryptocurrencies` int(11) DEFAULT NULL,
  `active_exchanges` int(11) DEFAULT NULL,
  `market_cap_change_24h` decimal(10,4) DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `deposits`
--

CREATE TABLE `deposits` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `status` enum('pending','completed','failed') DEFAULT NULL,
  `transaction_ref` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dividends`
--

CREATE TABLE `dividends` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `dividend_type` enum('cash','bonus','both') DEFAULT NULL,
  `cash_percent` decimal(10,4) DEFAULT NULL,
  `bonus_percent` decimal(10,4) DEFAULT NULL,
  `total_percent` decimal(10,4) DEFAULT NULL,
  `dividend_amount` decimal(18,6) DEFAULT NULL,
  `ex_dividend_date` date DEFAULT NULL,
  `record_date` date DEFAULT NULL,
  `payment_date` date DEFAULT NULL,
  `book_closure_date` date DEFAULT NULL,
  `fiscal_year` varchar(20) DEFAULT NULL,
  `status` enum('proposed','approved','paid') DEFAULT NULL,
  `country_code` varchar(5) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `dividends`
--

INSERT INTO `dividends` (`id`, `symbol`, `company_name`, `dividend_type`, `cash_percent`, `bonus_percent`, `total_percent`, `dividend_amount`, `ex_dividend_date`, `record_date`, `payment_date`, `book_closure_date`, `fiscal_year`, `status`, `country_code`, `created_at`) VALUES
(1, 'KO', 'Coca-Cola Company (The)', 'cash', 286.0000, 0.0000, 286.0000, 2.040000, '2025-12-01', NULL, '2025-12-01', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:49'),
(2, 'JNJ', 'Johnson & Johnson', 'cash', 238.0000, 0.0000, 238.0000, 5.200000, '2026-02-24', NULL, '2025-11-25', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:51'),
(3, 'PG', 'Procter & Gamble Company (The)', 'cash', 289.0000, 0.0000, 289.0000, 4.230000, '2026-01-23', NULL, '2025-10-24', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:51'),
(4, 'MMM', '3M Company', 'cash', 172.0000, 0.0000, 172.0000, 2.920000, '2025-11-14', NULL, '2025-11-14', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:52'),
(5, 'PEP', 'Pepsico, Inc.', 'cash', 390.0000, 0.0000, 390.0000, 5.690000, '2025-12-05', NULL, '2025-12-05', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:52'),
(6, 'WMT', 'Walmart Inc.', 'cash', 78.0000, 0.0000, 78.0000, 0.940000, '2025-12-12', NULL, '2025-12-12', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:53'),
(7, 'MCD', 'McDonald\'s Corporation', 'cash', 241.0000, 0.0000, 241.0000, 7.440000, '2025-12-01', NULL, '2025-12-01', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:53'),
(8, 'CL', 'Colgate-Palmolive Company', 'cash', 246.0000, 0.0000, 246.0000, 2.080000, '2026-01-21', NULL, '2025-10-17', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:53'),
(9, 'XOM', 'Exxon Mobil Corporation', 'cash', 316.0000, 0.0000, 316.0000, 4.120000, '2025-11-14', NULL, '2025-11-14', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:54'),
(10, 'CVX', 'Chevron Corporation', 'cash', 409.0000, 0.0000, 409.0000, 6.840000, '2025-11-18', NULL, '2025-11-18', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:54'),
(11, 'IBM', 'International Business Machines', 'cash', 217.0000, 0.0000, 217.0000, 6.720000, '2025-11-10', NULL, '2025-11-10', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:55'),
(12, 'T', 'AT&T Inc.', 'cash', 470.0000, 0.0000, 470.0000, 1.110000, '2026-01-12', NULL, '2026-01-12', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:56'),
(13, 'VZ', 'Verizon Communications Inc.', 'cash', 693.0000, 0.0000, 693.0000, 2.760000, '2026-01-12', NULL, '2026-01-12', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:56'),
(14, 'ABBV', 'AbbVie Inc.', 'cash', 312.0000, 0.0000, 312.0000, 6.920000, '2026-01-16', NULL, '2025-10-15', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:56'),
(15, 'MRK', 'Merck & Company, Inc.', 'cash', 306.0000, 0.0000, 306.0000, 3.400000, '2025-12-15', NULL, '2025-12-15', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:57'),
(16, 'PFE', 'Pfizer, Inc.', 'cash', 672.0000, 0.0000, 672.0000, 1.720000, '2026-01-23', NULL, '2025-11-07', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:57'),
(17, 'CAT', 'Caterpillar, Inc.', 'cash', 95.0000, 0.0000, 95.0000, 6.040000, '2026-01-20', NULL, '2025-10-20', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:58'),
(18, 'EMR', 'Emerson Electric Company', 'cash', 150.0000, 0.0000, 150.0000, 2.220000, '2025-11-14', NULL, '2025-11-14', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:58'),
(19, 'SHW', 'Sherwin-Williams Company (The)', 'cash', 89.0000, 0.0000, 89.0000, 3.160000, '2025-11-14', NULL, '2025-11-14', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:58'),
(20, 'GD', 'General Dynamics Corporation', 'cash', 164.0000, 0.0000, 164.0000, 6.000000, '2026-01-16', NULL, '2025-10-10', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:59'),
(21, 'MO', 'Altria Group, Inc.', 'cash', 690.0000, 0.0000, 690.0000, 4.240000, '2025-12-26', NULL, '2025-12-26', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:59'),
(22, 'PM', 'Philip Morris International Inc', 'cash', 344.0000, 0.0000, 344.0000, 5.880000, '2025-12-26', NULL, '2025-12-26', NULL, NULL, 'approved', 'US', '2026-01-10 04:11:59'),
(23, 'BTI', 'British American Tobacco  Indus', 'cash', 546.0000, 0.0000, 546.0000, 3.140000, '2025-12-30', NULL, '2025-12-30', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:00'),
(24, 'LYB', 'LyondellBasell Industries NV', 'cash', 1054.0000, 0.0000, 1054.0000, 5.480000, '2025-12-01', NULL, '2025-12-01', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:01'),
(25, 'OKE', 'ONEOK, Inc.', 'cash', 543.0000, 0.0000, 543.0000, 4.120000, '2025-11-03', NULL, '2025-11-03', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:02'),
(26, 'KMI', 'Kinder Morgan, Inc.', 'cash', 425.0000, 0.0000, 425.0000, 1.170000, '2025-11-03', NULL, '2025-11-03', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:02'),
(27, 'EPD', 'Enterprise Products Partners L.', 'cash', 669.0000, 0.0000, 669.0000, 2.180000, '2026-01-30', NULL, '2025-10-31', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:02'),
(28, 'AAPL', 'Apple Inc.', 'cash', 40.0000, 0.0000, 40.0000, 1.040000, '2025-11-10', NULL, '2025-11-10', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:03'),
(29, 'MSFT', 'Microsoft Corporation', 'cash', 79.0000, 0.0000, 79.0000, 3.640000, '2026-02-19', NULL, '2025-11-20', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:04'),
(30, 'CSCO', 'Cisco Systems, Inc.', 'cash', 220.0000, 0.0000, 220.0000, 1.640000, '2026-01-02', NULL, '2026-01-02', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:04'),
(31, 'TXN', 'Texas Instruments Incorporated', 'cash', 294.0000, 0.0000, 294.0000, 5.680000, '2025-10-31', NULL, '2025-10-31', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:05'),
(32, 'AVGO', 'Broadcom Inc.', 'cash', 76.0000, 0.0000, 76.0000, 2.600000, '2025-12-22', NULL, '2025-12-22', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:05'),
(33, 'QCOM', 'QUALCOMM Incorporated', 'cash', 216.0000, 0.0000, 216.0000, 3.560000, '2025-12-04', NULL, '2025-12-04', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:05'),
(34, 'HPQ', 'HP Inc.', 'cash', 578.0000, 0.0000, 578.0000, 1.200000, '2025-12-11', NULL, '2025-12-11', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:06'),
(35, 'ORCL', 'Oracle Corporation', 'cash', 103.0000, 0.0000, 103.0000, 2.000000, '2026-01-09', NULL, '2026-01-09', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:06'),
(36, 'JPM', 'JP Morgan Chase & Co.', 'cash', 195.0000, 0.0000, 195.0000, 6.000000, '2026-01-06', NULL, '2026-01-06', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:07'),
(37, 'BAC', 'Bank of America Corporation', 'cash', 205.0000, 0.0000, 205.0000, 1.120000, '2025-12-05', NULL, '2025-12-05', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:07'),
(38, 'WFC', 'Wells Fargo & Company', 'cash', 192.0000, 0.0000, 192.0000, 1.800000, '2025-11-07', NULL, '2025-11-07', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:08'),
(39, 'C', 'Citigroup, Inc.', 'cash', 214.0000, 0.0000, 214.0000, 2.400000, '2026-02-02', NULL, '2025-11-03', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:08'),
(40, 'GS', 'Goldman Sachs Group, Inc. (The)', 'cash', 172.0000, 0.0000, 172.0000, 16.000000, '2025-12-02', NULL, '2025-12-02', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:08'),
(41, 'MS', 'Morgan Stanley', 'cash', 221.0000, 0.0000, 221.0000, 4.000000, '2025-10-31', NULL, '2025-10-31', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:09'),
(42, 'USB', 'U.S. Bancorp', 'cash', 381.0000, 0.0000, 381.0000, 2.040000, '2025-12-31', NULL, '2025-12-31', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:09'),
(43, 'PNC', 'PNC Financial Services Group, I', 'cash', 320.0000, 0.0000, 320.0000, 6.800000, '2026-01-20', NULL, '2025-10-14', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:09'),
(44, 'TFC', 'Truist Financial Corporation', 'cash', 417.0000, 0.0000, 417.0000, 2.080000, '2025-11-14', NULL, '2025-11-14', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:10'),
(45, 'KEY', 'KeyCorp', 'cash', 391.0000, 0.0000, 391.0000, 0.820000, '2025-12-02', NULL, '2025-12-02', NULL, NULL, 'approved', 'US', '2026-01-10 04:12:10');

-- --------------------------------------------------------

--
-- Table structure for table `earnings_calendar`
--

CREATE TABLE `earnings_calendar` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `earnings_date` datetime NOT NULL,
  `eps_estimate` decimal(18,6) DEFAULT NULL,
  `eps_actual` decimal(18,6) DEFAULT NULL,
  `surprise_percent` decimal(10,4) DEFAULT NULL,
  `revenue_estimate` bigint(20) DEFAULT NULL,
  `revenue_actual` bigint(20) DEFAULT NULL,
  `market_cap` bigint(20) DEFAULT NULL,
  `before_after_market` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `economic_events`
--

CREATE TABLE `economic_events` (
  `id` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `country` varchar(50) DEFAULT NULL,
  `event_date` datetime DEFAULT NULL,
  `importance` enum('low','medium','high') DEFAULT NULL,
  `forecast` varchar(50) DEFAULT NULL,
  `previous` varchar(50) DEFAULT NULL,
  `actual` varchar(50) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `source` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `email_templates`
--

CREATE TABLE `email_templates` (
  `id` varchar(255) NOT NULL,
  `name` varchar(100) NOT NULL,
  `subject` varchar(255) DEFAULT NULL,
  `body_html` text DEFAULT NULL,
  `body_text` text DEFAULT NULL,
  `variables` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`variables`)),
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `email_templates`
--

INSERT INTO `email_templates` (`id`, `name`, `subject`, `body_html`, `body_text`, `variables`, `is_active`, `created_at`, `updated_at`) VALUES
('daily_digest', 'Daily Market Digest', '📊 Your Daily Market Digest', '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset=\"utf-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body style=\"margin: 0; padding: 0; background-color: #f4f7fa; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\">\n    <div style=\"max-width: 600px; margin: 0 auto; padding: 40px 20px;\">\n        <div style=\"background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;\">\n            <h1 style=\"color: white; margin: 0; font-size: 24px;\">📊 Daily Market Digest</h1>\n            <p style=\"color: #94a3b8; margin-top: 10px;\">{{date}}</p>\n        </div>\n        <div style=\"background: white; padding: 40px; border-radius: 0 0 16px 16px;\">\n            <p style=\"font-size: 16px; color: #333;\">Hi {{user_name}},</p>\n            <p style=\"font-size: 16px; color: #333;\">Here\'s your daily summary:</p>\n            \n            <div style=\"display: flex; gap: 15px; margin: 25px 0;\">\n                <div style=\"flex: 1; background: #f0fdf4; padding: 15px; border-radius: 8px; text-align: center;\">\n                    <div style=\"font-size: 28px; font-weight: bold; color: #10b981;\">📈 {{gainers_count}}</div>\n                    <div style=\"font-size: 12px; color: #666;\">Gainers</div>\n                </div>\n                <div style=\"flex: 1; background: #fef2f2; padding: 15px; border-radius: 8px; text-align: center;\">\n                    <div style=\"font-size: 28px; font-weight: bold; color: #ef4444;\">📉 {{losers_count}}</div>\n                    <div style=\"font-size: 12px; color: #666;\">Losers</div>\n                </div>\n            </div>\n            \n            <p style=\"font-size: 14px; color: #666;\">{{market_summary}}</p>\n            \n            <div style=\"text-align: center; margin: 30px 0;\">\n                <a href=\"{{dashboard_url}}\" style=\"display: inline-block; background: #10b981; color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600;\">View Full Report</a>\n            </div>\n            \n            <hr style=\"border: none; border-top: 1px solid #eee; margin: 30px 0;\">\n            <p style=\"font-size: 12px; color: #999; text-align: center;\">You\'re subscribed to daily digests from {{app_name}}.</p>\n        </div>\n    </div>\n</body>\n</html>', '📊 Daily Market Digest - {{date}}\n\nHi {{user_name}},\n\nHere\'s your daily summary:\n\n📈 Gainers: {{gainers_count}}\n📉 Losers: {{losers_count}}\n\n{{market_summary}}\n\nView full report: {{dashboard_url}}', '[\"user_name\", \"date\", \"gainers_count\", \"losers_count\", \"top_gainer\", \"top_loser\", \"market_summary\", \"dashboard_url\", \"app_name\"]', 1, '2026-01-16 01:53:35', '2026-01-16 01:53:35'),
('earnings_reminder', 'Earnings Reminder', '📅 Earnings Tomorrow: {{symbols}}', '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset=\"utf-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body style=\"margin: 0; padding: 0; background-color: #f4f7fa; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\">\n    <div style=\"max-width: 600px; margin: 0 auto; padding: 40px 20px;\">\n        <div style=\"background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;\">\n            <h1 style=\"color: white; margin: 0; font-size: 24px;\">📅 Earnings Tomorrow</h1>\n        </div>\n        <div style=\"background: white; padding: 40px; border-radius: 0 0 16px 16px;\">\n            <p style=\"font-size: 16px; color: #333;\">Hi {{user_name}},</p>\n            <p style=\"font-size: 16px; color: #333;\">Companies on your watchlist are reporting earnings tomorrow:</p>\n            \n            <div style=\"background: #fffbeb; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;\">\n                <div style=\"font-size: 18px; font-weight: bold; color: #92400e;\">{{symbols}}</div>\n            </div>\n            \n            <p style=\"font-size: 14px; color: #666;\">Earnings announcements can cause significant price movements. Stay informed!</p>\n            \n            <div style=\"text-align: center; margin: 30px 0;\">\n                <a href=\"{{dashboard_url}}\" style=\"display: inline-block; background: #f59e0b; color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600;\">View Calendar</a>\n            </div>\n            \n            <hr style=\"border: none; border-top: 1px solid #eee; margin: 30px 0;\">\n            <p style=\"font-size: 12px; color: #999; text-align: center;\">You\'re receiving this because you have earnings alerts enabled on {{app_name}}.</p>\n        </div>\n    </div>\n</body>\n</html>', '📅 Earnings Tomorrow\n\nHi {{user_name}},\n\nCompanies on your watchlist are reporting earnings tomorrow:\n\n{{symbols}}\n\nEarnings announcements can cause significant price movements. Stay informed!\n\nView Calendar: {{dashboard_url}}', '[\"user_name\", \"symbols\", \"earnings_count\", \"dashboard_url\", \"app_name\"]', 1, '2026-01-16 01:53:35', '2026-01-16 01:53:35'),
('login', 'Login Notification', 'New login to your Pearto Finance account', '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset=\"utf-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body style=\"margin: 0; padding: 0; background-color: #f4f7fa; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\">\n    <div style=\"max-width: 600px; margin: 0 auto; padding: 40px 20px;\">\n        <div style=\"background: #1a1a2e; border-radius: 16px 16px 0 0; padding: 30px; text-align: center;\">\n            <h1 style=\"color: white; margin: 0; font-size: 24px;\">🔐 Login Notification</h1>\n        </div>\n        <div style=\"background: white; padding: 40px; border-radius: 0 0 16px 16px;\">\n            <p style=\"font-size: 16px; color: #333;\">Hi {{user_name}},</p>\n            <p style=\"font-size: 16px; color: #333;\">We noticed a new login to your Pearto Finance account.</p>\n            <div style=\"background: #f0f9ff; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0;\">\n                <p style=\"margin: 5px 0;\"><strong>Time:</strong> {{login_time}}</p>\n                <p style=\"margin: 5px 0;\"><strong>Device:</strong> {{device_info}}</p>\n                <p style=\"margin: 5px 0;\"><strong>IP Address:</strong> {{ip_address}}</p>\n            </div>\n            <p style=\"font-size: 14px; color: #666;\">If this was you, no action is needed. If you didn\'t log in, please secure your account immediately.</p>\n            <div style=\"text-align: center; margin: 30px 0;\">\n                <a href=\"{{security_url}}\" style=\"display: inline-block; background: #dc2626; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;\">Secure My Account</a>\n            </div>\n            <hr style=\"border: none; border-top: 1px solid #eee; margin: 30px 0;\">\n            <p style=\"font-size: 12px; color: #999; text-align: center;\">This is an automated security notification from {{app_name}}.</p>\n        </div>\n    </div>\n</body>\n</html>', 'Login Notification\n\nHi {{user_name}},\n\nWe noticed a new login to your Pearto Finance account.\n\nTime: {{login_time}}\nDevice: {{device_info}}\nIP: {{ip_address}}\n\nIf this was you, no action is needed. If you didn\'t log in, please secure your account.', '[\"user_name\", \"login_time\", \"device_info\", \"ip_address\", \"security_url\", \"app_name\"]', 1, '2026-01-16 01:53:35', '2026-01-16 01:53:35'),
('password_reset', 'Password Reset', 'Reset Your Pearto Finance Password', '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset=\"utf-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body style=\"margin: 0; padding: 0; background-color: #f4f7fa; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\">\n    <div style=\"max-width: 600px; margin: 0 auto; padding: 40px 20px;\">\n        <div style=\"background: #1a1a2e; border-radius: 16px 16px 0 0; padding: 30px; text-align: center;\">\n            <h1 style=\"color: white; margin: 0; font-size: 24px;\">🔑 Password Reset</h1>\n        </div>\n        <div style=\"background: white; padding: 40px; border-radius: 0 0 16px 16px;\">\n            <p style=\"font-size: 16px; color: #333;\">Hi {{user_name}},</p>\n            <p style=\"font-size: 16px; color: #333;\">We received a request to reset your password. Click the button below to create a new password:</p>\n            <div style=\"text-align: center; margin: 30px 0;\">\n                <a href=\"{{reset_url}}\" style=\"display: inline-block; background: #10b981; color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;\">Reset Password</a>\n            </div>\n            <p style=\"font-size: 14px; color: #666;\">Or use this code: <strong>{{reset_code}}</strong></p>\n            <p style=\"font-size: 14px; color: #666;\">This link expires in 15 minutes. If you didn\'t request this, ignore this email.</p>\n            <hr style=\"border: none; border-top: 1px solid #eee; margin: 30px 0;\">\n            <p style=\"font-size: 12px; color: #999; text-align: center;\">This is an automated message from {{app_name}}.</p>\n        </div>\n    </div>\n</body>\n</html>', 'Password Reset\n\nHi {{user_name}},\n\nWe received a request to reset your password.\n\nReset your password: {{reset_url}}\nOr use code: {{reset_code}}\n\nThis link expires in 15 minutes. If you didn\'t request this, ignore this email.', '[\"user_name\", \"reset_url\", \"reset_code\", \"app_name\"]', 1, '2026-01-16 01:53:35', '2026-01-16 01:53:35'),
('price_alert', 'Price Alert', '🎯 {{symbol}} Price Alert - Target Reached!', '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset=\"utf-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body style=\"margin: 0; padding: 0; background-color: #f4f7fa; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\">\n    <div style=\"max-width: 600px; margin: 0 auto; padding: 40px 20px;\">\n        <div style=\"background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;\">\n            <h1 style=\"color: white; margin: 0; font-size: 24px;\">🎯 Price Alert Triggered!</h1>\n        </div>\n        <div style=\"background: white; padding: 40px; border-radius: 0 0 16px 16px;\">\n            <p style=\"font-size: 16px; color: #333;\">Hi {{user_name}},</p>\n            <p style=\"font-size: 16px; color: #333;\">Your price alert for <strong>{{symbol}}</strong> has been triggered!</p>\n            \n            <div style=\"background: #f0fdf4; border: 2px solid #10b981; border-radius: 12px; padding: 25px; margin: 25px 0; text-align: center;\">\n                <div style=\"font-size: 32px; font-weight: bold; color: #059669;\">{{symbol}}</div>\n                <div style=\"font-size: 42px; font-weight: bold; color: #111; margin: 10px 0;\">${{current_price}}</div>\n                <div style=\"font-size: 14px; color: #666;\">Target: ${{target_price}} ({{direction}})</div>\n            </div>\n            \n            <p style=\"font-size: 14px; color: #666;\">This alert will not trigger again. Create a new alert if you want to track this stock further.</p>\n            \n            <div style=\"text-align: center; margin: 30px 0;\">\n                <a href=\"{{dashboard_url}}\" style=\"display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;\">View Dashboard</a>\n            </div>\n            \n            <hr style=\"border: none; border-top: 1px solid #eee; margin: 30px 0;\">\n            <p style=\"font-size: 12px; color: #999; text-align: center;\">You\'re receiving this because you set a price alert on {{app_name}}.</p>\n        </div>\n    </div>\n</body>\n</html>', '🎯 Price Alert Triggered!\n\nHi {{user_name}},\n\nYour price alert for {{symbol}} has been triggered!\n\n{{symbol}}: ${{current_price}}\nTarget: ${{target_price}} ({{direction}})\n\nThis alert will not trigger again. Create a new alert if you want to track this stock further.\n\nView Dashboard: {{dashboard_url}}', '[\"user_name\", \"symbol\", \"current_price\", \"target_price\", \"direction\", \"app_name\", \"dashboard_url\"]', 1, '2026-01-16 01:53:35', '2026-01-16 01:53:35'),
('signup', 'Welcome Email', 'Welcome to Pearto Finance! 🎉', '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset=\"utf-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body style=\"margin: 0; padding: 0; background-color: #f4f7fa; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\">\n    <div style=\"max-width: 600px; margin: 0 auto; padding: 40px 20px;\">\n        <div style=\"background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 16px 16px 0 0; padding: 40px; text-align: center;\">\n            <h1 style=\"color: white; margin: 0; font-size: 28px;\">Welcome to {{app_name}}! 🎉</h1>\n        </div>\n        <div style=\"background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);\">\n            <p style=\"font-size: 16px; color: #333; line-height: 1.6;\">Hi {{user_name}},</p>\n            <p style=\"font-size: 16px; color: #333; line-height: 1.6;\">Thank you for joining {{app_name}}! We\'re thrilled to have you on board.</p>\n            <p style=\"font-size: 16px; color: #333; line-height: 1.6;\">Your account has been successfully created. You can now:</p>\n            <ul style=\"font-size: 16px; color: #333; line-height: 2;\">\n                <li>Track your investment portfolio</li>\n                <li>Get real-time market insights</li>\n                <li>Access financial tools and calculators</li>\n                <li>Set price alerts for your watchlist</li>\n            </ul>\n            <div style=\"text-align: center; margin: 30px 0;\">\n                <a href=\"{{login_url}}\" style=\"display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;\">Get Started</a>\n            </div>\n            <hr style=\"border: none; border-top: 1px solid #eee; margin: 30px 0;\">\n            <p style=\"font-size: 12px; color: #999; text-align: center;\">This email was sent by {{app_name}}.</p>\n        </div>\n    </div>\n</body>\n</html>', 'Welcome to {{app_name}}!\n\nHi {{user_name}},\n\nThank you for joining {{app_name}}! We\'re thrilled to have you on board.\n\nYour account has been successfully created. You can now:\n- Track your investment portfolio\n- Get real-time market insights\n- Access financial tools and calculators\n- Set price alerts for your watchlist\n\nGet started: {{login_url}}', '[\"user_name\", \"user_email\", \"app_name\", \"login_url\"]', 1, '2026-01-16 01:53:35', '2026-01-16 01:53:35'),
('verification', 'Email Verification', 'Verify Your Email - Pearto Finance', '<!DOCTYPE html>\n<html>\n<head>\n    <meta charset=\"utf-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n</head>\n<body style=\"margin: 0; padding: 0; background-color: #f4f7fa; font-family: \'Segoe UI\', Tahoma, Geneva, Verdana, sans-serif;\">\n    <div style=\"max-width: 600px; margin: 0 auto; padding: 40px 20px;\">\n        <div style=\"background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;\">\n            <h1 style=\"color: white; margin: 0; font-size: 24px;\">✉️ Verify Your Email</h1>\n        </div>\n        <div style=\"background: white; padding: 40px; border-radius: 0 0 16px 16px;\">\n            <p style=\"font-size: 16px; color: #333;\">Hi {{user_name}},</p>\n            <p style=\"font-size: 16px; color: #333;\">Please use the following code to verify your email address:</p>\n            <div style=\"text-align: center; margin: 30px 0;\">\n                <div style=\"display: inline-block; background: #f0fdf4; border: 2px dashed #10b981; padding: 20px 40px; border-radius: 12px;\">\n                    <span style=\"font-size: 36px; font-weight: bold; color: #059669; letter-spacing: 8px;\">{{code}}</span>\n                </div>\n            </div>\n            <p style=\"font-size: 14px; color: #666;\">This code expires in 15 minutes.</p>\n            <hr style=\"border: none; border-top: 1px solid #eee; margin: 30px 0;\">\n            <p style=\"font-size: 12px; color: #999; text-align: center;\">This is an automated message from {{app_name}}.</p>\n        </div>\n    </div>\n</body>\n</html>', 'Verify Your Email\n\nHi {{user_name}},\n\nYour verification code is: {{code}}\n\nThis code expires in 15 minutes.', '[\"user_name\", \"code\", \"app_name\"]', 1, '2026-01-16 01:53:35', '2026-01-16 01:53:35');

-- --------------------------------------------------------

--
-- Table structure for table `faqs`
--

CREATE TABLE `faqs` (
  `id` varchar(50) NOT NULL,
  `question` text NOT NULL,
  `answer` text NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `show_on_homepage` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `faq_items`
--

CREATE TABLE `faq_items` (
  `id` int(11) NOT NULL,
  `question` text NOT NULL,
  `answer` text NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `forex_rates`
--

CREATE TABLE `forex_rates` (
  `id` int(11) NOT NULL,
  `base_currency` varchar(10) NOT NULL,
  `target_currency` varchar(10) NOT NULL,
  `rate` decimal(18,6) DEFAULT NULL,
  `change` decimal(18,6) DEFAULT NULL,
  `change_percent` decimal(10,4) DEFAULT NULL,
  `high` decimal(18,6) DEFAULT NULL,
  `low` decimal(18,6) DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `forex_rates`
--

INSERT INTO `forex_rates` (`id`, `base_currency`, `target_currency`, `rate`, `change`, `change_percent`, `high`, `low`, `last_updated`) VALUES
(1, 'EUR', 'USD', 1.085000, 0.004575, 0.4217, NULL, NULL, '2026-01-08 12:28:19'),
(2, 'GBP', 'USD', 1.265000, -0.001301, -0.1028, NULL, NULL, '2026-01-08 12:28:19'),
(3, 'USD', 'JPY', 155.500000, -0.017811, -0.0115, NULL, NULL, '2026-01-08 12:28:19'),
(4, 'USD', 'CHF', 0.892000, -0.002874, -0.3222, NULL, NULL, '2026-01-08 12:28:19'),
(5, 'AUD', 'USD', 0.635000, -0.000138, -0.0217, NULL, NULL, '2026-01-08 12:28:19'),
(6, 'USD', 'CAD', 1.435000, 0.000632, 0.0440, NULL, NULL, '2026-01-08 12:28:19'),
(7, 'NZD', 'USD', 0.565000, 0.001874, 0.3318, NULL, NULL, '2026-01-08 12:28:19'),
(8, 'USD', 'NPR', 136.500000, 0.654266, 0.4793, NULL, NULL, '2026-01-08 12:28:19'),
(9, 'USD', 'INR', 86.250000, 0.412305, 0.4780, NULL, NULL, '2026-01-08 12:28:19'),
(10, 'EUR', 'GBP', 0.858000, 0.003131, 0.3650, NULL, NULL, '2026-01-08 12:28:19');

-- --------------------------------------------------------

--
-- Table structure for table `glossary_terms`
--

CREATE TABLE `glossary_terms` (
  `id` int(11) NOT NULL,
  `term` varchar(100) NOT NULL,
  `definition` text NOT NULL,
  `category` enum('trading','investing','derivatives','banking','crypto','economics','technical') DEFAULT NULL,
  `related_terms` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`related_terms`)),
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `help_articles`
--

CREATE TABLE `help_articles` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `is_featured` tinyint(1) DEFAULT NULL,
  `view_count` int(11) DEFAULT NULL,
  `helpful_count` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `country_code` varchar(10) DEFAULT 'GLOBAL'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `help_articles`
--

INSERT INTO `help_articles` (`id`, `title`, `slug`, `content`, `category_id`, `is_featured`, `view_count`, `helpful_count`, `is_active`, `created_at`, `updated_at`, `country_code`) VALUES
(1, 'Getting Started with PeartoFinance', 'getting-started-with-peartofinance', 'Welcome to PeartoFinance! This guide will help you get started...', 1, 0, 0, 0, 1, '2026-01-14 22:01:54', '2026-01-14 22:01:54', 'US'),
(2, 'How to Read Stock Charts', 'how-to-read-stock-charts', 'Understanding stock charts is essential for making informed decisions...', 2, 0, 0, 0, 1, '2026-01-14 22:01:54', '2026-01-14 22:01:54', 'US'),
(3, 'Setting Up Price Alerts', 'setting-up-price-alerts', 'Never miss a price movement. Learn how to set up alerts...', 3, 0, 0, 0, 1, '2026-01-14 22:01:54', '2026-01-14 22:01:54', 'US'),
(4, 'Understanding Your Portfolio', 'understanding-your-portfolio', 'Your portfolio dashboard shows all your investments...', 3, 0, 0, 0, 1, '2026-01-14 22:01:54', '2026-01-14 22:01:54', 'US'),
(5, 'Security Best Practices', 'security-best-practices', 'Keep your account secure with these tips...', 4, 0, 0, 0, 1, '2026-01-14 22:01:54', '2026-01-14 22:01:54', 'US');

-- --------------------------------------------------------

--
-- Table structure for table `help_categories`
--

CREATE TABLE `help_categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(100) DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT 'GLOBAL'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `help_categories`
--

INSERT INTO `help_categories` (`id`, `name`, `slug`, `icon`, `description`, `order_index`, `is_active`, `country_code`) VALUES
(1, 'Getting Started', 'getting-started', NULL, 'Help articles about Getting Started', 0, 1, 'GLOBAL'),
(2, 'Education', 'education', NULL, 'Help articles about Education', 1, 1, 'GLOBAL'),
(3, 'Features', 'features', NULL, 'Help articles about Features', 2, 1, 'GLOBAL'),
(4, 'Security', 'security', NULL, 'Help articles about Security', 3, 1, 'GLOBAL');

-- --------------------------------------------------------

--
-- Table structure for table `instructors`
--

CREATE TABLE `instructors` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `avatar_url` text DEFAULT NULL,
  `expertise` text DEFAULT NULL,
  `rating` decimal(2,1) DEFAULT NULL,
  `students_taught` int(11) DEFAULT NULL,
  `courses_count` int(11) DEFAULT NULL,
  `social_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`social_links`)),
  `is_active` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `instructors`
--

INSERT INTO `instructors` (`id`, `name`, `title`, `bio`, `avatar_url`, `expertise`, `rating`, `students_taught`, `courses_count`, `social_links`, `is_active`, `country_code`, `created_at`) VALUES
(1, 'Dr. Sarah Chen', 'Investment Strategist', 'Former Goldman Sachs portfolio manager with 15+ years of experience in equity research and portfolio management.', NULL, 'Stocks, ETFs, Portfolio Management', 4.8, 1424, 8, NULL, 1, 'GLOBAL', '2026-01-09 11:29:35'),
(2, 'Michael Rodriguez', 'Trading Expert', 'Professional day trader and technical analyst. Has trained over 5,000 students worldwide.', NULL, 'Technical Analysis, Day Trading', 4.5, 728, 3, NULL, 1, 'GLOBAL', '2026-01-09 11:29:35'),
(3, 'Emma Thompson', 'Crypto Educator', 'Early Bitcoin adopter and blockchain consultant. Former lead at Coinbase education team.', NULL, 'Cryptocurrency, DeFi, Blockchain', 5.0, 1428, 5, NULL, 1, 'GLOBAL', '2026-01-09 11:29:35'),
(4, 'James Wilson', 'Financial Planner', 'Certified Financial Planner (CFP) with expertise in retirement planning and wealth management.', NULL, 'Personal Finance, Retirement', 4.7, 2936, 2, NULL, 1, 'GLOBAL', '2026-01-09 11:29:35');

-- --------------------------------------------------------

--
-- Table structure for table `jobs`
--

CREATE TABLE `jobs` (
  `id` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `scheduled_at` datetime DEFAULT NULL,
  `executed_at` datetime DEFAULT NULL,
  `result` text DEFAULT NULL,
  `error` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `job_listings`
--

CREATE TABLE `job_listings` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `department` varchar(100) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `type` enum('full-time','part-time','contract','internship') DEFAULT NULL,
  `description` text DEFAULT NULL,
  `requirements` text DEFAULT NULL,
  `salary_range` varchar(100) DEFAULT NULL,
  `is_remote` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `expires_at` date DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `login_events`
--

CREATE TABLE `login_events` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `event_type` varchar(50) DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `success` tinyint(1) DEFAULT NULL,
  `failure_reason` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `marketing_campaigns`
--

CREATE TABLE `marketing_campaigns` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  `status` enum('draft','active','paused','completed') DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `budget` decimal(10,2) DEFAULT NULL,
  `target_audience` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`target_audience`)),
  `metrics` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`metrics`)),
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `market_cache`
--

CREATE TABLE `market_cache` (
  `id` varchar(255) NOT NULL,
  `cache_key` varchar(255) NOT NULL,
  `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`data`)),
  `expires_at` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `market_data`
--

CREATE TABLE `market_data` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `price` decimal(18,6) DEFAULT NULL,
  `change` decimal(18,6) DEFAULT NULL,
  `change_percent` decimal(10,4) DEFAULT NULL,
  `volume` bigint(20) DEFAULT NULL,
  `market_cap` bigint(20) DEFAULT NULL,
  `pe_ratio` decimal(10,4) DEFAULT NULL,
  `52_week_high` decimal(18,6) DEFAULT NULL,
  `52_week_low` decimal(18,6) DEFAULT NULL,
  `currency` varchar(3) DEFAULT NULL,
  `exchange` varchar(50) DEFAULT NULL,
  `asset_type` enum('stock','crypto','forex','commodity','index') DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `sector` varchar(100) DEFAULT NULL,
  `industry` varchar(100) DEFAULT NULL,
  `open_price` decimal(18,6) DEFAULT NULL,
  `previous_close` decimal(18,6) DEFAULT NULL,
  `day_high` decimal(18,6) DEFAULT NULL,
  `day_low` decimal(18,6) DEFAULT NULL,
  `avg_volume` bigint(20) DEFAULT NULL,
  `beta` decimal(10,4) DEFAULT NULL,
  `forward_pe` decimal(10,4) DEFAULT NULL,
  `trailing_pe` decimal(10,4) DEFAULT NULL,
  `eps` decimal(18,6) DEFAULT NULL,
  `dividend_yield` decimal(10,4) DEFAULT NULL,
  `dividend_rate` decimal(18,6) DEFAULT NULL,
  `book_value` decimal(18,6) DEFAULT NULL,
  `price_to_book` decimal(10,4) DEFAULT NULL,
  `shares_outstanding` bigint(20) DEFAULT NULL,
  `float_shares` bigint(20) DEFAULT NULL,
  `short_ratio` decimal(10,4) DEFAULT NULL,
  `logo_url` varchar(500) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `market_data`
--

INSERT INTO `market_data` (`id`, `symbol`, `name`, `price`, `change`, `change_percent`, `volume`, `market_cap`, `pe_ratio`, `52_week_high`, `52_week_low`, `currency`, `exchange`, `asset_type`, `last_updated`, `country_code`, `sector`, `industry`, `open_price`, `previous_close`, `day_high`, `day_low`, `avg_volume`, `beta`, `forward_pe`, `trailing_pe`, `eps`, `dividend_yield`, `dividend_rate`, `book_value`, `price_to_book`, `shares_outstanding`, `float_shares`, `short_ratio`, `logo_url`, `website`, `description`) VALUES
(1, 'AAPL', 'Apple Inc.', 258.210000, -1.800020, -0.6923, 34022938, 3815401848832, 34.6126, 288.620000, 169.210000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:29', 'US', 'Technology', 'Consumer Electronics', 258.720000, 260.010000, 261.030000, 257.050000, 45960616, 1.0930, 28.2158, 34.6126, 7.460000, 0.4000, 1.040000, 4.991000, 51.7351, 14697926000, 14750346619, 2.6800, NULL, 'https://www.apple.com', 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; and wearables, home, and accessories comprising AirPods, Apple Vision Pro, Apple TV, Apple Watch, Beats products, and HomePod, as well as Apple branded and third-party accessories. It also provides AppleCare support and cloud services; and operates various platforms, including the App Store that allow customers to discover and download applications and digital content, such as books, music, video, games, and podcasts, as well as advertising services include third-party licensing arrangements and its own advertising platforms. In addition, the company offers various subscription-based services, such as Apple Arcade, a game subscription service; Apple Fitness+, a personalized fitness service; Apple Music, which offers users a curated listening experience with on-demand radio stations; Apple News+, a subscription news and magazine service; Apple TV, which offers exclusive original content and live sports; Apple Card, a co-branded credit card; and Apple Pay, a cashless payment service, as well as licenses its intellectual property. The company serves consumers, and small and mid-sized businesses; and the education, enterprise, and government markets. It distributes third-party applications for its products through the App Store. The company also sells its products through its retail and online stores, and direct sales force; and third-party cellular network carriers and resellers. The company was formerly known as Apple Computer, Inc. and changed its name to Apple Inc. in January 2007. Apple Inc. was founded in 1976 and is headquartered in Cupertino, California.'),
(2, 'GOOGL', 'Alphabet Inc.', 332.780000, -3.113010, -0.9268, 28167935, 4030671880192, 32.8834, 340.490000, 140.530000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:30', 'US', 'Communication Services', 'Internet Content & Information', 337.510000, 335.893000, 337.690000, 330.740000, 36421372, 1.0860, 29.5450, 32.8834, 10.120000, 0.2500, 0.840000, 32.033000, 10.3887, 5818000000, 10798396290, 2.6800, NULL, 'https://abc.xyz', 'Alphabet Inc. offers various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America. It operates through Google Services, Google Cloud, and Other Bets segments. The Google Services segment provides products and services, including ads, Android, Chrome, devices, Gmail, Google Drive, Google Maps, Google Photos, Google Play, Search, and YouTube. It is also involved in the sale of apps and in-app purchases and digital content in the Google Play and YouTube; and devices, as well as the provision of YouTube consumer subscription services, such as YouTube TV, YouTube Music and Premium, NFL Sunday Ticket, and Google One. The Google Cloud segment provides consumption-based fees and subscriptions for AI solutions, including AI infrastructure, Vertex AI platform, and Gemini for Google Cloud. It also provides cybersecurity, and data and analytics services; Google Workspace that include cloud-based communication and collaboration tools for enterprises, such as Calendar, Gmail, Docs, Drive, and Meet; and other services for enterprise customers. The Other Bets segment sells healthcare-related and internet services. Alphabet Inc. was incorporated in 1998 and is headquartered in Mountain View, California.'),
(3, 'MSFT', 'Microsoft Corporation', 456.660000, -2.720000, -0.5921, 23015084, 3394429779968, 32.4794, 555.450000, 344.790000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:30', 'US', 'Technology', 'Software - Infrastructure', 466.345000, 459.380000, 464.120000, 455.910000, 23783257, 1.0730, 24.3583, 32.4794, 14.060000, 0.7900, 3.640000, 48.840000, 9.3501, 7432377655, 7421452060, 2.3500, NULL, 'https://www.microsoft.com', 'Microsoft Corporation develops and supports software, services, devices, and solutions worldwide. The company\'s Productivity and Business Processes segment offers Microsoft 365 Commercial, Enterprise Mobility + Security, Windows Commercial, Power BI, Exchange, SharePoint, Microsoft Teams, Security and Compliance, and Copilot; Microsoft 365 Commercial products, such as Windows Commercial on-premises and Office licensed services; Microsoft 365 Consumer products and cloud services, such as Microsoft 365 Consumer subscriptions, Office licensed on-premises, and other consumer services; LinkedIn; Dynamics products and cloud services, such as Dynamics 365, cloud-based applications, and on-premises ERP and CRM applications. Its Intelligent Cloud segment provides Server products and cloud services, such as Azure and other cloud services, GitHub, Nuance Healthcare, virtual desktop offerings, and other cloud services; Server products, including SQL and Windows Server, Visual Studio and System Center related Client Access Licenses, and other on-premises offerings; Enterprise and partner services, including Enterprise Support and Nuance professional Services, Industry Solutions, Microsoft Partner Network, and Learning Experience. The company\'s Personal Computing segment provides Windows and Devices, such as Windows OEM licensing and Devices and Surface and PC accessories; Gaming services and solutions, such as Xbox hardware, content, and services, first- and third-party content Xbox Game Pass, subscriptions, and Cloud Gaming, advertising, and other cloud services; search and news advertising services, such as Bing and Copilot, Microsoft News and Edge, and third-party affiliates. It sells its products through OEMs, distributors, and resellers; and online and retail stores. The company was founded in 1975 and is headquartered in Redmond, Washington.'),
(4, 'META', 'Meta Platforms, Inc.', 620.800000, 5.279970, 0.8578, 12938724, 1564743565312, 27.4690, 796.250000, 479.800000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:30', 'US', 'Communication Services', 'Internet Content & Information', 626.400000, 615.520000, 624.170000, 614.230000, 18452370, 1.2870, 20.4350, 27.4690, 22.600000, 0.3400, 2.100000, 76.980000, 8.0644, 2177889269, 2173350126, 2.1700, NULL, 'https://investor.atmeta.com', 'Meta Platforms, Inc. engages in the development of products that enable people to connect and share with friends and family through mobile devices, personal computers, virtual reality and mixed reality headsets, augmented reality, and wearables worldwide. It operates through two segments, Family of Apps (FoA) and Reality Labs (RL). The FoA segment offers Facebook, which enables people to build community through feed, reels, stories, groups, marketplace, and other; Instagram that brings people closer through instagram feed, stories, reels, live, and messaging; Messenger, a messaging application for people to connect with friends, family, communities, and businesses across platforms and devices through text, audio, and video calls; Threads, an application for text-based updates and public conversations; and WhatsApp, a messaging application that is used by people and businesses to communicate and transact in a private way. The RL segment provides virtual, augmented, and mixed reality related products comprising consumer hardware, software, and content that help people feel connected, anytime, and anywhere. The company was formerly known as Facebook, Inc. and changed its name to Meta Platforms, Inc. in October 2021. The company was incorporated in 2004 and is headquartered in Menlo Park, California.'),
(5, 'NVDA', 'NVIDIA Corporation', 187.050000, 3.910000, 2.1350, 202434730, 4554106601472, 46.1852, 212.190000, 86.620000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:31', 'US', 'Technology', 'Semiconductors', 186.490000, 183.140000, 189.700000, 186.330000, 183004118, 2.3140, 24.6193, 46.1852, 4.050000, 0.0200, 0.040000, 4.892000, 38.2359, 24305000000, 23330430000, 1.5600, NULL, 'https://www.nvidia.com', 'NVIDIA Corporation, a computing infrastructure company, provides graphics and compute and networking solutions in the United States, Singapore, Taiwan, China, Hong Kong, and internationally. The Compute & Networking segment includes its Data Centre accelerated computing platforms and artificial intelligence solutions and software; networking; automotive platforms and autonomous and electric vehicle solutions; Jetson for robotics and other embedded platforms; and DGX Cloud computing services. The Graphics segment offers GeForce GPUs for gaming and PCs, the GeForce NOW game streaming service and related infrastructure, and solutions for gaming platforms; Quadro/NVIDIA RTX GPUs for enterprise workstation graphics; virtual GPU or vGPU software for cloud-based visual and virtual computing; automotive platforms for infotainment systems; and Omniverse software for building and operating industrial AI and digital twin applications. It also customized agentic solutions designed in collaboration with NVIDIA to accelerate enterprise AI adoption. The company\'s products are used in gaming, professional visualization, data center, and automotive markets. It sells its products to original equipment manufacturers, original device manufacturers, system integrators and distributors, independent software vendors, cloud service providers, consumer internet companies, add-in board manufacturers, distributors, automotive manufacturers and tier-1 automotive suppliers, and other ecosystem participants. The company has a strategic partnership with Siemens Aktiengesellschaft to develop industrial and physical AI solutions for AI-driven innovation to every industry and industrial workflow. NVIDIA Corporation was incorporated in 1993 and is headquartered in Santa Clara, California.'),
(6, 'TSLA', 'Tesla, Inc.', 438.570000, -0.574982, -0.1309, 47845404, 1458604474368, 302.4621, 498.830000, 214.250000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:31', 'US', 'Consumer Cyclical', 'Auto Manufacturers', 442.430000, 439.145000, 445.360000, 437.650000, 78464300, 1.8350, 201.7759, 302.4621, 1.450000, NULL, NULL, 24.058000, 18.2297, 3325819167, 2386009187, 0.9100, NULL, 'https://www.tesla.com', 'Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally. The company operates in two segments, Automotive; and Energy Generation and Storage. The Automotive segment offers electric vehicles, as well as sells automotive regulatory credits; and non-warranty after-sales vehicle, used vehicles, body shop and parts, supercharging, retail merchandise, and vehicle insurance services. This segment also provides sedans and sport utility vehicles through direct and used vehicle sales, a network of Tesla Superchargers, and in-app upgrades; purchase financing and leasing services; services for electric vehicles through its company-owned service locations and Tesla mobile service technicians; and vehicle limited warranties and extended service plans. The Energy Generation and Storage segment engages in the design, manufacture, installation, sale, and leasing of solar energy generation and energy storage products, and related services to residential, commercial, and industrial customers and utilities through its website, stores, and galleries, as well as through a network of channel partners. This segment also provides services and repairs to its energy product customers, including under warranty; and various financing options to its residential customers. The company was formerly known as Tesla Motors, Inc. and changed its name to Tesla, Inc. in February 2017. Tesla, Inc. was incorporated in 2003 and is headquartered in Austin, Texas.'),
(7, 'AMZN', 'Amazon.com, Inc.', 238.180000, 1.469990, 0.6210, 42759679, 2546195496960, 33.6888, 258.600000, 161.380000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:31', 'US', 'Consumer Cyclical', 'Internet Retail', 239.280000, 236.710000, 240.650000, 236.630000, 44803913, 1.3760, 30.2987, 33.6888, 7.070000, NULL, NULL, 34.587000, 6.8864, 10690216011, 9701905541, 2.0500, NULL, 'https://www.amazon.com', 'Amazon.com, Inc. engages in the retail sale of consumer products, advertising, and subscriptions service through online and physical stores in North America and internationally. The company operates through three segments: North America, International, and Amazon Web Services (AWS). It also manufactures and sells electronic devices, including Kindle, fire tablets, fire TVs, echo, ring, blink, and eero; and develops and produces media content. In addition, the company offers programs that enable sellers to sell their products in its stores; and programs that allow authors, independent publishers, musicians, filmmakers, Twitch streamers, skill and app developers, and others to publish and sell content. Further, it provides compute, storage, database, analytics, machine learning, and other services, as well as advertising services through programs, such as sponsored ads, display, and video advertising. Additionally, the company offers Amazon Prime, a membership program. The company\'s products offered through its stores include merchandise and content purchased for resale and products offered by third-party sellers. It also provides AgentCore services, such as AgentCore Runtime, AgentCore Memory, AgentCore Observability, AgentCore Identity, AgentCore Gateway, AgentCore Browser, and AgentCore Code Interpreter. It serves consumers, sellers, developers, enterprises, content creators, advertisers, and employees. Amazon.com, Inc. was incorporated in 1994 and is headquartered in Seattle, Washington.'),
(8, 'NFLX', 'Netflix, Inc.', 88.050000, -0.479996, -0.5422, 36719496, 373096316928, 36.8410, 134.115000, 82.110000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:32', 'US', 'Communication Services', 'Entertainment', 89.010000, 88.530000, 89.890000, 87.820000, 45529675, 1.7110, 27.1927, 36.8410, 2.390000, NULL, NULL, 6.125000, 14.3755, 4237323340, 4209950231, 1.4600, NULL, 'https://www.netflix.com', 'Netflix, Inc. provides entertainment services. The company offers television (TV) series, documentaries, feature films, and games across various genres and languages. It also provides members the ability to receive streaming content through a host of internet-connected devices, including TVs, digital video players, TV set-top boxes, and mobile devices. The company operates approximately in 190 countries. Netflix, Inc. was incorporated in 1997 and is headquartered in Los Gatos, California.'),
(9, 'JPM', 'JP Morgan Chase & Co.', 309.260000, 1.390010, 0.4515, 14644238, 841886859264, 15.4553, 337.250000, 202.160000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:32', 'US', 'Financial Services', 'Banks - Diversified', 308.470000, 307.870000, 312.940000, 307.750000, 9091747, 1.0660, 13.3880, 15.4553, 20.010000, 1.9400, 6.000000, 126.991000, 2.4353, 2696200000, 2682044950, 2.4200, NULL, 'https://www.jpmorganchase.com', 'JPMorgan Chase & Co. operates as a financial services company worldwide. It operates through three segments: Consumer & Community Banking, Commercial & Investment Bank, and Asset & Wealth Management. The company offers deposit, investment and lending products, cash management, and payments and services; mortgage origination and servicing activities; residential mortgages and home equity loans; and credit cards, auto loans, leases, and travel services to consumers and small businesses through bank branches, ATMs, and digital and telephone banking. It also provides investment banking products and services, including corporate strategy and structure advisory, and equity and debt market capital-raising services, as well as loan origination and syndication; payments; and cash and derivative instruments, risk management solutions, prime brokerage, and research, as well as offers securities services, including custody, fund services, liquidity, and trading services, and data solutions products. In addition, the company provides financial solutions, including lending, payments, investment banking, and asset management to small and midsized companies, local governments, nonprofit clients, and municipalities, as well as commercial real estate clients. Further, it offers multi-asset investment management solutions in equities, fixed income, alternatives, and money market funds to institutional clients and retail investors; and retirement products and services, brokerage, custody, estate planning, lending, deposits, and investment management products to high net worth clients. The company was founded in 1799 and is headquartered in New York, New York.'),
(10, 'BAC', 'Bank of America Corporation', 52.590000, 0.110001, 0.2096, 50903555, 384038240256, 13.8032, 57.550000, 33.070000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:32', 'US', 'Financial Services', 'Banks - Diversified', 52.720000, 52.480000, 53.036500, 52.229700, 36972186, 1.2950, 10.6642, 13.8032, 3.810000, 2.0500, 1.120000, 37.951000, 1.3857, 7212464345, 7276425641, 2.4900, NULL, 'https://www.bankofamerica.com', 'Bank of America Corporation, through its subsidiaries, provides various financial products and services for individual consumers, small and middle-market businesses, institutional investors, large corporations, and governments worldwide. The company operates through four segments: Consumer Banking, Global Wealth & Investment Management (GWIM), Global Banking, and Global Markets. The Consumer Banking segment offers traditional and money market savings accounts, certificates of deposit and IRAs, checking accounts, and investment accounts and products; credit and debit cards; residential mortgages and home equity loans; and direct and indirect loans, such as automotive, recreational vehicle, and consumer personal loans. The GWIM segment provides investment management, brokerage, banking, and trust and retirement products and services; wealth management solutions; and customized solutions, including specialty asset management services. The Global Banking segment offers lending products and services, including commercial loans, leases, commitment facilities, trade finance, and commercial real estate and asset-based lending; treasury solutions, such as treasury management, foreign exchange, short-term investing options, and merchant services; working capital management solutions; debt and equity underwriting and distribution, and merger-related and other advisory services; and fixed-income and equity research services. The Global Markets segment provides market-making, financing, securities clearing, settlement, and custody services; securities and derivative products; and risk management products using interest rate, equity, credit, currency and commodity derivatives, foreign exchange, fixed-income, and mortgage-related products. Bank of America Corporation was founded in 1784 and is based in Charlotte, North Carolina.'),
(11, 'GS', 'Goldman Sachs Group, Inc. (The)', 975.860000, 43.190000, 4.6308, 3765941, 295413383168, 19.8426, 981.259900, 439.380000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:33', 'US', 'Financial Services', 'Capital Markets', 924.900000, 932.670000, 981.259900, 927.000000, 2052763, 1.3220, 15.3926, 19.8426, 49.180000, 1.7200, 16.000000, 348.019000, 2.8040, 299928511, 311916185, 3.3900, NULL, 'https://www.goldmansachs.com', 'The Goldman Sachs Group, Inc., a financial institution, provides a range of financial services for corporations, financial institutions, governments, and individuals in the Americas, Europe, the Middle East, Africa, and Asia. It operates through Global Banking & Markets, Asset & Wealth Management, and Platform Solutions segments. The Global Banking & Markets segment provides financial advisory services, including strategic advisory assignments related to mergers and acquisitions, divestitures, corporate defense activities, restructurings, and spin-offs; equity and debt underwriting of public offerings and private placements; relationship lending and acquisition financing; secured lending through structured credit and asset-backed lending, such as warehouse, residential and commercial mortgage, corporate, consumer, auto, and student loans; financing through securities purchased under agreements to resell; and commodity financing through structured transactions. This segment also offers client execution activities for cash and derivative instruments; credit and interest rate products; and provision of mortgages, currencies, commodities, and equities related products. Its Asset & Wealth Management segment manages assets across various classes, including equity, fixed income, hedge funds, credit funds, private equity, real estate, currencies, commodities, and asset allocation strategies; and provides customized investment advisory solutions, wealth advisory services, personalized financial planning, and private banking services, as well as invests in corporate equity, credit, real estate, and infrastructure assets. The Platform Solutions segment offers credit cards; and transaction banking and other services, such as deposit-taking, payment solutions, and other cash management services for corporate and institutional clients. The Goldman Sachs Group, Inc. was founded in 1869 and is headquartered in New York, New York.'),
(12, 'V', 'Visa Inc.', 327.750000, -1.420010, -0.4314, 8430874, 632523784192, 32.1639, 375.510000, 299.000000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:33', 'US', 'Financial Services', 'Credit Services', 329.330000, 329.170000, 331.690000, 326.370000, 6652457, 0.8150, 22.7212, 32.1639, 10.190000, 0.8200, 2.680000, 19.382000, 16.9100, 1685772208, 1747461684, 3.6700, NULL, 'https://www.visa.com', 'Visa Inc. operates as a payment technology company in the United States and internationally. The company operates VisaNet, a transaction processing network that enables authorization, clearing, and settlement of payment transactions. It also offers credit, debit, and prepaid card products; tap to pay, tokenization, and click to pay services; Visa Direct, a platform which facilitates money movement, enabling clients to collect, hold, convert, and send funds across its network; and issuing solutions, such as airport lounge access, dining reservations, shopping experiences, event tickets, and seller offers. In addition, the company provides acceptance solutions, an omnichannel payment integration with e-commerce platforms; risk detection and prevention solutions; and advisory and other services comprising consulting practice, proprietary analytics models, data scientists and economists, marketing services, and managed services. It provides its services under the Visa, Visa Electron, V PAY, Interlink, and PLUS brands. The company serves consumers, sellers, financial institutions, and government entities. Visa Inc. was founded in 1958 and is headquartered in San Francisco, California.'),
(13, 'MA', 'Mastercard Incorporated', 542.650000, -4.169980, -0.7626, 3945888, 490562060288, 34.7185, 601.770000, 465.590000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:33', 'US', 'Financial Services', 'Credit Services', 548.520000, 546.820000, 549.840000, 538.995000, 2878704, 0.8570, 28.3876, 34.7185, 15.630000, 0.6400, 3.480000, 8.781000, 61.7982, 891258183, 890111444, 2.5500, NULL, 'https://www.mastercard.com', 'Mastercard Incorporated, a technology company, provides transaction processing and other payment-related products and services in the United States and internationally. The company offers integrated products and value-added services for account holders, merchants, financial institutions, digital partners, businesses, governments, and other organizations, such as programs that enable issuers to provide consumers with credits to defer payments; payment products and solutions that allow its customers to access funds in deposit and other accounts; prepaid programs services; consumer bill payment services; and commercial credit, debit, and prepaid payment products and solutions. It also provides solutions that enable businesses or governments to make payments to businesses, including Virtual Card Number, which is generated dynamically from a physical card and leverages the credit limit of the funding account; and a platform to optimize supplier payment enablement campaigns for financial institutions. In addition, the company offers Mastercard Move, which partners with digital messaging and payment platforms to enable consumers to send money directly within applications to other consumers; and partners with central banks, fintechs and financial institutions to help governments and nonprofits, as well as enables various cross-border payment flows. Further, it provides security solutions; personalization, issuer and merchant loyalty, and marketing services; advanced analytics, business intelligence, economic and location-based insights, payments consulting, and operational insights services; processing and gateway solutions; and open banking services. The company offers payment solutions and services under the MasterCard, Maestro, and Cirrus names. Mastercard Incorporated was founded in 1966 and is headquartered in Purchase, New York.'),
(14, 'JNJ', 'Johnson & Johnson', 219.570000, 1.020000, 0.4667, 6197444, 529008951296, 21.2350, 219.750000, 141.500000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:34', 'US', 'Healthcare', 'Drug Manufacturers - General', 218.230000, 218.550000, 219.750000, 215.910600, 8464367, 0.3330, 19.0905, 21.2350, 10.340000, 2.3700, 5.200000, 32.947000, 6.6643, 2409295102, 2405488416, 2.5500, NULL, 'https://www.jnj.com', 'Johnson & Johnson, together with its subsidiaries, engages in the research and development, manufacture, and sale of various products in the healthcare field worldwide. It operates in two segments, Innovative Medicine and MedTech. The Innovative Medicine segment offers products for various therapeutic areas, such as immunology, including rheumatoid arthritis, psoriatic arthritis, inflammatory bowel disease, and psoriasis; infectious diseases comprising HIV/AIDS; neuroscience, consisting of mood disorders, neurodegenerative disorders, and schizophrenia; oncology, such as prostate cancer, hematologic malignancies, lung cancer, and bladder cancer; cardiovascular and metabolism, including thrombosis, diabetes, and macular degeneration; and pulmonary hypertension comprising pulmonary arterial hypertension through retailers, wholesalers, distributors, hospitals, and healthcare professionals for prescription use. The MedTech segment provides electrophysiology products to treat heart rhythm disorders; the heart recovery portfolio, which includes technologies to treat severe coronary artery disease requiring high-risk PCI or AMI cardiogenic shock; circulatory restoration products for the treatment of calcified coronary artery and peripheral artery diseases; and neurovascular care that treats hemorrhagic and ischemic stroke. This segment offers an orthopaedics portfolio that includes products and enabling technologies that support hips, knees, trauma, spine, sports, and other; surgery portfolios comprising advanced and general surgery technologies, as well as solutions for breast aesthetics and reconstruction; contact lenses under the ACUVUE brand; and TECNIS intraocular lenses for cataract surgery. It distributes its products to wholesalers, hospitals, and retailers, as well as physicians, nurses, hospitals, eye care professionals, and clinics. The company was founded in 1886 and is based in New Brunswick, New Jersey.'),
(15, 'PFE', 'Pfizer, Inc.', 25.890000, 0.309999, 1.2119, 55006438, 147202965504, 15.0523, 27.690000, 20.920000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:34', 'US', 'Healthcare', 'Drug Manufacturers - General', 25.550000, 25.580000, 25.890000, 25.250000, 63706195, 0.4330, 8.6792, 15.0523, 1.720000, 6.6400, 1.720000, 16.321000, 1.5863, 5685707552, 5675871278, 2.7600, NULL, 'https://www.pfizer.com', 'Pfizer Inc. discovers, develops, manufactures, markets, distributes, and sells biopharmaceutical products in the United States and internationally. The company offers medicines and vaccines in various therapeutic areas, including cardiovascular and migraine under the Eliquis, Nurtec ODT/Vydura, Zavzpret, and the Premarin family brands; infectious diseases with unmet medical needs under the Prevnar family, Abrysvo, Nimenrix, FSME/IMMUN-TicoVac, and Trumenba brands; and COVID-19 prevention and treatment, and potential future mRNA and antiviral products under the Comirnaty and Paxlovid brands. It also provides medicines and vaccines in various therapeutic areas, such as biosimilars for chronic immune and inflammatory diseases under the Xeljanz, Enbrel, Inflectra, Litfulo, Velsipity, and Cibinqo brands; amyloidosis, hemophilia, endocrine diseases, and sickle cell disease under the Vyndaqel family, Oxbryta, BeneFIX, Somavert, Ngenla, and Genotropin brands; sterile injectable and anti-infective medicines under the Sulperazon, Medrol, Zavicefta, Zithromax, Octagam, and Panzyga brands; and biologics, small molecules, immunotherapies, and biosimilars under the Ibrance, Xtandi, Padcev, Adcetris, Inlyta, Lorbrena, Bosulif, Tukysa, Braftovi, Mektovi, Orgovyx, Elrexfio, Tivdak, and Talzenna brands. In addition, the company involved in the contract manufacturing business. It serves wholesalers, retailers, hospitals, clinics, government agencies, pharmacies, individual provider offices, retail pharmacies, and integrated delivery systems. The company has collaboration agreements with Bristol-Myers Squibb Company; Astellas Pharma US, Inc.; Merck KGaA; and BioNTech SE. Pfizer Inc. has strategic collaboration with Boltz, PBC to develop and deploy state-of-the-art biomolecular AI foundation models. Pfizer Inc. was founded in 1849 and is headquartered in New York, New York.'),
(16, 'UNH', 'UnitedHealth Group Incorporated', 338.960000, 4.000000, 1.1942, 6919804, 307043041280, 17.6634, 606.360000, 234.600000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:34', 'US', 'Healthcare', 'Healthcare Plans', 335.200000, 334.960000, 339.435000, 328.060000, 7370249, 0.4250, 19.0924, 17.6634, 19.190000, 2.6100, 8.840000, 105.725000, 3.2061, 905838620, 898138992, 2.2600, NULL, 'https://www.unitedhealthgroup.com', 'UnitedHealth Group Incorporated operates as a health care company in the United States and internationally. The company operates through four segments: UnitedHealthcare, Optum Health, Optum Insight, and Optum Rx. The UnitedHealthcare segment offers consumer-oriented health benefit plans and services for national employers, public sector employers, mid-sized employers, small businesses, and individuals; health care coverage, and health and well-being services to individuals age 50 and older; Medicaid plans, children\'s health insurance and health care programs; and health care benefits products and services to state programs caring for the economically disadvantaged, medically underserved, and those without the benefit of employer-funded health care coverage. The Optum Health segment provides care delivery, care management, wellness and consumer engagement, and health financial services patients, consumers, care delivery systems, providers, employers, payers, and public-sector entities. The Optum Insight segment offers software and information products, advisory consulting arrangements, and managed services outsourcing contracts to hospital systems, physicians, health plans, governments, life sciences companies, and other organizations. The Optum Rx segment provides pharmacy care services and programs, including retail network contracting, home delivery, specialty and community health pharmacy services, infusion, and purchasing and clinical capabilities, as well as develops programs in the areas of step therapy, formulary management, drug adherence, and disease and drug therapy management. UnitedHealth Group Incorporated was founded in 1974 and is based in Eden Prairie, Minnesota.'),
(17, 'XOM', 'Exxon Mobil Corporation', 129.130000, -1.069990, -0.8218, 17375729, 550513147904, 18.7689, 131.720000, 97.800000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:35', 'US', 'Energy', 'Oil & Gas Integrated', 129.130000, 130.200000, 130.195000, 128.300000, 15615055, 0.3650, 18.3840, 18.7689, 6.880000, 3.1900, 4.120000, 61.786000, 2.0900, 4217165614, 4205737095, 2.6800, NULL, 'https://corporate.exxonmobil.com', 'Exxon Mobil Corporation engages in the exploration and production of crude oil and natural gas in the United States, Guyana, Canada, the United Kingdom, Singapore, France, and internationally. It operates through Upstream, Energy Products, Chemical Products, and Specialty Products segments. The Upstream segment explores for and produces crude oil and natural gas. The Energy Products segment offers fuels, aromatics, and catalysts, as well as licensing services. The Chemical Products segment manufactures and sells petrochemicals, including olefins, polyolefins, and intermediates. The Specialty Products segment offers performance products, including finished lubricants, basestocks, waxes, synthetics, elastomers, and resins. It also involved in the manufacture, trading, transportation, and sale of crude oil, natural gas, petroleum products, petrochemicals, and other specialty products; and pursuit of lower-emission and business opportunities, including carbon capture and storage, hydrogen, lower-emission fuels, Proxxima systems, carbon materials, and lithium. In addition, the company offers sustainable aviation fuel. It sells its products under the Exxon, Esso, and Mobil brands. Exxon Mobil Corporation was founded in 1870 and is headquartered in Spring, Texas.'),
(18, 'CVX', 'Chevron Corporation', 166.160000, -1.080000, -0.6458, 8078389, 334782889984, 23.3699, 169.370000, 132.040000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:35', 'US', 'Energy', 'Oil & Gas Integrated', 165.770000, 167.240000, 167.324400, 165.100000, 9179301, 0.6870, 22.5163, 23.3699, 7.110000, 4.1200, 6.840000, 94.284000, 1.7623, 1999353597, 1880307008, 2.1900, NULL, 'https://www.chevron.com', 'Chevron Corporation, through its subsidiaries, engages in the integrated energy and chemicals operations in the United States and internationally. The company operates in two segments, Upstream and Downstream. The Upstream segment engages in the exploration, development, production, and transportation of crude oil and natural gas; liquefaction, transportation, and regasification of liquefied natural gas; transporting crude oil through pipelines; processing, transporting, storage, and marketing of natural gas; and carbon capture and storage, as well as a gas-to-liquids plant. The Downstream segment refines crude oil into petroleum products; markets crude oil, refined products, and lubricants; manufactures and markets renewable fuels; transports crude oil and refined products through pipeline, marine vessel, motor equipment, and rail car; and manufactures and markets commodity petrochemicals, plastics for industrial uses, and fuel and lubricant additives. The company was formerly known as ChevronTexaco Corporation and changed its name to Chevron Corporation in 2005. Chevron Corporation was founded in 1879 and is headquartered in Houston, Texas.'),
(19, 'WMT', 'Walmart Inc.', 119.200000, -0.840004, -0.6998, 34400307, 950363815936, 41.6783, 121.240000, 79.810000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:35', 'US', 'Consumer Defensive', 'Discount Stores', 119.950000, 120.040000, 120.870000, 118.730000, 19934039, 0.6610, 40.1290, 41.6783, 2.860000, 0.7900, 0.940000, 12.054000, 9.8888, 7970166964, 4367252988, 2.7500, NULL, 'https://corporate.walmart.com', 'Walmart Inc. engages in the operation of retail and wholesale stores and clubs, eCommerce websites, and mobile applications worldwide. The company operates through three segments: Walmart U.S., Walmart International, and Sam\'s Club. It operates supercenters, supermarkets, warehouse clubs, cash and carry stores, and discount stores under Walmart and Walmart Neighborhood Market brands; membership-only warehouse clubs; and ecommerce websites, such as walmart.com.mx, walmart.ca, flipkart.com, PhonePe and other sites. The company also offers grocery items, including dry grocery, snacks, dairy, meat, produce, deli and bakery, frozen foods, alcoholic and nonalcoholic beverages, as well as consumables, such as health and beauty aids, pet supplies, household chemicals, paper goods, and baby products; and fuel and other categories. In addition, it is involved in the provision of health and wellness products covering pharmacy, optical and hearing services, over-the-counter drugs, and protein and nutrition products; and home, hardlines, and seasonal items, including home improvement, outdoor living, gardening, furniture, apparel, jewelry, tools and power equipment, housewares, toys, and mattresses. Further, the company offers consumer electronics and accessories, software, video games, office supplies, appliances, and third-party gift cards. Additionally, it operates digital payment platforms; offers financial services and related products, including money transfers, bill payments, money orders, check cashing, prepaid access, co-branded credit cards, installment lending, and earned wage access; and markets lines of merchandise under private and licensed brands. The company was formerly known as Wal-Mart Stores, Inc. and changed its name to Walmart Inc. in February 2018. Walmart Inc. was founded in 1945 and is based in Bentonville, Arkansas.'),
(20, 'KO', 'Coca-Cola Company (The)', 70.480000, -0.959999, -1.3438, 12288232, 303322464256, 23.3378, 74.380000, 61.370000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:36', 'US', 'Consumer Defensive', 'Beverages - Non-Alcoholic', 71.590000, 71.440000, 71.600000, 70.365000, 16737316, 0.3870, 21.8889, 23.3378, 3.020000, 2.8900, 2.040000, 7.263000, 9.7040, 4301608845, 3872781459, 2.2700, NULL, 'https://www.coca-colacompany.com', 'The Coca-Cola Company, a beverage company, manufactures and sells various nonalcoholic beverages in the United States and internationally. The company provides sparkling soft drinks and flavors; water, sports, coffee, and tea; juice, value-added dairy, and plant-based beverages; and other beverages. It also offers beverage concentrates and syrups, as well as fountain syrups to fountain retailers comprising restaurants and convenience stores. The company sells its products under the Coca-Cola, Diet Coke/Coca-Cola Light, Coca-Cola Zero Sugar, caffeine free Diet Coke, Cherry Coke, Fanta Orange, Fanta Zero Orange, Fanta Zero Sugar, Fanta Apple, Sprite, Sprite Zero Sugar, Simply Orange, Simply Apple, Simply Grapefruit, Fresca, Schweppes, Thums Up, Aquarius, Ayataka, BODYARMOR, Ciel, Costa, Crystal, Dasani, dogadan, Fuze Tea, Georgia, glacéau smartwater, glacéau vitaminwater, Gold Peak, I LOHAS, Powerade, Topo Chico, Core Power, Del Valle, fairlife, innocent, Maaza, Minute Maid, Minute Maid Pulpy, and Simply brands. It operates through a network of independent bottling partners, distributors, wholesalers, and retailers, as well as through bottling and distribution operators. The company was founded in 1886 and is headquartered in Atlanta, Georgia.'),
(21, 'PEP', 'Pepsico, Inc.', 146.570000, 0.650009, 0.4455, 5707482, 200665661440, 27.8650, 160.150000, 127.600000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:36', 'US', 'Consumer Defensive', 'Beverages - Non-Alcoholic', 141.100000, 145.920000, 147.017000, 145.530000, 7413119, 0.4210, 17.1302, 27.8650, 5.260000, 3.8800, 5.690000, 14.162000, 10.3495, 1367340122, 1363771364, 2.7700, NULL, 'https://www.pepsico.com', 'PepsiCo, Inc. engages in the manufacture, marketing, distribution, and sale of various beverages and convenient foods worldwide. The company operates through seven segments: Frito-Lay North America; Quaker Foods North America; PepsiCo Beverages North America; Latin America; Europe; Africa, Middle East and South Asia; and Asia Pacific, Australia and New Zealand and China Region. It provides dips, cheese-flavored snacks, and spreads, as well as corn, potato, and tortilla chips; cereals, rice, pasta, mixes and syrups, granola bars, grits, oatmeal, rice cakes, and side dishes; beverage concentrates, fountain syrups, and finished goods; ready-to-drink tea, coffee, and juices; dairy products; and sparkling water makers and related products, as well as distributes alcoholic beverages under Hard MTN Dew brand. The company offers its products primarily under the Lay\'s, Doritos, Fritos, Tostitos, BaiCaoWei, Cheetos, Cap\'n Crunch, Life, Pearl Milling Company, Gatorade, Pepsi-Cola, Mountain Dew, Quaker, Rice-A-Roni, Aquafina, Bubly, Emperador, Diet Mountain Dew, Diet Pepsi, Gatorade Zero, Crush, Propel, Dr Pepper, Schweppes, Marias Gamesa, Ruffles, Sabritas, Saladitas, Tostitos, 7UP, Diet 7UP, H2oh!, Manzanita Sol, Mirinda, Pepsi Black, Pepsi Max, San Carlos, Toddy, Walkers, Chipsy, Kurkure, Sasko, Spekko, White Star, Smith\'s, Sting, SodaStream, Lubimyj Sad, Agusha, Chudo, Domik v Derevne, Lipton, and other brands. It serves wholesale and other distributors, foodservice customers, grocery stores, drug stores, convenience stores, discount/dollar stores, mass merchandisers, membership stores, hard discounters, e-commerce retailers and authorized independent bottlers, and others through a network of direct-store-delivery, customer warehouse, and distributor networks, as well as directly to consumers through e-commerce platforms and retailers. The company was founded in 1898 and is based in Purchase, New York.'),
(22, 'MCD', 'McDonald\'s Corporation', 308.620000, 0.489990, 0.1590, 2216766, 220232597504, 26.3103, 326.320000, 278.730000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:36', 'US', 'Consumer Cyclical', 'Restaurants', 308.930000, 308.130000, 308.930000, 303.800000, 3183770, 0.5310, 23.3012, 26.3103, 11.730000, 2.4100, 7.440000, -3.037000, -101.6200, 712154350, 711057632, 2.5100, NULL, 'https://www.mcdonalds.com', 'McDonald\'s Corporation owns, operates, and franchises restaurants under the McDonald\'s brand in the United States and internationally. It offers food and beverages, including hamburgers and cheeseburgers, various chicken sandwiches, fries, shakes, desserts, sundaes, soft serve cones, cookies, pies, soft drinks, coffee, and other beverages; and full or limited breakfast, as well as sells various other products during limited-time promotions. The company owns and operates franchised restaurants under various structures, including conventional franchise, developmental license, or affiliate. McDonald\'s Corporation was founded in 1940 and is based in Chicago, Illinois.'),
(23, 'BA', 'Boeing Company (The)', 247.740000, 5.130000, 2.1145, 6505888, 193998077952, NULL, 248.749700, 128.880000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:36', 'US', 'Industrials', 'Aerospace & Defense', 244.380000, 242.610000, 248.749700, 243.965700, 8439175, 1.1630, 109.7297, NULL, -13.700000, NULL, NULL, -10.868000, -22.7954, 783071257, 728270271, 1.8900, NULL, 'https://www.boeing.com', 'The Boeing Company, together with its subsidiaries, designs, develops, manufactures, sells, services, and supports commercial jetliners, military aircraft, satellites, missile defense, human space flight and launch systems, and services worldwide. The company operates through three segments: Commercial Airplanes; Defense, Space & Security; and Global Services. The Commercial Airplanes segment develops, produces, and markets commercial jet aircraft for passenger and cargo requirements. The Defense, Space & Security segment engages in the research, development, production, and modification of manned and unmanned military aircraft and weapons systems; strategic defense and intelligence systems, which include strategic missile and defense systems, command, control, communications, computers, intelligence, surveillance and reconnaissance, cyber and information solutions, and intelligence systems; and satellite systems, such as government and commercial satellites, and space exploration. The Global Services segment offers products and services, including supply chain and logistics management, engineering, maintenance and modifications, upgrades and conversions, spare parts, pilot and maintenance training systems and services, technical and maintenance documents, and data analytics and digital services to commercial and defense customers. The Boeing Company was incorporated in 1916 and is based in Arlington, Virginia.'),
(24, 'CAT', 'Caterpillar, Inc.', 647.180000, 8.429990, 1.3198, 1710119, 303190179840, 33.2228, 652.359900, 267.300000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:37', 'US', 'Industrials', 'Farm & Heavy Construction Machinery', 644.940000, 638.750000, 652.359900, 644.160000, 2591367, 1.5680, 28.8431, 33.2228, 19.480000, 0.9500, 6.040000, 44.143000, 14.6610, 467979596, 466603736, 2.2900, NULL, 'https://www.caterpillar.com', 'Caterpillar Inc. manufactures and sells construction and mining equipment, off-highway diesel and natural gas engines, industrial gas turbines, and diesel-electric locomotives in the United States and internationally. Its Construction Industries segment offers asphalt pavers, cold planers, compactors, forestry machines, material handlers, motor graders, pipelayers, road reclaimers, telehandlers, track-type tractors, and track and wheel excavators; compact track, wheel, track-type, backhoe, and skid steer loaders; and related parts and tools. The company\'s Resource Industries segment provides electric rope and hydraulic shovels, draglines, rotary drills, hard rock vehicles, tractors, mining trucks, wheel loaders, off-highway and articulated trucks, wide-body trucks, wheel tractor scrapers and dozers, fleet management products, landfill and soil compactors, machinery components, autonomous ready vehicles and solutions, work tools, and safety services and mining performance solutions, as well as related parts and services. Its Energy & Transportation segment offers reciprocating engine powered generator sets; reciprocating engines, drivetrain, and integrated systems and solutions; turbines, centrifugal gas compressors, and related services; and diesel-electric locomotives and components, and other rail-related products. The company\'s Financial Products segment provides operating and finance leases, installment sale contracts, revolving charge accounts, repair/rebuild financing services, working capital loans, and wholesale financing; and insurance and risk management products and services. Its All Other segment offers wear and maintenance components; parts distribution; logistics solutions and distribution services; dealer portfolio management, and brand management and marketing strategy services; and digital investment services. Caterpillar Inc. was founded in 1925 and is headquartered in Irving, Texas.');
INSERT INTO `market_data` (`id`, `symbol`, `name`, `price`, `change`, `change_percent`, `volume`, `market_cap`, `pe_ratio`, `52_week_high`, `52_week_low`, `currency`, `exchange`, `asset_type`, `last_updated`, `country_code`, `sector`, `industry`, `open_price`, `previous_close`, `day_high`, `day_low`, `avg_volume`, `beta`, `forward_pe`, `trailing_pe`, `eps`, `dividend_yield`, `dividend_rate`, `book_value`, `price_to_book`, `shares_outstanding`, `float_shares`, `short_ratio`, `logo_url`, `website`, `description`) VALUES
(25, 'DIS', 'Walt Disney Company (The)', 113.410000, -0.119995, -0.1057, 7874679, 203903680512, 16.5562, 124.690000, 80.100000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:37', 'US', 'Communication Services', 'Entertainment', 113.710000, 113.530000, 114.110000, 112.170000, 10560352, 1.4420, 15.4340, 16.5562, 6.850000, 1.3200, 1.500000, 61.345000, 1.8487, 1785288846, 1782628766, 2.0400, NULL, 'https://thewaltdisneycompany.com', 'The Walt Disney Company operates as an entertainment company in Americas, Europe, and the Asia Pacific. It operates in three segments: Entertainment, Sports, and Experiences. The company produces and distributes film and television content under the ABC Television Network, Disney, Freeform, FX, Fox, National Geographic, and Star brand television channels, as well as ABC television stations and A+E television networks; and produces original content under the Disney Branded Television, FX Productions, Lucasfilm, Marvel, National Geographic Studios, Pixar, Searchlight Pictures, Twentieth Century Studios, 20th Television, and Walt Disney Pictures banners. It also provides direct-to-consumer streaming services through Disney+, Disney+ Hotstar, and Hulu; sports-related video streaming content through ESPN, ESPN on ABC, ESPN+ DTC, and Star; sale/licensing of film and episodic content to television and video-on-demand services; theatrical, home entertainment, and music distribution services; DVD and Blu-ray discs, electronic home video licenses, and VOD rental services; staging and licensing of live entertainment events; and post-production services. In addition, the company operates theme parks and resorts, such as Walt Disney World Resort, Disneyland Resort, Disneyland Paris, Hong Kong Disneyland Resort, Shanghai Disney Resort, Disney Cruise Line, Disney Vacation Club, National Geographic Expeditions, and Adventures by Disney, as well as Aulani, a Disney resort and spa in Hawaii. Further, it licenses its intellectual property (IP) to a third party that owns and operates Tokyo Disney Resort; licenses trade names, characters, visual, literary, and other IP for use on merchandise, published materials, and games; operates a direct-to-home satellite distribution platform; sells branded merchandise through retail, online, and wholesale businesses; and develops and publishes books, comic books, and magazines. The company was founded in 1923 and is based in Burbank, California.'),
(26, 'AMD', 'Advanced Micro Devices, Inc.', 227.920000, 4.319990, 1.9320, 54830061, 371063226368, 119.9579, 267.080000, 76.480000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:11', 'US', 'Technology', 'Semiconductors', 227.910000, 223.600000, 238.350000, 227.220000, 41587896, 1.9500, 34.6794, 119.9579, 1.900000, NULL, NULL, 37.340000, 6.1039, 1628041540, 1619038470, 1.3500, NULL, 'https://www.amd.com', 'Advanced Micro Devices, Inc. operates as a semiconductor company worldwide. It operates in three segments: Data Center, Client and Gaming, and Embedded. The company offers artificial intelligence (AI) accelerators, x86 microprocessors, and graphics processing units (GPUs) as standalone devices or as incorporated into accelerated processing units, chipsets, and data center and professional GPUs; and embedded processors and semi-custom system-on-chip (SoC) products, microprocessor and SoC development services and technology, data processing units, field programmable gate arrays (FPGA), system on modules, smart network interface cards, and adaptive SoC products. It provides processors under the AMD Ryzen, AMD Ryzen AI, AMD Ryzen PRO, AMD Ryzen Threadripper, AMD Ryzen Threadripper PRO, AMD Athlon, and AMD PRO A-Series brands; graphics under the AMD Radeon graphics and AMD Embedded Radeon graphics; professional graphics under the AMD Radeon Pro graphics brand; and AI and general-purpose compute infrastructure for hyperscale providers. The company offers data center graphics under the AMD Instinct accelerators and Radeon PRO V-series brands; server microprocessors under the AMD EPYC brand; low power solutions under the AMD Athlon, AMD Geode, AMD Ryzen, AMD EPYC, and AMD R-Series and G-Series brands; FPGA products under the Virtex-6, Virtex-7, Virtex UltraScale+, Kintex-7, Kintex UltraScale, Kintex UltraScale+, Artix-7, Artix UltraScale+, Spartan-6, and Spartan-7 brands; adaptive SOCs under the Zynq-7000, Zynq UltraScale+ MPSoC, Zynq UltraScale+ RFSoCs, Versal HBM, Versal Premium, Versal Prime, Versal AI Core, Versal AI Edge, Vitis, and Vivado brands; and compute and network acceleration board products under the Alveo and Pensando brands. It serves original equipment and design manufacturers, public cloud service providers, system integrators, distributors, and add-in-board manufacturers. The company was incorporated in 1969 and is headquartered in Santa Clara, California.'),
(27, 'INTC', 'Intel Corporation', 48.320000, -0.400002, -0.8210, 130670600, 230486392832, 805.3334, 50.380000, 17.670000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:11', 'US', 'Technology', 'Semiconductors', 49.360000, 48.720000, 50.380000, 47.825000, 91331870, 1.3540, 80.6745, 805.3334, 0.060000, NULL, NULL, 22.320000, 2.1649, 4770000000, 4762034100, 1.5700, NULL, 'https://www.intel.com', 'Intel Corporation designs, develops, manufactures, markets, and sells computing and related products and services worldwide. It operates through Intel Products, Intel Foundry, and All Other segments. The company offers microprocessor and chipset, stand-alone SoC, and multichip package; Computer Systems and Devices; hardware products comprising CPUs, graphics processing units (GPUs), accelerators, and field programmable gate arrays (FPGAs); and memory and storage, connectivity and networking, and other semiconductor products. It also offers silicon and software products; and optimization solutions for workloads, such as AI, cryptography, security, storage, networking, and leverages various features supporting diverse compute environments. In addition, the company provides driving assistance and self-driving solutions; advanced process technologies enabled by an ecosystem of electronic design automation tools, intellectual property, and design services, as well as systems of chips, including advanced packaging technologies, software, and system. Further, it delivers and deploys intelligent edge platforms that allow developers to achieve agility and drive automation using AI for efficient operations with data integrity, as well as provides hardware and software platforms, tools, and ecosystem partnerships for digital transformation from the cloud to edge. The company serves original equipment manufacturers, original design manufacturers, cloud service providers, and other manufacturers and service providers. Intel Corporation was incorporated in 1968 and is headquartered in Santa Clara, California.'),
(28, 'CRM', 'Salesforce, Inc.', 233.530000, -6.040010, -2.5212, 10218960, 222320558080, 31.1373, 367.090000, 221.960000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:12', 'US', 'Technology', 'Software - Application', 237.020000, 239.570000, 238.840000, 231.670000, 7691965, 1.2660, 17.8065, 31.1373, 7.500000, 0.7100, 1.660000, 63.717000, 3.6651, 937000000, 911644780, 2.0500, NULL, 'https://www.salesforce.com', 'Salesforce, Inc. provides customer relationship management technology that connects companies and customers together worldwide. The company offers Agentforce, an agentic layer of the salesforce platform; Data Cloud, a data engine; Industries AI for creating industry-specific AI agents with Agentforce; Salesforce Starter, a suite of solution for small and medium-size business; Slack, a workplace communication and productivity platform; Tableau, an end-to-end analytics solution for range of enterprise use cases and intelligent analytics with AI models, spot trends, predict outcomes, timely recommendations, and take action from any device; and integration and analytics solutions, as well as Agentforce Command Center, an observability solution to manage, track, and scale AI agent activity. It also provides marketing platform; commerce services, which empowers shopping experience across various customer touchpoint; and field service solution that enables companies to connect service agents, dispatchers, and mobile employees through one centralized platform to schedule and dispatch work, as well as track and manage jobs. The company has a strategic partnership with Google to integrate Agentforce 360 with Google Workspace for sales and IT service, which expands the Salesforce Gemini integration. Salesforce, Inc. was incorporated in 1999 and is headquartered in San Francisco, California.'),
(29, 'ORCL', 'Oracle Corporation', 189.850000, -3.759990, -1.9421, 14318966, 545463730176, 35.6861, 345.720000, 118.860000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:12', 'US', 'Technology', 'Software - Infrastructure', 195.010000, 193.610000, 195.000000, 189.390000, 25193488, 1.6510, 23.8712, 35.6861, 5.320000, 1.0300, 2.000000, 10.425000, 18.2110, 2873130000, 1706007131, 0.8600, NULL, 'https://www.oracle.com', 'Oracle Corporation offers products and services that address enterprise information technology environments worldwide. Its Oracle cloud software as a service offering include various cloud software applications, including Oracle Fusion cloud enterprise resource planning ERP, Oracle Fusion cloud enterprise performance management EPM, Oracle Fusion cloud supply chain and manufacturing management SCM, Oracle Fusion cloud human capital management HCM, and NetSuite applications suite, Oracle Health applications, as well as Oracle Fusion Sales, Service, and Marketing. The company also offers cloud-based industry solutions for various industries; Oracle cloud license and on-premise license; and Oracle license support services. In addition, it provides cloud and license business\' infrastructure technologies, such as the Oracle Database and MySQL Database; Java, a software development language; and middleware, including development tools and others. The company\'s cloud and license business\' infrastructure technologies also comprise cloud-based compute, storage, and networking capabilities; and Oracle autonomous database, as well as AI, Internet-of-Things, machine learning, digital assistant, and blockchain. Further, it provides hardware products and other hardware-related software offerings, including Oracle engineered systems, enterprise servers, storage solutions, industry-specific hardware, virtualization software, operating systems, management software, and related hardware support services, and consulting and advanced customer services. It markets and sells its cloud, license, hardware, support, and services offerings directly to businesses in various industries, government agencies, and educational institutions, as well as through indirect channels. Oracle Corporation has a strategic alliance with Metron, Inc. The company was founded in 1977 and is headquartered in Austin, Texas.'),
(30, 'ADBE', 'Adobe Inc.', 304.090000, -0.350006, -0.1150, 4569086, 128994975744, 18.2199, 465.700000, 301.400000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:13', 'US', 'Technology', 'Software - Application', 322.260000, 304.440000, 305.820000, 301.400000, 3960131, 1.5260, 11.5633, 18.2199, 16.690000, NULL, NULL, 27.873000, 10.9098, 418600000, 415811550, 2.8700, NULL, 'https://www.adobe.com', 'Adobe Inc. operates as a technology company worldwide. Its Digital Media segment offers products and services that enable individuals, teams, and enterprises to create, publish, and promote content; Document Cloud, a cloud-based document services platform; and Creative Cloud, a subscription service that allows subscribers to use its creative products and applications (apps) integrated with cloud-delivered services across various surfaces and platforms. This segment serves photographers, video editors, graphic and experience designers, game developers, content creators, students, marketers, knowledge workers, and consumers. The company\'s Digital Experience segment provides an integrated platform; and products, services, and solutions that enable brands and businesses to create, manage, execute, measure, monetize, and optimize customer experiences from analytics to commerce. This segment serves marketers, advertisers, agencies, publishers, merchandisers, merchants, web analysts, data scientists, developers, and executives across the C-suite. Its Publishing and Advertising segment offers e-learning, technical document publishing, web conferencing, document and forms platform, web application development, high-end printing, and Adobe Advertising solutions. It provides consulting, training, customer management, technical support, and learning services. The company offers its solutions to enterprise customers, and businesses and consumers; and licenses its products to end-user customers through app stores and website at adobe.com. It markets and distributes its products through distributors, retailers, software developers, mobile app stores, systems integrators, independent software vendors, value-added resellers, and original equipment and hardware manufacturers. The company has a strategic alliance with HUMAIN for the development of generative AI models and AI-powered applications. The company was formerly known as Adobe Systems Incorporated and changed its name to Adobe Inc. in October 2018. Adobe Inc. was founded in 1982 and is headquartered in San Jose, California.'),
(31, 'PYPL', 'PayPal Holdings, Inc.', 56.740000, -0.919998, -1.5956, 15376105, 54208172032, 11.3936, 93.245000, 55.850000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:13', 'US', 'Financial Services', 'Credit Services', 56.410000, 57.660000, 57.862000, 56.600000, 16438624, 1.4270, 9.8586, 11.3936, 4.980000, 0.9900, 0.560000, 21.464000, 2.6435, 935651953, 933528023, 2.9700, NULL, 'https://www.paypal.com', 'PayPal Holdings, Inc. operates a technology platform that enables digital payments for merchants and consumers worldwide. It operates a two-sided network at scale that connects merchants and consumers that enables its customers to connect, transact, and send and receive payments through online and in person, as well as transfer and withdraw funds using various funding sources, such as bank accounts, PayPal or Venmo account balance, consumer credit products, credit and debit cards, and cryptocurrencies, as well as other stored value products, including gift cards and eligible rewards. The company provides payment solutions under the PayPal, PayPal Credit, Braintree, Venmo, Xoom, Zettle, Hyperwallet, Honey, and Paidy names. The company was founded in 1998 and is headquartered in San Jose, California.'),
(32, 'NBY', 'NovaBay Pharmaceuticals, Inc.', 12.690000, -0.040000, -0.3142, 989695, 1599076352, 2.4593, 19.950000, 0.460000, 'USD', 'ASE', 'stock', '2026-01-16 02:44:13', 'US', 'Healthcare', 'Biotechnology', 12.400000, 12.730000, 14.740000, 12.420000, 1294762, 0.0020, -15.4756, 2.4593, 5.160000, NULL, NULL, -0.446000, -28.4529, 126010749, 12393157, 0.5900, NULL, 'https://novabay.com', 'NovaBay Pharmaceuticals, Inc. manufactures and sells wound care products. The company offers hypochlorous acid for use in the cleansing and irrigation of post-surgical wounds, minor burns, and superficial abrasions. It sells its products to its distribution partners in China. The company was formerly known as NovaCal Pharmaceuticals, Inc. and changed its name to NovaBay Pharmaceuticals, Inc. in February 2007. NovaBay Pharmaceuticals, Inc. was incorporated in 2000 and is headquartered in Emeryville, California.'),
(33, 'CGON', 'CG Oncology, Inc.', 53.070000, -2.440000, -4.3956, 759580, 4280953856, NULL, 57.395000, 14.800000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:14', 'US', 'Healthcare', 'Biotechnology', 53.030000, 55.510000, 56.350000, 52.600100, 1003111, NULL, -21.0678, NULL, -2.050000, NULL, NULL, 8.785000, 6.0410, 80666179, 65435598, 15.4300, NULL, 'https://cgoncology.com', 'CG Oncology, Inc., a late-stage clinical biopharmaceutical company, develops and commercializes backbone bladder-sparing therapeutics for patients with bladder cancer. The company develops BOND-003, which is in phase 3 clinical trial for the treatment of high-risk bacillus calmette guerin (BCG)-unresponsive non-muscle invasive bladder cancer (NMIBC) patients; CORE-001 that is in phase 2 clinical trial to treat cretostimogene in combination with pembrolizumab in high-risk BCG-unresponsive NMIBC patients; and CORE-002 for the treatment of cretostimogene in combination with the checkpoint inhibitor nivolumab in muscle invasive bladder cancer patients. It also develops PIVOT-006, a cretostimogene monotherapy that is in phase 3 clinical trial for intermediate-risk NMIBC following transurethral resection of the bladder tumor; and CORE-008, which is in phase 2 clinical trial for treating patients with high-risk NMIBC, including BCG-exposed and BCG-naïve NMIBC patients. The company was formerly known as Cold Genesys, Inc. and changed its name to CG Oncology, Inc. in June 2020. CG Oncology, Inc. was founded in 2010 and is headquartered in Irvine, California.'),
(34, 'APLD', 'Applied Digital Corporation', 35.220000, -0.879997, -2.4377, 25818740, 9847013376, NULL, 40.200000, 3.310000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:14', 'US', 'Technology', 'Information Technology Services', 36.885000, 36.100000, 37.060000, 35.050000, 29951206, 6.9240, -39.3520, NULL, -0.390000, NULL, NULL, 5.194000, 6.7809, 279585823, 235827846, 3.0300, NULL, 'https://applieddigital.com', 'Applied Digital Corporation designs, develops, and operates digital infrastructure solutions to high-performance computing (HPC) and artificial intelligence industries in North America. It operates through: Data Center Hosting Business, and HPC Hosting Business. The company offers infrastructure services to crypto mining customers; and GPU computing solutions for critical workloads related to AI, machine learning, and other HPC tasks. It also engages in the designing, constructing, and managing of data centers to support HPC applications. The company was formerly known as Applied Blockchain, Inc. and changed its name to Applied Digital Corporation in November 2022. Applied Digital Corporation has an lease agreement with CoreWeave for an additional 150MW at its Polaris Forge 1 Campus in Ellendale, North Dakota. Applied Digital Corporation is based in Dallas, Texas.'),
(35, 'UWMC', 'UWM Holdings Corporation', 5.800000, 0.350000, 6.4220, 23999891, 9358288896, 52.7273, 7.140000, 3.795000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:14', 'US', 'Financial Services', 'Mortgage Finance', 5.450000, 5.450000, 5.825000, 5.450000, 11750691, 1.9290, 13.0173, 52.7273, 0.110000, 6.9000, 0.400000, 0.758000, 7.6517, 268415480, 214987576, 3.2400, NULL, 'https://www.uwm.com', 'UWM Holdings Corporation engages in the origination, sale, and servicing residential mortgage lending in the United States. The company offers mortgage loans through wholesale channel. It originates primarily conforming and government loans. UWM Holdings Corporation was founded in 1986 and is headquartered in Pontiac, Michigan.'),
(36, 'OPEN', 'Opendoor Technologies Inc', 6.300000, -0.340000, -5.1205, 46693347, 6008865280, NULL, 10.870000, 0.508000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:15', 'US', 'Real Estate', 'Real Estate Services', 7.050000, 6.640000, 6.740000, 6.215000, 97906091, 3.6520, -29.2099, NULL, -0.440000, NULL, NULL, 1.051000, 5.9943, 953788119, 627496430, 1.8800, NULL, 'https://www.opendoor.com', 'Opendoor Technologies Inc. operates a digital platform for residential real estate transactions in the United States. It buys and sells homes. The company offers sell to opendoor product that enables homeowners to sell their home directly to it and resell the home to a home buyer; list with opendoor product that allows customers to list their home on the MLS with opendoor and receive cash offer; and opendoor marketplace product that connects the home seller with an institutional or retail buyer. It also provides real estate brokerage, title insurance and settlement, and escrow services, as well as property and casualty insurance, real estate licenses, and construction services. The company was formerly known as Social Capital Hedosophia Holdings Corp. II and changed its name to Opendoor Technologies Inc. Opendoor Technologies Inc. was incorporated in 2013 and is based in Tempe, Arizona.'),
(37, 'LQDA', 'Liquidia Corporation', 38.790000, -1.200000, -3.0008, 2359016, 3374554624, NULL, 41.570000, 11.260000, 'USD', 'NCM', 'stock', '2026-01-16 02:44:15', 'US', 'Healthcare', 'Biotechnology', 40.190000, 39.990000, 41.570000, 38.760000, 1979213, 0.4860, 14.3987, NULL, -1.460000, NULL, NULL, 0.254000, 152.7165, 86995483, 60654991, 9.7800, NULL, 'https://www.liquidia.com', 'Liquidia Corporation, a biopharmaceutical company, develops, manufactures, and commercializes various products for unmet patient needs in the United States. Its lead product candidates include YUTREPIA, an inhaled dry powder formulation of treprostinil for the treatment of pulmonary arterial hypertension (PAH) and pulmonary hypertension associated with interstitial lung disease (PH-ILD). The company also offers Remodulin, a treprostinil administered through continuous intravenous and subcutaneous infusion; and develops L606, an investigational liposomal formulation of treprostinil for the treatment of pulmonary arterial hypertension (PAH) and pulmonary hypertension associated with interstitial lung disease (PH-ILD). The company has a license agreement with Pharmosa Biopharm Inc to develop and commercialize L606, an inhaled sustained-release formulation of Treprostinil for the treatment of PAH and PH-ILD. Liquidia Corporation was founded in 2004 and is based in Morrisville, North Carolina.'),
(38, 'SNDK', 'Sandisk Corporation', 409.240000, 21.430000, 5.5259, 14057412, 59975421952, NULL, 423.350000, 27.885000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:15', 'US', 'Technology', 'Computer Hardware', 398.930000, 387.810000, 423.350000, 398.680000, 11860349, NULL, 18.0237, NULL, -12.030000, NULL, NULL, 63.816000, 6.4128, 146553179, 138031112, 1.1000, NULL, 'https://www.sandisk.com', 'Sandisk Corporation develops, manufactures, and sells data storage devices and solutions using NAND flash technology in the United States, Europe, the Middle East, Africa, Asia, and internationally. The company offers solid state drives for desktop and notebook PCs, gaming consoles, and set top boxes; and flash-based embedded storage products for mobile phones, tablets, notebook PCs and other portable and wearable devices, automotive applications, Internet of Things, industrial, and connected home applications, as well as removable cards, universal serial bus drives, and wafers and components. It sells its products to computer manufacturers and original equipment manufacturers, datacenters, private cloud customers, cloud service providers, resellers, distributors, and retailers through its sales personnel, dealers, distributors, retailers, and subsidiaries. Sandisk Corporation was incorporated in 2024 and is based in Milpitas, California.'),
(39, 'BLDR', 'Builders FirstSource, Inc.', 128.960000, 2.580010, 2.0415, 1531643, 14260472832, 24.4706, 175.120000, 94.350000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:16', 'US', 'Industrials', 'Building Products & Equipment', 127.460000, 126.380000, 130.305000, 126.905000, 2051336, 1.5690, 20.3746, 24.4706, 5.270000, NULL, NULL, 39.042000, 3.3031, 110580581, 107547356, 2.9100, NULL, 'https://www.bldr.com', 'Builders FirstSource, Inc., together with its subsidiaries, manufactures and supplies building materials, manufactured components, and construction services to professional homebuilders, sub-contractors, remodelers, and consumers in the United States. It offers manufactured products, such as wood floor and roof trusses, floor trusses, wall panels, stairs, and engineered wood products under the Ready-Frame brand name; windows and doors comprising interior and exterior door units; millwork includes interior trim and custom features, such as intricate mouldings, stair parts, and columns under the Synboard brand name. The company also provides specialty building products and services, including vinyl, composite and wood siding, exterior trims, metal studs, cement, roofing, insulation, wallboards, ceilings, cabinets, and hardware products; turn-key framing, shell construction, design assistance, and professional installation services; and lumber and lumber sheet goods comprising dimensional lumber, plywood, and oriented strand board products that are used in on-site house framing. In addition, it offers software products, such as drafting, estimating, quoting, and virtual home design services, which provide software solutions to retailers, distributors, manufacturers, and homebuilders. It serves its products to production builders and small custom homebuilders, as well as multi-family builders, repair and remodeling contractors, and light commercial contractors. The company was formerly known as BSL Holdings, Inc. and changed its name to Builders FirstSource, Inc. in October 1999. Builders FirstSource, Inc. was incorporated in 1998 and is based in Irving, Texas.'),
(40, 'CCS', 'Century Communities, Inc.', 69.130000, 0.519997, 0.7579, 151201, 2051763200, 10.0773, 81.100000, 50.420000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:16', 'US', 'Real Estate', 'Real Estate - Development', 68.800000, 68.610000, 69.790000, 67.790000, 279024, 1.5510, 10.7931, 10.0773, 6.860000, 1.6900, 1.160000, 87.736000, 0.7879, 29384289, 24817383, 9.4200, NULL, 'https://www.centurycommunities.com', 'Century Communities, Inc., together with its subsidiaries, engages in the design, development, construction, marketing, and sale of single-family attached and detached homes. It is also involved in the entitlement and development of the underlying land; and provision of mortgage, title, and insurance services to its homebuyers. The company offers homes under the Century Communities and Century Complete brands. It sells homes through its sales representatives, retail studios, and internet, as well as through independent real estate brokers in 18 states in the United States. Century Communities, Inc. was founded in 2002 and is headquartered in Greenwood Village, Colorado.'),
(41, 'RGC', 'Regencell Bioscience Holdings L', 30.060000, -5.110000, -14.5294, 441835, 14864335872, NULL, 83.600000, 0.092789, 'USD', 'NCM', 'stock', '2026-01-16 02:44:16', 'US', 'Healthcare', 'Drug Manufacturers - Specialty & Generic', 44.370000, 35.170000, 33.900000, 28.230000, 401998, 2.0220, NULL, NULL, -0.010000, NULL, NULL, 0.010000, 3006.0000, 494488908, 18434546, 3.9800, NULL, 'https://www.regencellbioscience.com', 'Regencell Bioscience Holdings Limited operates as a Traditional Chinese medicine (TCM) bioscience company in Hong Kong. It focuses on the research, development, and commercialization of TCM for the treatment of neurocognitive disorders and degeneration, primarily for attention deficit hyperactivity disorder and autism spectrum disorder. The company was incorporated in 2014 and is headquartered in Causeway Bay, Hong Kong.'),
(42, 'TTMI', 'TTM Technologies, Inc.', 100.900000, 4.380000, 4.5379, 3681510, 10426071040, 80.0794, 106.680000, 15.770000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:17', 'US', 'Technology', 'Electronic Components', 94.675000, 96.520000, 106.680000, 99.660000, 2236539, 1.7450, 34.3489, 80.0794, 1.260000, NULL, NULL, 16.466000, 6.1278, 103330725, 101770431, 2.6600, NULL, 'https://www.ttm.com', 'TTM Technologies, Inc. manufactures and sells mission systems, radio frequency (RF) components and RF microwave/microelectronic assemblies, and printed circuit boards (PCB) in the United States, Taiwan, and internationally. It operates in two segments, PCB and RF&S Components. The company offers a range of engineered systems, RF and microwave assemblies, HDI PCBs, flexible PCBs, rigid-flex PCBs, custom assemblies and system integration, IC substrates, passive RF components, advanced ceramic RF components, hi-reliability multi-chip modules, beamforming and switching networks, PCB products, RF components, and backplane/custom assembly solutions, including conventional PCBs. It also provides value-added services, such as design for manufacturability, PCB layout design, simulation and testing services, and quick turnaround production, as well as specialized assembly and RF testing. In addition, the company offers maritime surveillance and weather avoidance radar systems for fixed- and rotary-wing aircraft, unmanned aerial vehicles, and shipboard platforms; AN/APS-153 multi-mode radar; communications suite within the MH-60R/S multi-mission helicopters; and develops multi-mode maritime and overland surveillance AESA radar under MOSAIC brand. Further, it provides identification friend, monopulse secondary surveillance radars, and air traffic control systems; wired and wireless communication systems; custom electronic assemblies; quick turnaround services comprising prototype production and ramp-to-volume production; and thermal management. The company serves original equipment manufacturers and electronic manufacturing services providers, original design manufacturers, distributors, and government agencies; and aerospace and defense, data center computing, automotive, medical, industrial, and instrumentation, and networking markets. TTM Technologies, Inc. was incorporated in 1978 and is headquartered in Santa Ana, California.'),
(43, 'RVMD', 'Revolution Medicines, Inc.', 123.270000, 2.050000, 1.6911, 2967699, 23830532096, NULL, 124.160000, 29.170000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:17', 'US', 'Healthcare', 'Biotechnology', 118.090000, 121.220000, 124.160000, 120.700000, 3162868, 0.9900, -19.6131, NULL, -5.190000, NULL, NULL, 8.418000, 14.6436, 193319805, 173962693, 6.6200, NULL, 'https://www.revmed.com', 'Revolution Medicines, Inc., a clinical-stage precision oncology company, develops novel targeted therapies for RAS-addicted cancers. The company\'s research and development pipeline consist of RAS(ON) inhibitors that binds RAS variants to be used as monotherapy in combination with other RAS(ON) inhibitors and/or in combination with RAS companion inhibitors or other therapeutic agents, and RAS companion inhibitors to suppress cooperating targets and pathways that sustain RAS-addicted cancers. Its RAS(ON) inhibitors include daraxonrasib (RMC-6236), elironrasib G12C (RMC-6291), and zoldonrasib G12D (RMC-9805), which are in phase 1 clinical trial; and development candidates comprise RMC-5127 (G12V), RMC-0708 (Q61H), and RMC-8839 (G13C). The company\'s RAS companion inhibitors include RMC-4630 that is in phase 2 clinical trial; RMC-5552, a selective inhibitor of mTORC1 signaling in tumors, which is in phase 1 clinical trial; and RMC-5845 that targets SOS1. Revolution Medicines, Inc. was incorporated in 2014 and is headquartered in Redwood City, California.'),
(44, 'VST', 'Vistra Corp.', 180.180000, 11.210000, 6.6343, 7023267, 61049577472, 65.0469, 219.820000, 90.510000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:17', 'US', 'Utilities', 'Utilities - Independent Power Producers', 173.000000, 168.970000, 182.560000, 171.680000, 4767290, 1.4180, 19.1551, 65.0469, 2.770000, 0.5000, 0.910000, 8.073000, 22.3188, 338825490, 316547714, 1.8800, NULL, 'https://vistracorp.com', 'Vistra Corp., together with its subsidiaries, operates as an integrated retail electricity and power generation company in the United States. It operates through five segments: Retail, Texas, East, West, and Asset Closure. The company retails electricity and natural gas to residential, commercial, and industrial customers across states in the United States and the District of Columbia. It also involved in the electricity generation, wholesale energy purchases and sales, commodity risk management, fuel production, and fuel logistics management activities. It serves approximately 5 million customers with a generation capacity of approximately 41,000 megawatts with a portfolio of natural gas, nuclear, coal, solar, and battery energy storage facilities. The company was formerly known as Vistra Energy Corp. and changed its name to Vistra Corp. in July 2020. Vistra Corp. was founded in 1882 and is based in Irving, Texas.'),
(45, 'MTH', 'Meritage Homes Corporation', 78.250000, 1.170000, 1.5179, 569322, 5567967744, 10.4473, 84.740000, 59.270000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:18', 'US', 'Consumer Cyclical', 'Residential Construction', 77.410000, 77.080000, 78.395000, 76.302500, 869885, 1.4810, 11.3320, 10.4473, 7.490000, 2.2000, 1.720000, 75.100000, 1.0419, 70406707, 68768343, 5.7400, NULL, 'https://www.meritagehomes.com', 'Meritage Homes Corporation, together with its subsidiaries, designs and builds single-family attached and detached homes in the United States. It operates through two segments: Homebuilding and Financial Services. The company acquires and develops land; and constructs, markets, and sells homes for entry-level and first move-up buyers in Arizona, California, Colorado, Utah, Texas, Florida, Georgia, North Carolina, South Carolina, and Tennessee. It also provides title and escrow, mortgage, insurance, title insurance, and closing/settlement services to its homebuyers. Meritage Homes Corporation was founded in 1985 and is based in Scottsdale, Arizona.'),
(46, 'BE', 'Bloom Energy Corporation', 139.170000, 5.709990, 4.2784, 8871542, 32915200000, 1739.6250, 147.860000, 15.150000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:18', 'US', 'Industrials', 'Electrical Equipment & Parts', 138.490000, 133.460000, 144.500000, 134.660000, 13732875, 3.0230, 129.1098, 1739.6250, 0.080000, NULL, NULL, 2.763000, 50.3692, 236510755, 220234085, 1.8400, NULL, 'https://www.bloomenergy.com', 'Bloom Energy Corporation designs, manufactures, sells, and installs solid-oxide fuel cell systems for on-site power generation in the United States and internationally. It offers Bloom Energy Server, a power generation platform to convert fuel, such as natural gas, biogas, hydrogen, or a blend of these fuels, into electricity through an electrochemical process without combustion. The company also provides Bloom Electrolyzer for producing hydrogen. It sells its products through direct and indirect sales channels to utilities, data centers, agriculture, retail, hospitals, higher education, biotech, and manufacturing industries. The company was formerly known as Ion America Corp. and changed its name to Bloom Energy Corporation in 2006. Bloom Energy Corporation was incorporated in 2001 and is headquartered in San Jose, California.'),
(47, 'HBNB', 'Hotel101 Global Holdings Corp.', 9.970000, 0.506101, 5.3477, 29349, 2334499584, NULL, 19.280000, 1.550000, 'USD', 'NCM', 'stock', '2026-01-16 02:44:18', 'US', 'Real Estate', 'Real Estate Services', 9.250000, 9.463900, 10.000000, 9.500000, 37554, NULL, NULL, NULL, -0.070000, NULL, NULL, 0.078000, 127.8205, 234152398, 11672497, 1.0400, NULL, 'https://www.hotel101global.com', 'Hotel101 Global Holdings Corp. operates prop-tech hospitality platform. It enables hotel and hospitality sector through its tech-enabled business model, including advance sale of individual hotel units during the construction phase; and long-term recurring revenue derived from day-to-day hotel operations. The company is based in Singapore, Singapore. Hotel101 Global Holdings Corp. operates as a subsidiary of DoubleDragon Corporation.'),
(48, 'OLMA', 'Olema Pharmaceuticals, Inc.', 29.190000, 0.420000, 1.4599, 1097845, 2339868160, NULL, 36.259000, 2.860000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:19', 'US', 'Healthcare', 'Biotechnology', 28.390000, 28.770000, 29.220000, 27.770000, 3895013, 1.9320, -12.6360, NULL, -1.760000, NULL, NULL, 4.479000, 6.5171, 80159923, 49842298, 3.9400, NULL, 'https://olema.com', 'Olema Pharmaceuticals, Inc., a clinical-stage biopharmaceutical company, focuses on the discovery, development, and commercialization of therapies for women\'s cancers. The company\'s lead product candidate is palazestrant, an estrogen receptor (ER) antagonist and a selective ER degrader, which is in Phase 3 clinical trial for the treatment of recurrent, locally advanced, or metastatic estrogen receptor-positive, human epidermal growth factor receptor 2-negative breast cancer; OPERA-01, the pivotal Phase 3 clinical trial of palazestrant as a monotherapy in second/third-line ER+/HER2- metastatic breast cancer; and palazestrant with CDK4/6 inhibitors palbociclib and ribociclib, a phosphatidylinositol 3 kinase alpha (PI3Ka) inhibitor alpelisib, and with an mTOR inhibitor everolimus that is in Phase 1/2 clinical trial for the treatment of recurrent, locally advanced, or metastatic estrogen receptor-positive human epidermal growth factor receptor 2-negative breast cancer. It also develops OP-3136, an orally-available small molecule that potently and selectively inhibits KAT6 for patients with ER+/HER2- metastatic breast cancer and other cancers which is in Phase 1 clinical trial. The company was formerly known as CombiThera, Inc. and changed its name to Olema Pharmaceuticals, Inc. in March 2009. Olema Pharmaceuticals, Inc. was incorporated in 2006 and is headquartered in San Francisco, California.'),
(49, 'RKT', 'Rocket Companies, Inc.', 23.440000, 0.770000, 3.3966, 25511559, 66004459520, NULL, 23.600000, 10.940000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:19', 'US', 'Financial Services', 'Mortgage Finance', 22.900000, 22.670000, 23.600000, 22.900000, 32941429, 2.2960, 27.9154, NULL, -0.030000, NULL, NULL, 4.195000, 5.5876, 967010557, 941746256, 2.2600, NULL, 'https://www.rocketcompanies.com', 'Rocket Companies, Inc., provides spanning mortgage, real estate, and personal finance services in the United States and Canada. It operates through two segments, Direct to Consumer and Partner Network. The company offers Rocket Mortgage, a mortgage lender service; Rocket Close, an appraisal management, settlement, and title service; Rocket Homes, a home search platform and real estate agent referral network that provides technology-enabled services to support the home buying and selling experience; and Rocket Loans, an online-based personal loans business. It also provides Rocket Money that provides financial wellness services, including subscription cancellation, budget management, and credit score; and Lendesk, a software service that provides a point of sale system for mortgage professionals and a loan origination system for private lenders. In addition, the company originates, closes, sells, and services agency-conforming loans. Rocket Companies, Inc. was founded in 1985 and is headquartered in Detroit, Michigan. Rocket Companies, Inc. operates as a subsidiary of Rock Holdings Inc.'),
(50, 'FLNC', 'Fluence Energy, Inc.', 25.500000, 2.850000, 12.5828, 7069988, 4663150080, NULL, 26.320000, 3.460000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:19', 'US', 'Utilities', 'Utilities - Renewable', 23.485000, 22.650000, 26.320000, 23.390000, 6172536, 2.8850, 104.0349, NULL, -0.370000, NULL, NULL, 3.275000, 7.7863, 131369447, 96090182, 4.2400, NULL, 'https://fluenceenergy.com', 'Fluence Energy, Inc., through its subsidiaries, provides energy storage and optimization software for renewables and storage applications in the Americas, the Asia Pacific, Europe, the Middle East, and Africa. It sells energy storage products with integrated hardware, software, and digital intelligence. The company\'s energy storage products include Gridstack Pro, a large-scale front-of-the-meter application; Gridstack, a front-of-the-meter application; Ultrastack for critical system requirements of distribution and transmission networks; Smartstack, a split architecture design, incorporating embedded intelligence and higher energy density compared to traditional AC systems. The company also provides operational and maintenance services; and digital applications. It serves independent power producers, developers, conglomerates, utilities/load-serving entities, and commercial and industrial customers. Fluence Energy, Inc. was founded in 2018 and is headquartered in Arlington, Virginia.'),
(51, 'KTOS', 'Kratos Defense & Security Solut', 124.560000, 3.060000, 2.5185, 3595760, 21030797312, 1038.0000, 126.310000, 23.900000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:20', 'US', 'Industrials', 'Aerospace & Defense', 118.010000, 121.500000, 126.310000, 117.266700, 2998983, 1.0930, 163.7697, 1038.0000, 0.120000, NULL, NULL, 11.736000, 10.6135, 168840708, 166238873, 4.2100, NULL, 'https://www.kratosdefense.com', 'Kratos Defense & Security Solutions, Inc., a technology company, provides technology, products, and system and software for the defense, national security, and commercial markets in the United States, other North America, the Asia Pacific, the Middle East, Europe, and Internationally. The company operates in two segments, Kratos Government Solutions and Unmanned Systems. It offers ground systems for satellites and space vehicles, including software for command and control, telemetry, and tracking and control; jet powered unmanned aerial drone systems, hypersonic vehicles, and rocket systems; propulsion systems for drones, missiles, loitering munitions, supersonic systems, spacecraft, and launch systems; command, control, communication, computing, combat, and intelligence surveillance and reconnaissance; and microwave electronic products for missile, radar, missile defense, space, and satellite; and counter unmanned aircraft systems, directed energy, communication and other systems, and virtual and augmented reality training systems for the warfighter. The company primarily serves national security-related agencies, the U.S. Department of Defense, intelligence and classified agencies, international government agencies, and commercial customers. Kratos Defense & Security Solutions, Inc. was incorporated in 1994 and is headquartered in San Diego, California.'),
(52, 'EOSE', 'Eos Energy Enterprises, Inc.', 16.880000, -0.420000, -2.4278, 23480899, 5470776832, NULL, 19.860000, 3.070000, 'USD', 'NCM', 'stock', '2026-01-16 02:44:20', 'US', 'Industrials', 'Electrical Equipment & Parts', 15.975000, 17.300000, 18.230000, 16.840000, 21311211, 2.1200, -109.9173, NULL, -8.310000, NULL, NULL, -8.237000, -2.0493, 324098179, 283910247, 5.4800, NULL, 'https://www.eose.com', 'Eos Energy Enterprises, Inc. designs, develops, manufactures, and markets energy storage solutions for utility-scale, microgrid, and commercial and industrial applications in the United States. The company offers Znyth technology battery energy storage system (BESS), which provides the operating flexibility to manage increased grid complexity and price volatility. It also provides Z3 battery module that provides utilities, independent power producers, renewables developers, and commercial and industrial customers with an alternative to lithium-ion and lead-acid monopolar batteries for critical 3- to 12-hour discharge duration applications; battery management system, which provides a remote asset monitoring capability and service to track the performance and health of BESS and identify future system performance issues through predictive analytics; and project management and commissioning services, as well as long-term maintenance plans. The company was founded in 2008 and is headquartered in Edison, New Jersey.'),
(53, 'LPX', 'Louisiana-Pacific Corporation', 93.710000, 1.720000, 1.8698, 689324, 6526288896, 30.3269, 119.910000, 73.420000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:21', 'US', 'Industrials', 'Building Products & Equipment', 93.520000, 91.990000, 94.070000, 91.430000, 988744, 1.7990, 25.9151, 30.3269, 3.090000, 1.2000, 1.120000, 24.843000, 3.7721, 69643461, 59173960, 4.7500, NULL, 'https://www.lpcorp.com', 'Louisiana-Pacific Corporation, together with its subsidiaries, provides building solutions for applications in new home construction, repair and remodeling, and outdoor structure markets. It operates through three segments: Siding, Oriented Strand Board (OSB), and LP South America (LPSA). The Siding segment consists of a portfolio of engineered wood siding, trim, soffit, and fascia products, including LP SmartSide trim and siding, LP SmartSide ExpertFinish trim and siding, LP BuilderSeries lap siding, and LP outdoor building solutions. The OSB segment manufactures and distributes OSB structural panel products, including the value-added OSB product portfolio comprising LP Structural Solutions, which includes LP TechShield radiant barriers, LP WeatherLogic air and water barriers, LP Legacy premium sub-floorings, LP NovaCore thermal insulated sheathing, LP FlameBlock fire-rated sheathing, and LP TopNotch 350 durable sub-flooring. The LPSA segment manufactures and distributes OSB structural panel and siding solutions. This segment distributes and sells a variety of companion products for the region\'s transition to wood frame construction. The company sells its products primarily to retailers, wholesalers, home building, and industrial businesses in North America, South America, Asia, Australia, and Europe. Louisiana-Pacific Corporation was incorporated in 1972 and is headquartered in Nashville, Tennessee.'),
(54, 'LEN', 'Lennar Corporation', 122.250000, 0.860001, 0.7085, 2296025, 30192197632, 15.3195, 144.240000, 98.420000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:21', 'US', 'Consumer Cyclical', 'Residential Construction', 121.640000, 121.390000, 122.710000, 119.270000, 6006686, 1.4340, 13.6513, 15.3195, 7.980000, 1.6400, 2.000000, 87.015000, 1.4049, 215753936, 218089581, 1.8900, NULL, 'https://www.lennar.com', 'Lennar Corporation, together with its subsidiaries, operates as a homebuilder primarily under the Lennar brand in the United States. It operates through Homebuilding East, Homebuilding Central, Homebuilding Texas, Homebuilding West, Financial Services, Multifamily, and Lennar Other segments. The company\'s homebuilding operations include the construction and sale of single-family attached and detached homes, as well as the purchase, development, and sale of residential land; and development, construction, and management of multifamily rental properties. It also offers residential mortgage financing, title, insurance, and closing services for home buyers and others, as well as originates and sells securitization commercial mortgage loans. In addition, the company is involved in the fund investment activity. It primarily serves first-time, move-up, active adult, and luxury homebuyers. The company was founded in 1954 and is based in Miami, Florida.'),
(55, 'TPH', 'Tri Pointe Homes, Inc.', 35.500000, 0.410000, 1.1684, 380384, 3106481152, 10.4720, 38.960000, 27.900000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:21', 'US', 'Consumer Cyclical', 'Residential Construction', 35.150000, 35.090000, 35.580000, 35.025000, 936567, 1.3580, 15.5475, 10.4720, 3.390000, NULL, NULL, 38.399000, 0.9245, 85953497, 83519294, 5.8400, NULL, 'https://www.tripointehomes.com', 'Tri Pointe Homes, Inc. engages in the design, construction, and sale of single-family attached and detached homes in the United States. The company operates in two segments, Homebuilding and Financial Services. It operates active selling communities and owns or controls lots. The company sells its homes through its own sales representatives and independent real estate brokers. It also provides financial services, such as mortgage financing, title and escrow, and property and casualty insurance agency services. The company was formerly known as TRI Pointe Group, Inc. and changed its name to Tri Pointe Homes, Inc. in January 2021. Tri Pointe Homes, Inc. was founded in 2009 and is based in Incline Village, Nevada.');
INSERT INTO `market_data` (`id`, `symbol`, `name`, `price`, `change`, `change_percent`, `volume`, `market_cap`, `pe_ratio`, `52_week_high`, `52_week_low`, `currency`, `exchange`, `asset_type`, `last_updated`, `country_code`, `sector`, `industry`, `open_price`, `previous_close`, `day_high`, `day_low`, `avg_volume`, `beta`, `forward_pe`, `trailing_pe`, `eps`, `dividend_yield`, `dividend_rate`, `book_value`, `price_to_book`, `shares_outstanding`, `float_shares`, `short_ratio`, `logo_url`, `website`, `description`) VALUES
(56, 'LRCX', 'Lam Research Corporation', 217.470000, 8.680010, 4.1573, 15235138, 274236702720, 48.1128, 229.320000, 56.320000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:22', 'US', 'Technology', 'Semiconductor Equipment & Materials', 219.420000, 208.790000, 229.320000, 217.210000, 11297152, 1.7790, 37.5421, 48.1128, 4.520000, 0.4800, 1.040000, 8.095000, 26.8647, 1256030000, 1251156604, 3.3100, NULL, 'https://www.lamresearch.com', 'Lam Research Corporation designs, manufactures, markets, refurbishes, and services semiconductor processing equipment used in the fabrication of integrated circuits in the United States, China, Korea, Taiwan, Japan, Southeast Asia, and Europe. The company offers ALTUS systems to deposit conformal or selective films for tungsten or molybdenum metallization applications; SABRE electrochemical deposition products for copper interconnect transition that offers copper damascene manufacturing; SPEED gapfill high-density plasma chemical vapor deposition (CVD) products; Striker single-wafer atomic layer deposition products for dielectric film solutions; and VECTOR plasma-enhanced CVD products. It also provides Flex for dielectric etch applications; Vantex, a dielectric etch system that provides RF technology and repeatable wafer-to-wafer performance enabled by Equipment Intelligence solutions; Kiyo for conductor etch applications; Syndion for through-silicon via etch applications; and Versys metal products for metal etch processes. In addition, the company offers Coronus bevel clean products to enhance die yield; and Da Vinci, DV-Prime, EOS, and SP series products to address various wafer cleaning applications. Further, it provides Reliant deposition, etch, and clean products; and Sense.i platform products, as well as customer service, spares, and upgrades. Lam Research Corporation was incorporated in 1980 and is headquartered in Fremont, California.'),
(57, 'EXK', 'Endeavour Silver Corporation', 11.570000, 0.360000, 3.2114, 11531842, 3403633664, NULL, 11.700000, 2.950000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:22', 'US', 'Basic Materials', 'Silver', 10.960000, 11.210000, 11.700000, 10.860000, 13727237, 2.1530, 11.2169, NULL, -0.330000, NULL, NULL, 1.730000, 6.6879, 294177499, 293650921, 1.1100, NULL, 'https://www.edrsilver.com', 'Endeavour Silver Corp., a silver mining company, engages in the acquisition, exploration, development, extraction, processing, refining, and reclamation of mineral properties in Mexico, Chile, Peru, and the United States. It explores for gold and silver deposits, and precious metals, as well as polymetals. The company was formerly known as Endeavour Gold Corp. and changed its name to Endeavour Silver Corp. in September 2004. Endeavour Silver Corp. was incorporated in 1981 and is headquartered in Vancouver, Canada.'),
(58, 'IBP', 'Installed Building Products, In', 314.400000, 8.449980, 2.7619, 160999, 8481051648, 33.9159, 315.990000, 150.830000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:22', 'US', 'Consumer Cyclical', 'Residential Construction', 305.570000, 305.950000, 315.990000, 306.050000, 324781, 1.9240, 28.5603, 33.9159, 9.270000, 1.0400, 3.180000, 25.169000, 12.4916, 26975357, 22863906, 7.3400, NULL, 'https://www.installedbuildingproducts.com', 'Installed Building Products, Inc., together with its subsidiaries, engages in the installation of insulation for residential and commercial builders in the United States. It operates through three segments: Installation, Distribution, and Manufacturing Operations. The company offers a range of insulation materials, such as fiberglass and cellulose, and spray foam insulation materials. It is also involved in the installation of insulation and sealant materials in various areas of a structure, which includes basement and crawl space, building envelope, attic, and acoustical applications. In addition, the company installs a range of caulk and sealant products that control air infiltration in residential and commercial buildings; basic sliding door and complex custom designs; and custom designed mirrors, as well as closet shelving systems. Further, it installs and services garage doors and openers, including steel, aluminum, wood, and vinyl garage doors, as well as opener systems; installs waterproofing and caulking and moisture protection systems; offers sheet and hot applied waterproofing membrane, deck coating, bentonite, and air and vapor systems; and provides rain gutters installation services. Additionally, the company provides fire-stopping systems, including fire-rated joint assemblies, perimeter fire containment, and smoke and fire containment systems installation services; and cordless blinds, shades, and shutters installation services, as well as other complementary building products. It also distributes products and materials purchased wholesale from manufacturers, such as spray foam insulation, metal building insulation, residential insulation, and mechanical and fabricated Styrofoam insulation; and insulation products, including equipment, machines, and services. The company was formerly known as CCIB Holdco, Inc. Installed Building Products, Inc. was founded in 1977 and is based in Columbus, Ohio.'),
(59, 'ACMR', 'ACM Research, Inc.', 52.195000, 1.705000, 3.3769, 1623096, 3386226432, 30.3459, 54.825000, 16.805000, 'USD', 'NGM', 'stock', '2026-01-16 02:44:23', 'US', 'Technology', 'Semiconductor Equipment & Materials', 53.280000, 50.490000, 54.360000, 52.120000, 1309019, 1.4490, 25.0938, 30.3459, 1.720000, NULL, NULL, 22.083000, 2.3636, 59854640, 53114350, 3.4500, NULL, 'https://www.acmr.com', 'ACM Research, Inc., together with its subsidiaries, develops, manufactures, and sells capital equipment worldwide. It also develops, manufactures, and sells a range of packaging tools to wafer assembly and packaging customers. The company provides Wet Cleaning Equipment for Front End Production Processes; Ultra C SAPS II and Ultra C SAPS V which are a single-wafer, serial-processing tool used to remove random defects from wafer surfaces or interconnects and barrier metals as part of the chip front-end fabrication process or for recycling test wafers; and Ultra C TEBO II and Ultra C TEBO V, a single-wafer, serial-processing tool used at numerous manufacturing processing steps for cleaning of chips at process nodes of 28nm or less. In addition, it offers Ultra-C Tahoe wafer cleaning tool that delivers high cleaning performance using significantly less sulfuric acid and hydrogen peroxide than is typically consumed by conventional high-temperature single-wafer cleaning tools; and advanced packaging tools, such as coaters, developers, photoresist strippers, scrubbers, wet etchers, and copper-plating tools. Further, the company provides e Ultra fn Furnace, a dry processing tool; Ultra Pmax PECVD tool, for film uniformity; Ultra Track tool, a 300mm process tool that delivers air downflow, robot handling, and customizable software to address specific customer requirements; and a suite of semi-critical cleaning systems which include single wafer back side cleaning, scrubber, and auto bench cleaning tools. It markets and sells its products under the SAPS, TEBO, ULTRA C, ULTRA Fn, Ultra ECP, Ultra ECP map, and Ultra ECP ap trademarks through direct sales force and third-party representatives. ACM Research, Inc. was incorporated in 1998 and is headquartered in Fremont, California.'),
(60, 'HE', 'Hawaiian Electric Industries, I', 14.280000, 0.250000, 1.7819, 2476284, 2465020416, 6.5806, 15.050000, 8.750000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:23', 'US', 'Utilities', 'Utilities - Regulated Electric', 14.040000, 14.030000, 14.495500, 14.055100, 3447932, 0.6550, 15.1111, 6.5806, 2.170000, NULL, NULL, 9.059000, 1.5763, 172620476, 161520979, 3.5300, NULL, 'https://www.hei.com', 'Hawaiian Electric Industries, Inc., together with its subsidiaries, engages in the electric utility business in the United States. It operates through Electric Utility and Other segments. The Electric Utility segment engages in the production, purchase, transmission, distribution, and sale of electricity in the islands of Oahu; Hawaii; and Maui, Lanai, and Molokai. This segment\'s renewable energy sources and potential sources include wind, solar, photovoltaic, geothermal, wave, hydroelectric, municipal waste, and other biofuels. This segment serves suburban communities, resorts, the United States Armed Forces installations, and agricultural operations. The Other segment invests in non-regulated renewable energy and sustainable infrastructure in the State of Hawaii. Hawaiian Electric Industries, Inc. was founded in 1891 and is headquartered in Honolulu, Hawaii.'),
(61, 'TREX', 'Trex Company, Inc.', 43.080000, 0.070004, 0.1628, 1876537, 4620536320, 23.4130, 75.550000, 29.770000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:23', 'US', 'Industrials', 'Building Products & Equipment', 43.230000, 43.010000, 43.660000, 42.470000, 2765011, 1.5580, 26.3412, 23.4130, 1.840000, NULL, NULL, 9.720000, 4.4321, 107254784, 106605893, 3.9000, NULL, 'https://www.trex.com', 'Trex Company, Inc. manufactures and sells composite decking and railing products in the United States. The company offers decking products and accessories that can be used for protection against fading, staining, mold, and scratching, including Trex Transcend, which are decking products that can also be used as cladding; Trex Signature; Trex Transcend Lineage; Trex Select; Trex Enhance; Trex Hideaway fastener collection; and Trex DeckLighting, an outdoor lighting system that includes a post cap, deck rail, riser, a soffit, and a recessed deck lights. It also offers railing products, such as Trex Signature X-Series Railing, Trex Signature aluminum railing, Trex Transcend Railing, Trex Select Railing, Trex Select T-Rail, Trex Enhance Railing; and fencing products, which includes Trex Seclusions that consists of structural posts, bottom rails, pickets, top rails, and decorative post caps. In addition, the company acts as a licensor in various licensing agreements with third parties to manufacture and sell products under the Trex name, including Trex Outdoor Furniture; Trex RainEscape, an above joist deck drainage system; Trex Protect joist, beam and rim tape, a self-adhesive butyl tape that protects wooden deck framing/substructure elements; Trex RainEscape Soffit Light, a plug-and-play LED Soffit light that is installed in the under-deck ceiling of a two-story deck; Trex Seal Ledger Flashing Tape, butyl flashing tape with an aluminum liner; Trex Pergola, Pergolas made from low maintenance cellular PVC and all-aluminum product; Trex Lattice outdoor boards; Trex Cornhole boards; Trex Blade, a specialty saw blade for wood-alternative composite decking; Trex SpiralStairs; and Trex Outdoor Kitchen cabinetry. It sells its products through wholesale distributors, retail lumber dealers, and Home Depot and Lowe\'s stores. Trex Company, Inc. was founded in 1996 and is headquartered in Winchester, Virginia.'),
(62, 'FND', 'Floor & Decor Holdings, Inc.', 75.520000, 0.149994, 0.1990, 3120113, 8137742336, 37.7600, 108.760000, 55.110000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:24', 'US', 'Consumer Cyclical', 'Home Improvement Retail', 75.880000, 75.370000, 76.370000, 74.325000, 2584096, 1.7340, 35.8054, 37.7600, 2.000000, NULL, NULL, 21.923000, 3.4448, 107756127, 106172845, 4.3000, NULL, 'https://www.flooranddecor.com', 'Floor & Decor Holdings, Inc., together with its subsidiaries, operates as a multi-channel specialty retailer of hard surface flooring and related accessories, and commercial surfaces seller in the United States. The company offers wood-based laminate flooring, vinyl, and engineered/composite rigid core vinyl; porcelain and ceramic tile, porcelain mosaics, and porcelain tile slabs; grout, mortar, backer board, tools, adhesives, underlayments, moldings, and stair treads; and decorative tiles and mosaics, which includes natural stone, porcelain, ceramic, glass, wall tile, and decorative trims. The company also provides solid prefinished and unfinished hardwood, engineered hardwood, bamboo, and wood countertops; marble, limestone, travertine, slate, ledger, prefabricated countertops, thresholds, and shower benches; vanities, shower doors, bath accessories, faucets, sinks, custom countertops, bathroom mirrors, and bathroom lighting. It sells products through its warehouse-format stores and five small-format design studios, as well as through Website, FloorandDecor.com. The company serves professional installers, commercial businesses, and homeowners. The company was formerly known as FDO Holdings, Inc. and changed its name to Floor & Decor Holdings, Inc. in April 2017. Floor & Decor Holdings, Inc. was founded in 2000 and is headquartered in Atlanta, Georgia.'),
(63, 'OKLO', 'Oklo Inc.', 91.450000, -4.520000, -4.7098, 10464402, 14288794624, NULL, 193.840000, 17.420000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:24', 'US', 'Utilities', 'Utilities - Independent Power Producers', 97.800000, 95.970000, 99.289900, 91.380000, 13610003, 0.7730, -144.9815, NULL, -0.560000, NULL, NULL, 7.719000, 11.8474, 156247075, 127686672, 1.7400, NULL, 'https://www.oklo.com', 'Oklo Inc. develops advanced fission power plants to provide clean, reliable, and affordable energy at scale to the customers in the United States. It also commercializes nuclear fuel recycling technology that converts nuclear waste into useable fuel for its reactors. Oklo Inc. has an joint agreement with newcleo to develop advanced fuel fabrication and manufacturing infrastructure in the United States. Oklo Inc. is based in Santa Clara, California.'),
(64, 'ASTS', 'AST SpaceMobile, Inc.', 101.250000, 6.030000, 6.3327, 16787334, 37199384576, NULL, 104.800000, 17.500000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:24', 'US', 'Technology', 'Communication Equipment', 91.245000, 95.220000, 104.800000, 92.050000, 13289509, 2.6930, -127.9362, NULL, -1.140000, NULL, NULL, 4.561000, 22.1991, 278010950, 229726859, 2.4900, NULL, 'https://ast-science.com', 'AST SpaceMobile, Inc., together with its subsidiaries, designs and develops the constellation of BlueBird satellites in the United States. The company provides a cellular broadband network in space to be accessible directly by smartphones for commercial use and other applications, as well as for government use. Its SpaceMobile service provides cellular broadband services to end-users who are out of terrestrial cellular coverage. The company was founded in 2017 and is headquartered in Midland, Texas.'),
(65, 'DHI', 'D.R. Horton, Inc.', 161.000000, 1.700000, 1.0672, 2397762, 47021748224, 13.9033, 184.550000, 110.440000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:25', 'US', 'Consumer Cyclical', 'Residential Construction', 160.400000, 159.300000, 161.530000, 158.045000, 3134108, 1.4200, 12.1895, 13.9033, 11.580000, 1.1200, 1.800000, 82.148000, 1.9599, 291099538, 259557121, 5.4100, NULL, 'https://www.drhorton.com', 'D.R. Horton, Inc. operates as a homebuilding company in East, North, Southeast, South Central, Southwest, and Northwest regions in the United States. It engages in the acquisition and development of land; and construction and sale of residential homes in 126 markets across 36 states under the names of D.R. Horton. The company also constructs and sells single-family detached homes; and attached homes, such as townhomes and duplexes. In addition, it provides mortgage financing and title agency services; and engages in the residential lot development business. Further, the company develops, constructs, owns, leases, and sells multi-family and single-family rental properties; conducts insurance-related operations; and owns water rights and other water-related assets, as well as non-residential real estate, including ranch land and improvements. It primarily serves homebuyers. D.R. Horton, Inc. was founded in 1978 and is headquartered in Arlington, Texas.'),
(66, 'SMTC', 'Semtech Corporation', 77.260000, 3.080000, 4.1521, 1431153, 7149644800, 137.9643, 81.390000, 24.050000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:25', 'US', 'Technology', 'Semiconductors', 76.330000, 74.180000, 78.200000, 76.025000, 1585668, 2.0140, 35.5295, 137.9643, 0.560000, NULL, NULL, 6.128000, 12.6077, 92540057, 91943174, 4.0100, NULL, 'https://www.semtech.com', 'Semtech Corporation provides semiconductor, Internet of Things systems, and cloud connectivity service solutions in the Asia- Pacific, North America, and Europe. It operates in three segments: Signal Integrity, Analog Mixed Signal and Wireless, and IoT Systems and Connectivity. It provides signal integrity products, including a portfolio of optical and copper data communications and video transport products used in various infrastructure, and industrial applications; a portfolio of integrated circuits for data centers, enterprise networks, passive optical networks, wireless base station optical transceivers, and interface applications; and video products for broadcast applications, as well as video-over-IP technology for professional audio video applications. The company offers analog mixed signal and wireless products; protection devices, such as filter and termination devices that are integrated with the transient voltage suppressor devices, which protect electronic systems from voltage spikes; and designs, develops, manufactures, and markets radio frequency products used in industrial, medical, and communications applications, as well as specialized sensing products. In addition, it provides switching voltage regulators, combination switching and linear regulators, smart regulators, isolated switches, and wireless charging related products. Further, the company offers a portfolio of IoT systems and connectivity solutions, such as modules, gateways, routers, and connected services, including wireless connectivity and cloud-based services for industrial, medical, and communications applications. It serves original equipment manufacturers, solution providers, commercial applications, infrastructure, high-end consumer, and industrial end markets. It sells its products directly, as well as through independent sales representative firms and independent distributors. Semtech Corporation was incorporated in 1960 and is headquartered in Camarillo, California.'),
(67, 'TMHC', 'Taylor Morrison Home Corporatio', 64.150000, 0.680000, 1.0714, 426020, 6269061632, 7.7289, 72.500000, 51.900000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:25', 'US', 'Consumer Cyclical', 'Residential Construction', 63.700000, 63.470000, 64.510000, 62.960000, 1056513, 1.5900, 9.8157, 7.7289, 8.300000, NULL, NULL, 63.290000, 1.0136, 97725037, 97101551, 5.2300, NULL, 'https://www.taylormorrison.com', 'Taylor Morrison Home Corporation, together with its subsidiaries, operates as a land developer and homebuilder in the United States. It designs, builds, and sells single and multi-family detached and attached homes; and develops lifestyle and master-planned communities. The company also develops and constructs multi-use properties comprising commercial space, retail, and multi-family properties under the Urban Form brand name. In addition, it offers financial, title insurance, and closing settlement services. Further, the company engages in the build-to-rent homebuilding business under the Yardly brand name. It operates under the Taylor Morrison, Darling Homes Collection by Taylor Morrison, and Esplanade brand names in Arizona, California, Colorado, Florida, Georgia, Indiana, Nevada, North and South Carolina, Oregon, Texas, and Washington. Taylor Morrison Home Corporation was founded in 1936 and is headquartered in Scottsdale, Arizona.'),
(68, 'ALMS', 'Alumis Inc.', 24.170000, -0.170000, -0.6984, 2486009, 3013779200, NULL, 25.189800, 2.760000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:25', 'US', 'Healthcare', 'Biotechnology', 24.250000, 24.340000, 25.189800, 23.650000, 2637559, NULL, -7.6326, NULL, -2.150000, NULL, NULL, 3.687000, 6.5555, 117505995, 71584644, 3.6900, NULL, 'https://www.alumis.com', 'Alumis Inc., a clinical stage biopharmaceutical company, focuses on the development and commercialization of medicines for autoimmune disorders. The company\'s clinical asset comprises ESK-001, an allosteric tyrosine kinase 2 (TYK2) inhibitor for the treatment of plaque psoriasis and systemic lupus erythematosus; and A-005, a central nervous system-penetrant allosteric TYK2 inhibitor for neuroinflammatory and neurodegenerative diseases. It also develops interferon regulatory factor 5 (IRF5) to address immune dysfunction. The company was formerly known as Esker Therapeutics, Inc. and changed its name to Alumis Inc. in January 2022. The company was incorporated in 2021 and is headquartered in South San Francisco, California.'),
(69, 'FLY', 'Firefly Aerospace Inc.', 29.750000, -0.260000, -0.8664, 2249223, 4737720832, NULL, 73.800000, 16.000000, 'USD', 'NGM', 'stock', '2026-01-16 02:44:26', 'US', 'Industrials', 'Aerospace & Defense', 31.470000, 30.010000, 30.880000, 28.920000, 2613518, NULL, -36.5614, NULL, -2.670000, NULL, NULL, 6.405000, 4.6448, 159251122, 76053558, 1.5600, NULL, 'https://www.fireflyspace.com', 'Firefly Aerospace Inc. operates as a space and defense technology company and provides mission solutions for national security, government, and commercial customers. The company offers integrated launch and space services technology that is committed to enabling launch, transit, and operations in space. It also provides Alpha, a responsive launch service; Eclipse, a medium-lift launch vehicle; Blue Ghost, a lunar delivery and operation service; Elytra, which offers space maneuverability and servicing; and Ocula, a lunar imaging service. The company was incorporated in 2017 and is headquartered in Cedar Park, Texas.'),
(70, 'TOL', 'Toll Brothers, Inc.', 149.040000, 4.120000, 2.8429, 1214350, 14364921856, 11.0482, 149.800000, 86.670000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:26', 'US', 'Consumer Cyclical', 'Residential Construction', 145.690000, 144.920000, 149.280000, 144.390000, 1184386, 1.4280, 10.4562, 11.0482, 13.490000, 0.6700, 1.000000, 87.246000, 1.7083, 95003000, 94251526, 2.8900, NULL, 'https://www.tollbrothers.com', 'Toll Brothers, Inc., together with its subsidiaries, designs, builds, markets, sells, and arranges finance for a range of detached and attached homes in luxury residential communities in the United States. It designs, builds, markets, and sells condominiums through Toll Brothers City Living. The company also develops a range of single-story living and first-floor primary bedroom suite home designs, as well as communities with recreational amenities, such as golf courses, marinas, pool complexes, country clubs, and fitness and recreation centers; and develops, operates, rents apartments and student housing communities. In addition, it provides various interior fit-out options, such as flooring, wall tile, plumbing, cabinets, fixtures, appliances, lighting, and home-automation and security technologies. Further, the company owns and operates architectural, engineering, mortgage, title, land development, insurance, smart home technology, landscaping, lumber distribution, house component assembly, and component manufacturing operations. It serves luxury first-time, move-up, empty-nester, active-adult, and second-home buyers. The company was founded in 1967 and is headquartered in Fort Washington, Pennsylvania.'),
(71, 'PHM', 'PulteGroup, Inc.', 132.870000, 2.140000, 1.6370, 1335794, 26214926336, 10.2602, 142.110000, 88.070000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:26', 'US', 'Consumer Cyclical', 'Residential Construction', 131.640000, 130.730000, 133.140000, 130.170000, 1950352, 1.3390, 12.3659, 10.2602, 12.950000, 0.7800, 1.040000, 65.717000, 2.0219, 194916877, 193258134, 3.7400, NULL, 'https://www.pultegroup.com', 'PulteGroup, Inc., through its subsidiaries, engages in the homebuilding business in the United States. It acquires and develops land primarily for residential purposes; and constructs housing on such land. The company also offers various home designs, including single-family detached, townhomes, condominiums, and duplexes under the Centex, Pulte Homes, Del Webb, DiVosta Homes, John Wieland Homes and Neighborhoods, and American West brand names. In addition, the company arranges financing through the origination of mortgage loans for homebuyers; sells the servicing rights for the originated loans; and provides title insurance policies, and examination and closing services to homebuyers. PulteGroup, Inc. was founded in 1950 and is headquartered in Atlanta, Georgia.'),
(72, 'WY', 'Weyerhaeuser Company', 26.800000, 0.179998, 0.6762, 6826881, 19336493056, 58.2609, 31.660000, 21.160000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:27', 'US', 'Real Estate', 'REIT - Specialty', 26.645000, 26.620000, 26.910000, 26.315000, 6733059, 1.0500, 114.0862, 58.2609, 0.460000, 3.1300, 0.840000, 13.093000, 2.0469, 720861000, 717624334, 2.5600, NULL, 'https://www.weyerhaeuser.com', 'Weyerhaeuser Company, one of the world\'s largest private owners of timberlands, began operations in 1900 and today owns or controls approximately 10.4 million acres of timberlands in the U.S., as well as additional public timberlands managed under long-term licenses in Canada. Weyerhaeuser has been a global leader in sustainability for more than a century and manages 100 percent of its timberlands on a fully sustainable basis in compliance with internationally recognized sustainable forestry standards. Weyerhaeuser is also one of the largest manufacturers of wood products in North America and operates additional business lines around product distribution, climate solutions, real estate, and energy and natural resources, among others. In 2024, the company generated $7.1 billion in net sales and employed approximately 9,400 people who serve customers worldwide. Operated as a real estate investment trust, Weyerhaeuser\'s common stock trades on the New York Stock Exchange under the symbol WY.'),
(73, 'LEN-B', 'Lennar Corporation', 110.940000, 1.210000, 1.1027, 37822, 28291979264, 13.9023, 137.390000, 94.090000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:27', 'US', 'Consumer Cyclical', 'Residential Construction', 110.350000, 109.730000, 110.940000, 108.460000, 60036, 1.4340, 6.8481, 13.9023, 7.980000, 1.8000, 2.000000, 87.015000, 1.2750, 31217013, 218089581, 4.1600, NULL, 'https://www.lennar.com', 'Lennar Corporation, together with its subsidiaries, operates as a homebuilder primarily under the Lennar brand in the United States. It operates through Homebuilding East, Homebuilding Central, Homebuilding Texas, Homebuilding West, Financial Services, Multifamily, and Lennar Other segments. The company\'s homebuilding operations include the construction and sale of single-family attached and detached homes, as well as the purchase, development, and sale of residential land; and development, construction, and management of multifamily rental properties. It also offers residential mortgage financing, title, insurance, and closing services for home buyers and others, as well as originates and sells securitization commercial mortgage loans. In addition, the company is involved in the fund investment activity. It primarily serves first-time, move-up, active adult, and luxury homebuyers. The company was founded in 1954 and is based in Miami, Florida.'),
(74, 'SSL', 'Sasol Ltd.', 7.150000, -0.290000, -3.8979, 668635, 4558394368, 11.1719, 7.540000, 2.780000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:27', 'US', 'Basic Materials', 'Specialty Chemicals', 7.170000, 7.440000, 7.185000, 7.090000, 1032768, 0.1750, 4.5602, 11.1719, 0.640000, NULL, NULL, 14.395620, 0.4967, 631206335, 588056825, 4.5400, NULL, 'https://www.sasol.com', 'Sasol Limited operates as a chemical and energy company. It offers bitumen, industrial heating fuels, naphtha, lubricants and lubricant base oils, liquefied petroleum gas, automotive and industrial lubricants, greases, cleansers and degreasers, automotive fuels, and burner fuels or domestic, as well as illuminating paraffin transport fuels, such as petrol, diesel, and jet fuels. The company also provides methane rich and natural gas. In addition, it offers ammonium nitrate, limestone ammonium nitrate, and nitric acid for agriculture; industrial foaming agents, wax/hydrophobic coatings and industrial pegs, dispersible hydrates, boehmites, and aluminum oxides for building and construction; short-chain alcohols for flavors and fragrances; liquids, flakes, powders, and polyethylene glycols for health and wellness; caustic soda, hydrochloric acid CP Grade, and calcium chloride for industrial and institutional cleaning; alumina-based catalyst, cobalt FT catalysts, and mixed metal oxides for inorganic materials and catalysts; chemical feedstocks, process solvents, and chemicals for manufacturing and industrial; viscosity modifiers, chemical carriers, and adsorbents for mining, oil, and gas; hydrocarbons, surfactants, polyether, and polyglycols for paper and water; surfactants, dyes, finishing agents, tanning agents, and emulsifiers for textile and leather; and other chemicals for automotive and transportation, consumer goods, home care, packaging, printing, coatings, personal care, and polymers sectors. Further, it is involved in engineering services, research and development, and technology transfer; management of cash resources, investments, and procurement of loans; develop and implement international gas to liquid and CTL ventures; marketing of fuels and lubricants; trading and transportation of oil products, petrochemicals and chemical products, and derivatives; and coal mining activities. Sasol Limited was founded in 1950 and is based in Johannesburg, South Africa.'),
(75, 'LB', 'LandBridge Company LLC', 59.760000, 1.480000, 2.5395, 368583, 4756244992, 67.9091, 87.597000, 43.750000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:28', 'US', 'Energy', 'Oil & Gas Equipment & Services', 58.440000, 58.280000, 60.075000, 56.610100, 452785, NULL, 23.7054, 67.9091, 0.880000, 0.6700, 0.400000, 10.735000, 5.5668, 27838199, 25191744, 9.0500, NULL, 'https://www.landbridgeco.com', 'LandBridge Company LLC, together with its subsidiaries, owns and manages land and resources to support and enhance oil and natural gas development in the United States. It owns surface acres in and around the Delaware Basin in Texas and New Mexico. The company holds a portfolio of oil and gas royalties. It sells brackish water and other surface composite materials. The company was founded in 2021 and is based in Houston, Texas. LandBridge Company LLC operates as a subsidiary of LandBridge Holdings LLC.'),
(76, 'MIR', 'Mirion Technologies, Inc.', 27.000000, 0.750000, 2.8571, 2240075, 6597995520, 245.4545, 30.277000, 12.000000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:28', 'US', 'Industrials', 'Specialty Industrial Machinery', 26.860000, 26.250000, 27.400000, 26.575000, 3320316, 0.9550, 42.8571, 245.4545, 0.110000, NULL, NULL, 8.161000, 3.3084, 244370206, 211639284, 9.2400, NULL, 'https://www.mirion.com', 'Mirion Technologies, Inc. provides radiation detection, measurement, analysis, and monitoring products and services in North America, Europe, and the Asia Pacific. It operates in two segments, Medical, and Nuclear & Safety. The Medical segment offers radiation oncology quality assurance and dosimetry solutions; patient safety solutions for diagnostic imaging and radiation therapy centers; radiation therapy quality assurance solutions for calibrating and verifying imaging and treatment accuracy; and radionuclide therapy products for nuclear medicine applications, such as product handling, medical imaging furniture, and rehabilitation products. This segment improves the quality and safety of cancer care delivery; and supports applications across medical diagnostics and practitioner safety. The Nuclear & Safety segment focuses on addressing critical radiation safety, measurement, and analysis applications; and provides personal radiation detection, identification equipment, and analysis tools. The company\'s products and solutions also include radiation measurement and monitoring solutions, reactor instrumentation and control detectors, imaging systems and cameras, and waste management systems; laboratory and scientific analysis systems comprising gamma/alpha spectroscopy, alpha/beta counting, specialty detectors, and spectroscopy software; radiation measurement and health physics instrumentation; and contamination and clearance monitors. It serves hospitals, clinics and urgent care facilities, dental and veterinary offices, radiation treatment facilities, OEMs for radiation therapy, laboratories, military organizations, government agencies, industrial companies, power and utility companies, reactor design firms, and NPPs. The company was formerly known as Global Monitoring Systems, Inc. and changed its name to Mirion Technologies, Inc. in January 2006. Mirion Technologies, Inc. was incorporated in 2005 and is headquartered in Atlanta, Georgia.'),
(77, 'LEU', 'Centrus Energy Corp.', 306.100000, -1.470000, -0.4779, 1005074, 5574703104, 47.6050, 464.250000, 49.400000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:28', 'US', 'Energy', 'Uranium', 314.240000, 307.570000, 272.701000, 246.110100, 1143732, 1.2520, 62.2715, 47.6050, 6.430000, NULL, NULL, 19.937000, 15.3534, 17492832, 16839027, 4.9300, NULL, 'https://www.centrusenergy.com', 'Centrus Energy Corp. supplies nuclear fuel components for the nuclear power industry in the United States, Belgium, Japan, the Netherlands, and internationally. The company operates in two segments, Low-Enriched Uranium (LEU) and Technical Solutions. The LEU segment sells separative work units (SWU) components of LEU; natural uranium hexafluoride, uranium concentrates, and uranium conversion; and enriched uranium products to utilities that operate nuclear power plants. The Technical Solutions segment offers technical, manufacturing, engineering, and operations services to public and private sector customers. The company was formerly known as USEC Inc. and changed its name to Centrus Energy Corp. in September 2014. Centrus Energy Corp. was incorporated in 1998 and is headquartered in Bethesda, Maryland.'),
(78, 'KBH', 'KB Home', 62.240000, 0.610001, 0.9898, 639972, 3933568000, 10.1203, 70.470000, 48.900000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:29', 'US', 'Consumer Cyclical', 'Residential Construction', 61.840000, 61.630000, 62.560000, 61.260000, 1150678, 1.4330, 11.3644, 10.1203, 6.150000, 1.6100, 1.000000, 61.722000, 1.0084, 63200000, 60596792, 4.0200, NULL, 'https://www.kbhome.com', 'KB Home operates as a homebuilding company in the United States. The company operates through four segments: West Coast, Southwest, Central, and Southeast. It builds and sells a variety of homes, including attached and detached single-family residential homes, townhomes, and condominiums primarily for first-time, first move-up, second move-up, and active adult homebuyers. The company also provides financial services, such as mortgage banking services comprising residential consumer mortgage loan originations to homebuyers; property and casualty insurance services, as well as earthquake, flood, and personal property insurance products to homebuyers; and title services. It conducts operations in Arizona, California, Colorado, Florida, Idaho, Nevada, North Carolina, Texas, and Washington. The company was formerly known as Kaufman and Broad Home Corporation and changed its name to KB Home in January 2001. KB Home was founded in 1957 and is based in Los Angeles, California.'),
(79, 'AMAT', 'Applied Materials, Inc.', 319.080000, 17.190000, 5.6941, 11224925, 254192664576, 36.8453, 330.999900, 123.740000, 'USD', 'NMS', 'stock', '2026-01-16 02:44:29', 'US', 'Technology', 'Semiconductor Equipment & Materials', 327.360000, 301.890000, 330.999900, 318.830000, 7170339, 1.6710, 27.0408, 36.8453, 8.660000, 0.6100, 1.840000, 25.744000, 12.3943, 792943366, 789398909, 2.2100, NULL, 'https://www.appliedmaterials.com', 'Applied Materials, Inc. provides materials engineering solutions, equipment, services, and software to the semiconductor and related industries in the United States, China, Korea, Taiwan, Japan, Southeast Asia, Europe, and internationally. The company operates through Semiconductor Systems and Applied Global Services (AGS) segments. The Semiconductor Systems segment includes semiconductor capital equipment to enable materials engineering steps, including etch, rapid thermal processing, deposition, chemical mechanical planarization, metrology and inspection, wafer packaging, and ion implantation. The AGS segment offers integrated solutions to optimize equipment and fab performance and productivity comprising spares, upgrades, services, and 200 millimeter and other equipment and factory automation software for semiconductor and other products. It serves manufacturers of semiconductor wafers and chips, and other electronic devices. Applied Materials, Inc. was incorporated in 1967 and is headquartered in Santa Clara, California.'),
(80, 'TPB', 'Turning Point Brands, Inc.', 118.010000, 2.670010, 2.3149, 275340, 2250540032, 36.4228, 118.615000, 51.481000, 'USD', 'NYQ', 'stock', '2026-01-16 02:44:29', 'US', 'Consumer Defensive', 'Tobacco', 114.920000, 115.340000, 118.615000, 114.600000, 377931, 0.8660, 28.5969, 36.4228, 3.240000, 0.2600, 0.300000, 18.035000, 6.5434, 19070757, 16014096, 3.2000, NULL, 'https://www.turningpointbrands.com', 'Turning Point Brands, Inc., together with its subsidiaries, manufactures, markets, and distributes branded consumer products in the United States and Canada. It operates through two segments, Zig-Zag Products and Stoker\'s Products. The Zig-Zag Products segment markets and distributes rolling papers, tubes, finished cigars, make-your-own cigar wraps, and related products, as well as lighters and other accessories under the Zig-Zag brand. The Stoker\'s Products segment manufactures and markets moist snuff tobacco and loose-leaf chewing tobacco products under the Stoker\'s, FRE, Beech-Nut, Durango, Trophy, and Wind River brands. In addition, it markets and distributes cannabis accessories and tobacco products. The company sells its products to wholesale distributors and retail merchants in the independent and chain convenience stores, tobacco outlets, food stores, mass merchandising, drug store, and non-traditional retail channels. The company was formerly known as North Atlantic Holding Company, Inc. and changed its name to Turning Point Brands, Inc. in November 2015. Turning Point Brands, Inc. was founded in 1988 and is headquartered in Louisville, Kentucky.'),
(81, 'BTC-USD', 'Bitcoin USD', 95503.470000, -872.351560, -0.9052, 50693742592, 1907816005632, NULL, 126198.070000, 74436.680000, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:01', 'GLOBAL', NULL, NULL, 95562.780000, 95562.780000, 95754.164000, 95416.260000, 56187967589, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(82, 'ETH-USD', 'Ethereum USD', 3301.007800, -19.142334, -0.5765, 26530695168, 398413856768, NULL, 4953.733000, 1386.799300, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:01', 'GLOBAL', NULL, NULL, 3317.557400, 3317.557400, 3324.831800, 3297.515900, 27789237892, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(83, 'BNB-USD', 'BNB USD', 930.829800, -6.337341, -0.6762, 2240146944, 126929141760, NULL, 1370.546000, 509.835700, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:02', 'GLOBAL', NULL, NULL, 930.897900, 930.897900, 933.257750, 929.657040, 2711210788, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(84, 'XRP-USD', 'XRP USD', 2.069156, -0.043825, -2.0741, 2872346368, 125595869184, NULL, 3.650210, 1.528451, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:02', 'GLOBAL', NULL, NULL, 2.078166, 2.078166, 2.084835, 2.068247, 3985738101, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(85, 'SOL-USD', 'Solana USD', 142.023000, -2.725235, -1.8827, 4365552640, 80288825344, NULL, 294.334960, 96.588066, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:03', 'GLOBAL', NULL, NULL, 142.333440, 142.333440, 142.658130, 141.859800, 5084554822, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(86, 'ADA-USD', 'Cardano USD', 0.391983, -0.015095, -3.7081, 673774144, 14096128000, NULL, 1.163675, 0.330370, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:03', 'GLOBAL', NULL, NULL, 0.393492, 0.393492, 0.393883, 0.390240, 791159852, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(87, 'DOGE-USD', 'Dogecoin USD', 0.139702, -0.004493, -3.1162, 1457079808, 23516755968, NULL, 0.433512, 0.114784, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:03', 'GLOBAL', NULL, NULL, 0.139997, 0.139997, 0.140284, 0.139276, 1679456104, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(88, 'AVAX-USD', 'Avalanche USD', 13.805890, -0.593436, -4.1213, 384250560, 5947165696, NULL, 41.795708, 10.638627, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:03', 'GLOBAL', NULL, NULL, 13.819229, 13.819229, 13.848261, 13.716839, 426429578, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(89, 'DOT-USD', 'Polkadot USD', 2.121583, -0.085684, -3.8819, 158348368, 3512402432, NULL, 7.591953, 1.410394, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:04', 'GLOBAL', NULL, NULL, 2.117067, 2.117067, 2.122201, 2.106217, 219800184, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(90, 'MATIC-USD', 'Polygon USD', 0.218236, 0.005909, 2.7830, 1267171, 0, NULL, 1.083047, 0.196799, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:04', 'GLOBAL', NULL, NULL, 0.212760, 0.212760, 0.218261, 0.210346, 6834226, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(91, 'SHIB-USD', 'Shiba Inu USD', 0.000008, 0.000000, -2.7248, 108374992, 4964712448, NULL, 0.000025, 0.000007, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:04', 'GLOBAL', NULL, NULL, 0.000008, 0.000008, 0.000008, 0.000008, 146829287, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(92, 'LTC-USD', 'Litecoin USD', 72.253555, -3.575302, -4.7150, 1021647488, 5544884736, NULL, 140.616790, 63.751860, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:04', 'GLOBAL', NULL, NULL, 72.127020, 72.127020, 72.336810, 71.639960, 609828238, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(93, 'TRX-USD', 'TRON USD', 0.310989, 0.005757, 1.8861, 826328896, 29452347392, NULL, 0.369787, 0.204147, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:05', 'GLOBAL', NULL, NULL, 0.312041, 0.312041, 0.312198, 0.310902, 688938628, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(94, 'ATOM-USD', 'Cosmos USD', 2.470041, -0.100154, -3.8968, 56601044, 1205725312, NULL, 7.160012, 1.835402, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:05', 'GLOBAL', NULL, NULL, 2.475757, 2.475757, 2.481960, 2.453128, 84507736, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(95, 'LINK-USD', 'Chainlink USD', 13.728634, -0.232428, -1.6648, 527691392, 9721245696, NULL, 27.735258, 10.179260, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:05', 'GLOBAL', NULL, NULL, 13.785211, 13.785211, 13.856090, 13.690852, 681267100, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(96, 'UNI-USD', 'UNICORN Token USD', 0.000163, 0.000000, 0.0000, 3, 17388, NULL, 0.001590, 0.000099, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:06', 'GLOBAL', NULL, NULL, 0.000163, 0.000163, 0.000163, 0.000163, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(97, 'XLM-USD', 'Stellar USD', 0.227737, -0.005211, -2.2368, 172472320, 7382379520, NULL, 0.519372, 0.197770, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:06', 'GLOBAL', NULL, NULL, 0.228301, 0.228301, 0.228743, 0.226778, 199832014, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(98, 'BCH-USD', 'Bitcoin Cash USD', 590.897000, -8.199890, -1.3687, 1032907520, 11806956544, NULL, 668.063300, 250.792570, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:06', 'GLOBAL', NULL, NULL, 592.110200, 592.110200, 593.371770, 590.121100, 471328759, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(99, 'ETC-USD', 'Ethereum Classic USD', 12.645361, -0.392643, -3.0115, 72104048, 1961815936, NULL, 29.180513, 10.236784, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:06', 'GLOBAL', NULL, NULL, 12.639289, 12.639289, 12.653783, 12.582671, 97436613, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(100, 'FIL-USD', 'Filecoin USD', 1.540510, -0.064999, -4.0485, 191926304, 1136061056, NULL, 5.941113, 0.633614, 'USD', 'CCC', 'crypto', '2026-01-16 02:44:07', 'GLOBAL', NULL, NULL, 1.503995, 1.503995, 1.540510, 1.499156, 277172955, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(101, 'AAPL', 'Apple Inc.', 473.220000, 4.050000, 0.8600, 24801102, 415177369264, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(102, 'GOOGL', 'Alphabet Inc.', 106.050000, 1.950000, 1.8400, 12860908, 2090659029777, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(103, 'MSFT', 'Microsoft Corporation', 316.090000, -0.280000, -0.0900, 22863636, 2024101004730, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(104, 'META', 'Meta Platforms Inc.', 204.720000, 4.160000, 2.0300, 47986511, 2210143092750, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(105, 'NVDA', 'NVIDIA Corporation', 339.110000, -3.630000, -1.0700, 47510052, 24901471249, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(106, 'TSLA', 'Tesla Inc.', 226.760000, -1.140000, -0.5000, 1557719, 1886279648047, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(107, 'AMZN', 'Amazon.com Inc.', 476.220000, -1.840000, -0.3900, 39639226, 722592923109, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(108, 'NFLX', 'Netflix Inc.', 97.920000, 0.520000, 0.5300, 2498614, 2729438624516, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(109, 'JPM', 'JPMorgan Chase & Co.', 359.780000, 5.570000, 1.5500, 43898059, 472241843369, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(110, 'BAC', 'Bank of America Corp.', 155.560000, -1.990000, -1.2800, 29500269, 356935893097, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(111, 'GS', 'Goldman Sachs Group', 264.380000, 5.910000, 2.2300, 2327649, 2229981956469, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(112, 'V', 'Visa Inc.', 462.860000, -3.620000, -0.7800, 22689426, 1171920030451, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(113, 'MA', 'Mastercard Inc.', 320.380000, -2.290000, -0.7200, 47402044, 1707132293919, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(114, 'JNJ', 'Johnson & Johnson', 282.140000, -0.880000, -0.3100, 25639334, 842467588389, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(115, 'PFE', 'Pfizer Inc.', 386.430000, -1.810000, -0.4700, 3773586, 203172434146, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `market_data` (`id`, `symbol`, `name`, `price`, `change`, `change_percent`, `volume`, `market_cap`, `pe_ratio`, `52_week_high`, `52_week_low`, `currency`, `exchange`, `asset_type`, `last_updated`, `country_code`, `sector`, `industry`, `open_price`, `previous_close`, `day_high`, `day_low`, `avg_volume`, `beta`, `forward_pe`, `trailing_pe`, `eps`, `dividend_yield`, `dividend_rate`, `book_value`, `price_to_book`, `shares_outstanding`, `float_shares`, `short_ratio`, `logo_url`, `website`, `description`) VALUES
(116, 'UNH', 'UnitedHealth Group', 446.380000, -2.680000, -0.6000, 18971305, 1321468343302, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(117, 'XOM', 'Exxon Mobil Corp.', 128.820000, 6.590000, 5.1200, 34877546, 2325034950946, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(118, 'CVX', 'Chevron Corporation', 299.910000, 7.710000, 2.5700, 33780539, 24289006405, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(119, 'WMT', 'Walmart Inc.', 227.660000, 1.380000, 0.6100, 31857042, 267345382261, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(120, 'KO', 'Coca-Cola Company', 59.150000, 0.440000, 0.7400, 11161767, 1300236733065, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(121, 'PEP', 'PepsiCo Inc.', 344.550000, -0.410000, -0.1200, 25617761, 1536168737735, NULL, NULL, NULL, 'USD', 'NASDAQ', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(122, 'MCD', 'McDonald\'s Corp.', 94.200000, -0.300000, -0.3100, 44554918, 2135311151322, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(123, 'BA', 'Boeing Company', 192.520000, 3.930000, 2.0400, 13321224, 2719231669761, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(124, 'CAT', 'Caterpillar Inc.', 424.940000, 0.550000, 0.1300, 10430313, 2914466270955, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(125, 'DIS', 'Walt Disney Company', 218.800000, -2.810000, -1.2800, 8151032, 1049073374082, NULL, NULL, NULL, 'USD', 'NYSE', 'stock', '2026-01-14 22:01:54', 'NP', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `market_indices`
--

CREATE TABLE `market_indices` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `price` decimal(15,4) DEFAULT NULL,
  `change_amount` decimal(15,4) DEFAULT NULL,
  `change_percent` decimal(10,4) DEFAULT NULL,
  `previous_close` decimal(15,4) DEFAULT NULL,
  `day_high` decimal(15,4) DEFAULT NULL,
  `day_low` decimal(15,4) DEFAULT NULL,
  `year_high` decimal(15,4) DEFAULT NULL,
  `year_low` decimal(15,4) DEFAULT NULL,
  `market_status` enum('pre-market','open','after-hours','closed') DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `market_indices`
--

INSERT INTO `market_indices` (`id`, `symbol`, `name`, `price`, `change_amount`, `change_percent`, `previous_close`, `day_high`, `day_low`, `year_high`, `year_low`, `market_status`, `country_code`, `last_updated`, `created_at`) VALUES
(1, '^GSPC', 'S&P 500', 6944.4700, 17.8701, 0.2580, 6926.6000, 6979.3400, 6937.9300, 6986.3300, 4835.0400, 'closed', 'US', '2026-01-16 02:44:01', '2026-01-07 11:48:09'),
(2, '^DJI', 'Dow Jones Industrial Average', 49442.4400, 292.8125, 0.5958, 49149.6300, 49581.1800, 49201.1000, 49633.3500, 36611.7800, 'closed', 'US', '2026-01-16 02:44:02', '2026-01-07 11:48:09'),
(3, '^IXIC', 'NASDAQ Composite', 23530.0210, 58.2715, 0.2483, 23471.7500, 23721.1070, 23502.1760, 24019.9900, 14784.0300, 'closed', 'US', '2026-01-16 02:44:02', '2026-01-07 11:48:09'),
(4, '^RUT', 'Russell 2000', 2674.5570, 22.9194, 0.8644, 2651.6375, 2689.2766, 2659.2874, 2689.2766, 1732.9900, 'closed', 'US', '2026-01-16 02:44:03', '2026-01-07 11:48:09'),
(5, '^VIX', 'CBOE Volatility Index', 15.8400, -0.9100, -5.4328, 16.7500, 16.5400, 15.3000, 60.1300, 13.3800, 'closed', 'US', '2026-01-16 02:44:03', '2026-01-07 11:48:09'),
(6, '^NDX', 'NASDAQ-100', 25547.0740, 81.1309, 0.3186, 25465.9430, 25781.0310, 25520.1970, 26182.1000, 16542.2000, 'closed', 'US', '2026-01-16 02:44:03', '2026-01-07 11:48:09'),
(47, '^NYA', 'NYSE Composite Index', 22808.8140, 87.5879, 0.3855, 22721.2270, 0.0000, 0.0000, 22750.8800, 0.0000, 'closed', 'US', '2026-01-16 02:44:03', '2026-01-16 02:04:04'),
(48, '^FTSE', 'FTSE 100', 10238.9400, 54.5908, 0.5360, 10184.3500, 10250.4500, 10173.5300, 10250.4500, 7544.8000, 'closed', 'US', '2026-01-16 02:44:04', '2026-01-16 02:04:05'),
(49, '^GDAXI', 'DAX                           P', 25352.3900, 66.1504, 0.2616, 25286.2400, 25378.5500, 25233.3200, 25507.7900, 18489.9100, 'closed', 'US', '2026-01-16 02:44:04', '2026-01-16 02:04:05'),
(50, '^FCHI', 'CAC 40', 8313.1200, -17.8398, -0.2141, 8330.9600, 0.0000, 0.0000, 8396.7200, 0.0000, 'closed', 'US', '2026-01-16 02:44:04', '2026-01-16 02:04:06'),
(51, '^STOXX50E', 'EURO STOXX 50                 I', 6041.1400, 36.0903, 0.6010, 6005.0500, 0.0000, 0.0000, 6052.8600, 0.0000, 'closed', 'US', '2026-01-16 02:44:04', '2026-01-16 02:04:06'),
(52, '^IBEX', 'IBEX 35', 17642.7000, -53.0000, -0.2995, 17695.7000, 17725.7000, 17611.7000, 17833.5000, 11583.0000, 'closed', 'US', '2026-01-16 02:44:05', '2026-01-16 02:04:07'),
(53, '^N225', 'Nikkei 225', 53869.4400, -241.0586, -0.4455, 54110.5000, 54130.6000, 53706.7900, 54487.3200, 30792.7400, 'closed', 'US', '2026-01-16 02:44:05', '2026-01-16 02:04:07'),
(54, '^HSI', 'HANG SENG INDEX', 26898.6700, -24.9492, -0.0927, 26923.6200, 27176.3100, 26877.7900, 27381.8400, 19260.2100, 'closed', 'US', '2026-01-16 02:44:05', '2026-01-16 02:04:07'),
(55, '000001.SS', 'SSE Composite Index', 4106.8994, -5.7017, -0.1386, 4112.6010, 4140.2250, 4100.6484, 4190.8660, 3040.6930, 'closed', 'GLOBAL', '2026-01-16 02:44:05', '2026-01-16 02:04:08'),
(56, '^KS11', 'KOSPI Composite Index', 4845.9600, 48.4102, 1.0091, 4797.5500, 4852.0000, 4797.7500, 4852.0000, 2284.7200, 'closed', 'US', '2026-01-16 02:44:06', '2026-01-16 02:04:08'),
(57, '^TWII', 'TSEC CAPITALIZATION WEIGHTED ST', 31268.2900, 457.7090, 1.4874, 30810.5800, 31339.3900, 30844.6300, 31339.3900, 17306.9700, 'closed', 'US', '2026-01-16 02:44:06', '2026-01-16 02:04:08'),
(58, '^BSESN', 'S&P BSE SENSEX', 83382.7100, -244.9766, -0.2929, 83627.6900, 83809.9800, 83185.2000, 86159.0200, 71425.0100, 'closed', 'US', '2026-01-16 02:44:06', '2026-01-16 02:04:09'),
(59, '^NSEI', 'NIFTY 50', 25665.6000, -66.7012, -0.2592, 25732.3000, 25791.7500, 25603.9500, 26373.2000, 21743.6500, 'closed', 'US', '2026-01-16 02:44:07', '2026-01-16 02:04:09'),
(60, '^GSPTSE', 'S&P/TSX Composite index', 33028.9200, 112.4531, 0.3416, 32916.4700, 33099.2800, 32876.3900, 33099.2800, 22227.7000, 'closed', 'US', '2026-01-16 02:44:07', '2026-01-16 02:04:09'),
(61, '^AXJO', 'S&P/ASX 200 [XJO]', 8895.5000, 33.7998, 0.3815, 8861.7000, 8895.5000, 8855.6000, 9115.2000, 7169.2000, 'closed', 'US', '2026-01-16 02:44:07', '2026-01-16 02:04:09');

-- --------------------------------------------------------

--
-- Table structure for table `market_sentiment`
--

CREATE TABLE `market_sentiment` (
  `id` int(11) NOT NULL,
  `indicator_type` enum('fear_greed','vix','put_call_ratio','other') DEFAULT NULL,
  `value` decimal(10,2) NOT NULL,
  `classification` varchar(50) DEFAULT NULL,
  `previous_close` decimal(10,2) DEFAULT NULL,
  `previous_week` decimal(10,2) DEFAULT NULL,
  `previous_month` decimal(10,2) DEFAULT NULL,
  `previous_year` decimal(10,2) DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `navigation_items`
--

CREATE TABLE `navigation_items` (
  `id` int(11) NOT NULL,
  `label` varchar(100) NOT NULL,
  `url` varchar(255) DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `position` varchar(50) DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `requires_auth` tinyint(1) DEFAULT NULL,
  `roles_allowed` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`roles_allowed`)),
  `country_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `nav_metrics`
--

CREATE TABLE `nav_metrics` (
  `id` int(11) NOT NULL,
  `page` varchar(255) DEFAULT NULL,
  `views` int(11) DEFAULT NULL,
  `unique_views` int(11) DEFAULT NULL,
  `avg_time_seconds` int(11) DEFAULT NULL,
  `bounce_rate` decimal(5,2) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `news_items`
--

CREATE TABLE `news_items` (
  `id` int(11) NOT NULL,
  `source` varchar(50) DEFAULT NULL,
  `source_url` text DEFAULT NULL,
  `canonical_url` text DEFAULT NULL,
  `title` text NOT NULL,
  `summary` text DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `raw` text DEFAULT NULL,
  `hash` varchar(64) DEFAULT NULL,
  `simhash` varchar(32) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `processed_at` datetime DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `retry_count` int(11) DEFAULT NULL,
  `image` text DEFAULT NULL,
  `featured` tinyint(1) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `curated_status` varchar(20) DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `source_type` varchar(20) DEFAULT NULL,
  `full_content` text DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `meta_description` varchar(500) DEFAULT NULL,
  `country_code` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `news_items`
--

INSERT INTO `news_items` (`id`, `source`, `source_url`, `canonical_url`, `title`, `summary`, `published_at`, `raw`, `hash`, `simhash`, `status`, `created_at`, `processed_at`, `error_message`, `retry_count`, `image`, `featured`, `category`, `curated_status`, `updated_at`, `source_type`, `full_content`, `author`, `slug`, `meta_description`, `country_code`) VALUES
(1, 'Bloomberg', NULL, NULL, 'Fed Signals Potential Rate Cuts in 2024 Amid Cooling Inflation Data', 'Federal Reserve officials hint at possible interest rate reductions as inflation shows signs of cooling. Markets respond positively to dovish signals.', '2026-01-07 05:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600', 1, 'business', 'published', NULL, 'admin', NULL, NULL, 'fed-signals-rate-cuts-2024', NULL, 'US'),
(2, 'Financial Times', NULL, NULL, 'Major Merger Announced Between Tech Giants Worth $50 Billion', 'Two leading technology companies announce historic merger deal, reshaping the industry landscape.', '2026-01-04 18:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600', 0, 'business', 'published', NULL, 'admin', NULL, NULL, 'tech-giants-merger-50b', NULL, 'US'),
(3, 'CNBC', NULL, NULL, 'Q4 Earnings Season Kicks Off With Strong Corporate Results', 'Early reports show companies exceeding analyst expectations across multiple sectors.', '2026-01-06 09:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=600', 0, 'business', 'published', NULL, 'admin', NULL, NULL, 'q4-earnings-strong-results', NULL, 'US'),
(4, 'CNBC', NULL, NULL, 'Tech Stocks Rally on Strong Q4 Earnings Reports', 'Major technology companies exceed earnings expectations, driving market gains. NASDAQ reaches new highs.', '2026-01-04 17:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600', 1, 'markets', 'published', NULL, 'admin', NULL, NULL, 'tech-stocks-rally-q4', NULL, 'US'),
(5, 'CoinDesk', NULL, NULL, 'Bitcoin Surges Past $90,000 on ETF Momentum', 'Cryptocurrency markets rally as institutional adoption continues to grow with new ETF approvals.', '2026-01-07 10:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=800&h=600', 0, 'markets', 'published', NULL, 'admin', NULL, NULL, 'bitcoin-surges-90k-etf', NULL, 'US'),
(6, 'Wall Street Journal', NULL, NULL, 'S&P 500 Hits Record High as Investors Eye Rate Cuts', 'Stock market reaches new all-time highs as optimism grows about monetary policy easing.', '2026-01-06 07:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=600', 0, 'markets', 'published', NULL, 'admin', NULL, NULL, 'sp500-record-high-rate-cuts', NULL, 'US'),
(7, 'TechCrunch', NULL, NULL, 'NVIDIA Announces Next-Gen AI Chips at CES', 'Chip giant reveals breakthrough GPU architecture for AI applications, promising 10x performance gains.', '2026-01-07 11:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=600', 1, 'technology', 'published', NULL, 'admin', NULL, NULL, 'nvidia-next-gen-ai-chips-ces', NULL, 'US'),
(8, 'MIT Technology Review', NULL, NULL, 'AI Breakthrough: New Language Models Show Human-Level Reasoning', 'Latest research demonstrates significant advances in artificial intelligence reasoning capabilities.', '2026-01-05 16:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600', 0, 'technology', 'published', NULL, 'admin', NULL, NULL, 'ai-breakthrough-human-reasoning', NULL, 'US'),
(9, 'Gartner', NULL, NULL, 'Cloud Computing Market Expected to Reach $1 Trillion by 2028', 'Industry analysts project continued strong growth in cloud infrastructure spending.', '2026-01-04 20:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&h=600', 0, 'technology', 'published', NULL, 'admin', NULL, NULL, 'cloud-computing-trillion-2028', NULL, 'US'),
(10, 'Reuters', NULL, NULL, 'Global Trade Tensions Ease as New Agreements Signed', 'Major economies reach new trade deals, reducing tariff concerns and boosting market confidence.', '2026-01-07 10:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&h=600', 1, 'world', 'published', NULL, 'admin', NULL, NULL, 'global-trade-tensions-ease', NULL, 'US'),
(11, 'Financial Times', NULL, NULL, 'European Central Bank Maintains Steady Interest Rates', 'ECB holds rates unchanged while signaling cautious approach to monetary policy.', '2026-01-05 04:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1569025743873-ea3a9ber5f1c?w=800&h=600', 0, 'world', 'published', NULL, 'admin', NULL, NULL, 'ecb-steady-interest-rates', NULL, 'US'),
(12, 'Reuters', NULL, NULL, 'Oil Prices Surge Amid Middle East Tensions', 'Crude oil prices rise sharply as geopolitical concerns affect global supply outlook.', '2026-01-06 10:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1513828583688-c52646db42da?w=800&h=600', 1, 'energy', 'published', NULL, 'admin', NULL, NULL, 'oil-prices-surge-middle-east', NULL, 'US'),
(13, 'Bloomberg Green', NULL, NULL, 'Renewable Energy Investment Hits Record $500 Billion', 'Global investment in solar and wind power reaches new highs as clean energy transition accelerates.', '2026-01-06 10:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&h=600', 0, 'energy', 'published', NULL, 'admin', NULL, NULL, 'renewable-energy-record-500b', NULL, 'US'),
(14, 'Electrek', NULL, NULL, 'Electric Vehicle Sales Double Year Over Year', 'EV adoption accelerates globally as prices fall and charging infrastructure expands.', '2026-01-07 08:33:09', NULL, NULL, NULL, 'queued', '2026-01-07 11:48:09', NULL, NULL, 0, 'https://images.unsplash.com/photo-1593941707882-a5bba14938c7?w=800&h=600', 0, 'energy', 'published', NULL, 'admin', NULL, NULL, 'ev-sales-double-yoy', NULL, 'US'),
(15, 'The Kathmandu Post', NULL, NULL, 'Nepal Rastra Bank Issues New Monetary Policy Guidelines', 'The central bank of Nepal announces updates to its monetary policy to stabilize the economy.', '2026-01-14 23:42:04', NULL, NULL, NULL, 'queued', '2026-01-14 21:57:04', NULL, NULL, 0, NULL, 1, 'business', 'published', NULL, 'admin', NULL, NULL, 'nrb-monetary-policy-2024', NULL, 'NP'),
(16, 'The Economic Times', NULL, NULL, 'India Becomes Third Largest Economy in Terms of Purchasing Power', 'India continues its rapid economic growth, reaching a new milestone in global rankings.', '2026-01-13 12:42:04', NULL, NULL, NULL, 'queued', '2026-01-14 21:57:04', NULL, NULL, 0, NULL, 1, 'business', 'published', NULL, 'admin', NULL, NULL, 'india-economy-milestone', NULL, 'IN'),
(17, 'MyRepublica', NULL, NULL, 'Kathmandu Stock Exchange (NEPSE) Hits All-Time High', 'Investors cheer as the Nepalese stock market reaches new heights.', '2026-01-14 17:42:05', NULL, NULL, NULL, 'queued', '2026-01-14 21:57:05', NULL, NULL, 0, NULL, 1, 'markets', 'published', NULL, 'admin', NULL, NULL, 'nepse-all-time-high', NULL, 'NP');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `order_number` varchar(50) DEFAULT NULL,
  `status` enum('pending','confirmed','shipped','delivered','cancelled') DEFAULT NULL,
  `total_amount` decimal(18,2) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `shipping_address` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`shipping_address`)),
  `billing_address` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`billing_address`)),
  `notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `order_items`
--

CREATE TABLE `order_items` (
  `id` int(11) NOT NULL,
  `order_id` varchar(255) NOT NULL,
  `product_id` varchar(255) DEFAULT NULL,
  `product_name` varchar(255) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `unit_price` decimal(18,2) DEFAULT NULL,
  `total_price` decimal(18,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `pages`
--

CREATE TABLE `pages` (
  `id` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `meta_title` varchar(255) DEFAULT NULL,
  `meta_description` text DEFAULT NULL,
  `template` varchar(100) DEFAULT NULL,
  `status` enum('draft','published') DEFAULT NULL,
  `is_homepage` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `paper_holdings`
--

CREATE TABLE `paper_holdings` (
  `id` varchar(255) NOT NULL,
  `account_id` varchar(255) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `shares` decimal(18,8) NOT NULL,
  `avg_price` decimal(18,4) DEFAULT NULL,
  `current_price` decimal(18,4) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `paper_trading_accounts`
--

CREATE TABLE `paper_trading_accounts` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `initial_balance` decimal(18,2) DEFAULT NULL,
  `current_balance` decimal(18,2) DEFAULT NULL,
  `total_value` decimal(18,2) DEFAULT NULL,
  `total_gain_loss` decimal(18,2) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `paper_transactions`
--

CREATE TABLE `paper_transactions` (
  `id` varchar(255) NOT NULL,
  `account_id` varchar(255) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `transaction_type` enum('buy','sell') NOT NULL,
  `shares` decimal(18,8) NOT NULL,
  `price` decimal(18,4) NOT NULL,
  `total_amount` decimal(18,2) DEFAULT NULL,
  `executed_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `password_reset_tokens`
--

CREATE TABLE `password_reset_tokens` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `token` varchar(255) NOT NULL,
  `expires_at` datetime NOT NULL,
  `used` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `portfolio_holdings`
--

CREATE TABLE `portfolio_holdings` (
  `id` varchar(255) NOT NULL,
  `portfolio_id` varchar(255) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `asset_type` varchar(20) DEFAULT NULL,
  `shares` decimal(18,8) NOT NULL,
  `avg_buy_price` decimal(18,4) DEFAULT NULL,
  `current_price` decimal(18,4) DEFAULT NULL,
  `current_value` decimal(18,2) DEFAULT NULL,
  `gain_loss` decimal(18,2) DEFAULT NULL,
  `gain_loss_percent` decimal(10,4) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `first_buy_date` date DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `portfolio_holdings`
--

INSERT INTO `portfolio_holdings` (`id`, `portfolio_id`, `symbol`, `asset_type`, `shares`, `avg_buy_price`, `current_price`, `current_value`, `gain_loss`, `gain_loss_percent`, `notes`, `first_buy_date`, `last_updated`) VALUES
('385336e4-2da2-4786-af41-e8a0f6989c78', '12695772-dd94-46c4-a220-bc594cf8af5e', 'AAPL', 'stock', 10.00000000, 100.0000, 258.2100, 2582.10, 1582.10, 158.2100, NULL, NULL, '2026-01-16 02:34:07'),
('d03109e1-2605-4d9b-9285-65b07411927d', '12695772-dd94-46c4-a220-bc594cf8af5e', 'GOOGL', 'stock', 100.00000000, 150.0000, 332.7800, 33278.00, 18278.00, 121.8533, NULL, NULL, '2026-01-16 02:45:04');

-- --------------------------------------------------------

--
-- Table structure for table `portfolio_transactions`
--

CREATE TABLE `portfolio_transactions` (
  `id` varchar(255) NOT NULL,
  `portfolio_id` varchar(255) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `transaction_type` enum('buy','sell','dividend','split') NOT NULL,
  `shares` decimal(18,8) NOT NULL,
  `price_per_share` decimal(18,4) NOT NULL,
  `total_amount` decimal(18,2) DEFAULT NULL,
  `fees` decimal(10,2) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `transaction_date` date NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `id` varchar(255) NOT NULL,
  `title` varchar(500) NOT NULL,
  `slug` varchar(255) DEFAULT NULL,
  `content` text DEFAULT NULL,
  `excerpt` text DEFAULT NULL,
  `featured_image` text DEFAULT NULL,
  `category_id` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `status` enum('draft','published','archived') DEFAULT NULL,
  `is_featured` tinyint(1) DEFAULT NULL,
  `view_count` int(11) DEFAULT NULL,
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`tags`)),
  `meta_title` varchar(255) DEFAULT NULL,
  `meta_description` text DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `published_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `post_categories`
--

CREATE TABLE `post_categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `color` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `sort_order` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `pricing`
--

CREATE TABLE `pricing` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `price_monthly` decimal(10,2) DEFAULT NULL,
  `price_yearly` decimal(10,2) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `features` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`features`)),
  `is_popular` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `sort_order` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `discount_price` decimal(10,2) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `image_url` text DEFAULT NULL,
  `stock_quantity` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `providers`
--

CREATE TABLE `providers` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `base_url` text DEFAULT NULL,
  `api_key` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `rate_limit` int(11) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quizzes`
--

CREATE TABLE `quizzes` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `course_id` int(11) DEFAULT NULL,
  `module_id` int(11) DEFAULT NULL,
  `time_limit_minutes` int(11) DEFAULT NULL,
  `passing_score` int(11) DEFAULT NULL,
  `max_attempts` int(11) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quiz_answers`
--

CREATE TABLE `quiz_answers` (
  `id` int(11) NOT NULL,
  `attempt_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `answer` text DEFAULT NULL,
  `is_correct` tinyint(1) DEFAULT NULL,
  `points_earned` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quiz_attempts`
--

CREATE TABLE `quiz_attempts` (
  `id` int(11) NOT NULL,
  `quiz_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `score` int(11) DEFAULT NULL,
  `total_points` int(11) DEFAULT NULL,
  `passed` tinyint(1) DEFAULT NULL,
  `time_taken_seconds` int(11) DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `quiz_questions`
--

CREATE TABLE `quiz_questions` (
  `id` int(11) NOT NULL,
  `quiz_id` int(11) NOT NULL,
  `question` text NOT NULL,
  `question_type` enum('multiple_choice','true_false','short_answer') DEFAULT NULL,
  `options` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`options`)),
  `correct_answer` text DEFAULT NULL,
  `explanation` text DEFAULT NULL,
  `points` int(11) DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `radio_stations`
--

CREATE TABLE `radio_stations` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `stream_url` varchar(500) NOT NULL,
  `website_url` varchar(500) DEFAULT NULL,
  `logo_url` varchar(500) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `genre` varchar(50) DEFAULT NULL,
  `language` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `bitrate` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `listeners_count` int(11) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `country_code` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `radio_stations`
--

INSERT INTO `radio_stations` (`id`, `name`, `stream_url`, `website_url`, `logo_url`, `country`, `genre`, `language`, `description`, `bitrate`, `is_active`, `listeners_count`, `position`, `created_at`, `country_code`) VALUES
(1, 'BBC Nepali', 'https://stream.live.vc.bbcmedia.co.uk/bbc_nepali_radio', NULL, 'https://static.files.bbci.co.uk/ws/simorgh-assets/public/nepali/images/icons/icon-128x128.png', 'Nepal', 'news', 'Nepali', NULL, NULL, 1, 0, 0, '2026-01-07 11:48:09', 'US'),
(2, 'America\'s Country', 'https://ais-sa2.cdnstream1.com/1976_128.mp3', NULL, 'https://marinifamily.files.wordpress.com/2015/08/favicon.png', 'United States', 'country', 'English', NULL, NULL, 1, 0, 0, '2026-01-07 11:48:09', 'US'),
(3, 'NetTalk America', 'https://stream-162.zeno.fm/st9bhqvgvceuv', NULL, 'https://img1.wsimg.com/isteam/ip/6e7215c5-5ca4-45c2-b61c-24421c4a5003/74cfc8bf-f67f-4e7d-ad46-0ac09ca2d362.gif.png', 'United States', 'talk', 'English', NULL, NULL, 1, 0, 0, '2026-01-07 11:48:09', 'US'),
(4, 'Radio Panamericana', 'https://stream-146.zeno.fm/pnwpbyfambruv', NULL, 'https://graph.facebook.com/NoticiasPanamericana/picture?width=200&height=200', 'Bolivia', 'culture', 'Spanish', NULL, NULL, 1, 0, 0, '2026-01-07 11:48:09', 'US'),
(5, 'Panamericana Retro Rock', 'https://us-b4-p-e-pb13-audio.cdn.mdstrm.com/live-audio', NULL, 'https://static-media.streema.com/media/cache/88/74/8874c7e02e56f56b4d18607b234c95ba.jpg', 'Peru', 'rock', 'English', NULL, NULL, 1, 0, 0, '2026-01-07 11:48:09', 'US'),
(6, 'Radio America 94.7', 'http://26563.live.streamtheworld.com/AMERICA_SC', NULL, 'https://d9hhnadinot6y.cloudfront.net/imag/2023/08/cropped-cropped-favico-192x192-1-180x180.png', 'Honduras', 'news', 'Spanish', NULL, NULL, 1, 0, 0, '2026-01-07 11:48:09', 'US'),
(7, 'BBC Nepali', 'https://stream.live.vc.bbcmedia.co.uk/bbc_nepali_radio', 'https://www.bbc.com/nepali', 'https://static.files.bbci.co.uk/ws/simorgh-assets/public/nepali/images/icons/icon-128x128.png', 'Nepal', 'news', 'nepali', NULL, '56 kbps', 1, 0, 0, '2026-01-08 11:55:19', 'NP'),
(8, 'BBC Nepali 103 MHz', 'https://stream.live.vc.bbcmedia.co.uk/bbc_nepali_radio', 'https://bbc.co.uk/nepali', 'https://static.files.bbci.co.uk/ws/simorgh-assets/public/nepali/images/icons/icon-128x128.png', 'Nepal', '', '', NULL, '56 kbps', 1, 0, 0, '2026-01-08 11:55:19', 'NP');

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` text DEFAULT NULL,
  `permissions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`permissions`)),
  `is_system` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `roles`
--

INSERT INTO `roles` (`id`, `name`, `description`, `permissions`, `is_system`, `created_at`) VALUES
(1, 'admin', 'Administrator with full access', '{\"all\": true}', 1, '2026-01-14 21:57:05'),
(2, 'user', 'Standard user', '{\"read\": true}', 1, '2026-01-14 21:57:05'),
(3, 'editor', 'Content editor', '{\"read\": true, \"write\": true}', 0, '2026-01-14 21:57:05');

-- --------------------------------------------------------

--
-- Table structure for table `rss_feeds`
--

CREATE TABLE `rss_feeds` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `url` text NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `last_fetched` datetime DEFAULT NULL,
  `fetch_interval` int(11) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `rss_items`
--

CREATE TABLE `rss_items` (
  `id` varchar(255) NOT NULL,
  `feed_id` varchar(255) DEFAULT NULL,
  `title` varchar(500) DEFAULT NULL,
  `link` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `pub_date` datetime DEFAULT NULL,
  `guid` varchar(500) DEFAULT NULL,
  `image_url` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sellers`
--

CREATE TABLE `sellers` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `business_name` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `logo_url` text DEFAULT NULL,
  `status` enum('pending','approved','suspended') DEFAULT NULL,
  `rating` decimal(2,1) DEFAULT NULL,
  `total_sales` int(11) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `seller_applications`
--

CREATE TABLE `seller_applications` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `business_name` varchar(255) DEFAULT NULL,
  `business_type` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `documents` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`documents`)),
  `status` enum('pending','approved','rejected') DEFAULT NULL,
  `reviewed_by` int(11) DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `seller_categories`
--

CREATE TABLE `seller_categories` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

CREATE TABLE `services` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `service_features`
--

CREATE TABLE `service_features` (
  `id` int(11) NOT NULL,
  `service_id` int(11) NOT NULL,
  `feature` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `sports_events`
--

CREATE TABLE `sports_events` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `sport_type` varchar(50) DEFAULT NULL,
  `league` varchar(100) DEFAULT NULL,
  `team_home` varchar(100) DEFAULT NULL,
  `team_away` varchar(100) DEFAULT NULL,
  `score_home` varchar(20) DEFAULT NULL,
  `score_away` varchar(20) DEFAULT NULL,
  `event_date` datetime DEFAULT NULL,
  `venue` varchar(255) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `stream_url` text DEFAULT NULL,
  `thumbnail_url` text DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_live` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sports_events`
--

INSERT INTO `sports_events` (`id`, `name`, `sport_type`, `league`, `team_home`, `team_away`, `score_home`, `score_away`, `event_date`, `venue`, `status`, `stream_url`, `thumbnail_url`, `country_code`, `is_active`, `is_live`, `created_at`) VALUES
(1, 'India vs Australia - 3rd Test', 'cricket', 'Border-Gavaskar Trophy', 'India', 'Australia', '250/6', '474', '2026-01-14 18:00:01', 'Melbourne Cricket Ground', 'live', NULL, NULL, 'GLOBAL', 1, 1, '2026-01-09 12:15:01'),
(2, 'Nepal vs UAE - T20', 'cricket', 'ACC Premier Cup', 'Nepal', 'UAE', NULL, NULL, '2026-01-13 18:00:01', 'TU Cricket Ground', 'scheduled', NULL, NULL, 'NP', 1, 0, '2026-01-09 12:15:01'),
(3, 'England vs New Zealand - ODI', 'cricket', 'ODI Series', 'England', 'New Zealand', NULL, NULL, '2026-01-11 18:00:01', 'Lords Cricket Ground', 'scheduled', NULL, NULL, 'GB', 1, 0, '2026-01-09 12:15:01'),
(4, 'Pakistan vs South Africa - Test', 'cricket', 'Test Championship', 'Pakistan', 'South Africa', '320', '295', '2026-01-12 18:00:01', 'National Stadium Karachi', 'completed', NULL, NULL, 'GLOBAL', 1, 0, '2026-01-09 12:15:01'),
(5, 'Manchester United vs Liverpool', 'football', 'Premier League', 'Manchester United', 'Liverpool', NULL, NULL, '2026-01-16 18:00:01', 'Old Trafford', 'scheduled', NULL, NULL, 'GB', 1, 0, '2026-01-09 12:15:01'),
(6, 'Real Madrid vs Barcelona', 'football', 'La Liga', 'Real Madrid', 'Barcelona', NULL, NULL, '2026-01-10 18:00:01', 'Santiago Bernabéu', 'scheduled', NULL, NULL, 'ES', 1, 0, '2026-01-09 12:15:01'),
(7, 'Bayern Munich vs Dortmund', 'football', 'Bundesliga', 'Bayern Munich', 'Borussia Dortmund', '2', '1', '2026-01-14 18:00:01', 'Allianz Arena', 'live', NULL, NULL, 'DE', 1, 1, '2026-01-09 12:15:01'),
(8, 'PSG vs Marseille', 'football', 'Ligue 1', 'Paris Saint-Germain', 'Olympique Marseille', NULL, NULL, '2026-01-13 18:00:01', 'Parc des Princes', 'scheduled', NULL, NULL, 'FR', 1, 0, '2026-01-09 12:15:01'),
(9, 'Inter Milan vs AC Milan', 'football', 'Serie A', 'Inter Milan', 'AC Milan', '3', '2', '2026-01-14 18:00:01', 'San Siro', 'completed', NULL, NULL, 'IT', 1, 0, '2026-01-09 12:15:01'),
(10, 'Lakers vs Warriors', 'basketball', 'NBA', 'Los Angeles Lakers', 'Golden State Warriors', '87', '92', '2026-01-07 18:00:01', 'Crypto.com Arena', 'live', NULL, NULL, 'US', 1, 1, '2026-01-09 12:15:01'),
(11, 'Celtics vs Bucks', 'basketball', 'NBA', 'Boston Celtics', 'Milwaukee Bucks', NULL, NULL, '2026-01-08 18:00:01', 'TD Garden', 'scheduled', NULL, NULL, 'US', 1, 0, '2026-01-09 12:15:01'),
(12, 'Bulls vs 76ers', 'basketball', 'NBA', 'Chicago Bulls', 'Philadelphia 76ers', '105', '112', '2026-01-16 18:00:01', 'United Center', 'completed', NULL, NULL, 'US', 1, 0, '2026-01-09 12:15:01'),
(13, 'Australian Open - Mens Final', 'tennis', 'Grand Slam', 'Djokovic', 'Sinner', NULL, NULL, '2026-01-11 18:00:01', 'Rod Laver Arena', 'scheduled', NULL, NULL, 'GLOBAL', 1, 0, '2026-01-09 12:15:01'),
(14, 'Wimbledon - Womens Semifinal', 'tennis', 'Grand Slam', 'Swiatek', 'Sabalenka', '6-4, 6-3', '-', '2026-01-13 18:00:02', 'Centre Court', 'completed', NULL, NULL, 'GLOBAL', 1, 0, '2026-01-09 12:15:02'),
(15, 'India vs Pakistan - Asia Cup', 'hockey', 'Asia Cup', 'India', 'Pakistan', NULL, NULL, '2026-01-09 18:00:02', 'Dhaka Hockey Stadium', 'scheduled', NULL, NULL, 'GLOBAL', 1, 0, '2026-01-09 12:15:02'),
(16, 'New Zealand vs Australia', 'rugby', 'Bledisloe Cup', 'All Blacks', 'Wallabies', NULL, NULL, '2026-01-11 18:00:02', 'Eden Park', 'scheduled', NULL, NULL, 'GLOBAL', 1, 0, '2026-01-09 12:15:02');

-- --------------------------------------------------------

--
-- Table structure for table `stock_offers`
--

CREATE TABLE `stock_offers` (
  `id` varchar(255) NOT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `offer_type` enum('ipo','fpo','rights') DEFAULT NULL,
  `price_range` varchar(50) DEFAULT NULL,
  `units` bigint(20) DEFAULT NULL,
  `min_application` int(11) DEFAULT NULL,
  `open_date` date DEFAULT NULL,
  `close_date` date DEFAULT NULL,
  `listing_date` date DEFAULT NULL,
  `status` enum('upcoming','open','closed','listed') DEFAULT NULL,
  `prospectus_url` text DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `exchange` varchar(50) DEFAULT NULL,
  `deal_type` varchar(50) DEFAULT NULL,
  `shares_offered` bigint(20) DEFAULT NULL,
  `offer_price` decimal(18,6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `stock_offers`
--

INSERT INTO `stock_offers` (`id`, `symbol`, `company_name`, `offer_type`, `price_range`, `units`, `min_application`, `open_date`, `close_date`, `listing_date`, `status`, `prospectus_url`, `country_code`, `created_at`, `exchange`, `deal_type`, `shares_offered`, `offer_price`) VALUES
('offer_newenergy_7656', 'NEWENERGY', 'NewEnergy Corp.', 'ipo', '25-30', NULL, NULL, '2025-12-09', '2026-01-14', NULL, 'upcoming', NULL, 'US', '2026-01-07 11:48:09', NULL, NULL, NULL, NULL),
('offer_rddt_8980', 'RDDT', 'Reddit Inc.', 'ipo', '31-34', NULL, NULL, '2025-12-13', '2026-01-19', NULL, 'listed', NULL, 'US', '2026-01-07 11:48:09', NULL, NULL, NULL, NULL),
('offer_xyzco_3843', 'XYZCO', 'XYZ Technologies', 'ipo', '18-22', NULL, NULL, '2025-12-11', '2026-01-14', NULL, 'open', NULL, 'US', '2026-01-07 11:48:09', NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `stock_price_history`
--

CREATE TABLE `stock_price_history` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `date` date NOT NULL,
  `open_price` decimal(18,6) DEFAULT NULL,
  `high` decimal(18,6) DEFAULT NULL,
  `low` decimal(18,6) DEFAULT NULL,
  `close` decimal(18,6) DEFAULT NULL,
  `adj_close` decimal(18,6) DEFAULT NULL,
  `volume` bigint(20) DEFAULT NULL,
  `interval` varchar(10) DEFAULT '1d',
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `stock_splits`
--

CREATE TABLE `stock_splits` (
  `id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `company_name` varchar(255) DEFAULT NULL,
  `split_date` date NOT NULL,
  `split_ratio` varchar(20) DEFAULT NULL,
  `numerator` int(11) DEFAULT NULL,
  `denominator` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `subscribers`
--

CREATE TABLE `subscribers` (
  `id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `preferences` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`preferences`)),
  `source` varchar(100) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `subscribed_at` datetime DEFAULT NULL,
  `unsubscribed_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tasks`
--

CREATE TABLE `tasks` (
  `id` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `assigned_to` int(11) DEFAULT NULL,
  `status` enum('pending','in_progress','completed','cancelled') DEFAULT NULL,
  `priority` enum('low','medium','high','urgent') DEFAULT NULL,
  `due_date` date DEFAULT NULL,
  `created_by` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `team_members`
--

CREATE TABLE `team_members` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `bio` text DEFAULT NULL,
  `photo_url` text DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `linkedin` varchar(255) DEFAULT NULL,
  `twitter` varchar(255) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `sort_order` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `team_members`
--

INSERT INTO `team_members` (`id`, `name`, `title`, `bio`, `photo_url`, `email`, `linkedin`, `twitter`, `is_active`, `sort_order`, `created_at`) VALUES
(1, 'Bishal Regmi', 'Software Er', 'NTG', '', 'regmibishal964@gmail.com', '', '', 1, 0, '2026-01-07 13:23:56');

-- --------------------------------------------------------

--
-- Table structure for table `testimonials`
--

CREATE TABLE `testimonials` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `company` varchar(255) DEFAULT NULL,
  `avatar_url` text DEFAULT NULL,
  `content` text NOT NULL,
  `rating` int(11) DEFAULT NULL,
  `is_featured` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tool_settings`
--

CREATE TABLE `tool_settings` (
  `tool_slug` varchar(100) NOT NULL,
  `tool_name` varchar(255) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `order_index` int(11) DEFAULT NULL,
  `is_implemented` tinyint(1) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tool_settings`
--

INSERT INTO `tool_settings` (`tool_slug`, `tool_name`, `category`, `enabled`, `order_index`, `is_implemented`, `country_code`, `created_at`, `updated_at`) VALUES
('bmi', 'BMI Calculator', 'Health & Fitness', 1, 34, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('budget-planner', 'Budget Planner', 'Personal Finance', 1, 25, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('calorie-calculator', 'Calorie Calculator', 'Health & Fitness', 1, 35, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('capital-gains', 'Capital Gains Tax', 'Taxation', 1, 15, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('car-insurance', 'Car Insurance Calculator', 'Insurance', 1, 24, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('car-loan', 'Car Loan EMI', 'Finance & Loans', 1, 9, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('compound', 'Compound Interest Calculator', 'Investing', 1, 1, 1, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('credit-card-payoff', 'Credit Card Payoff', 'Debt', 0, 29, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 13:26:00'),
('debt-avalanche', 'Debt Avalanche Calculator', 'Debt', 1, 31, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('debt-snowball', 'Debt Snowball Calculator', 'Debt', 1, 30, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('dividend-yield', 'Dividend Yield Calculator', 'Investing', 1, 6, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('emergency-fund', 'Emergency Fund Calculator', 'Personal Finance', 1, 26, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('emi', 'Loan EMI Calculator', 'Finance & Loans', 1, 7, 1, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('epf', 'EPF Calculator', 'Retirement', 1, 20, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('goal-planner', 'Goal Planner', 'Investing', 1, 2, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('health-premium', 'Health Premium Estimator', 'Insurance', 1, 23, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('home-loan', 'Home Loan EMI', 'Finance & Loans', 1, 8, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('hra-exemption', 'HRA Exemption Calculator', 'Taxation', 1, 14, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('income-tax', 'Income Tax Calculator', 'Taxation', 1, 13, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('inflation', 'Inflation Calculator', 'Personal Finance', 1, 28, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('life-insurance', 'Life Insurance Needs', 'Insurance', 1, 21, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('loan-eligibility', 'Loan Eligibility', 'Finance & Loans', 1, 11, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('lumpsum', 'Lumpsum Calculator', 'Investing', 1, 3, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('mutual-fund-returns', 'Mutual Fund Returns', 'Investing', 1, 5, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('net-worth', 'Net Worth Calculator', 'Personal Finance', 1, 27, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('nps', 'NPS Calculator', 'Retirement', 1, 19, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('pension', 'Pension Calculator', 'Retirement', 1, 18, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('personal-loan', 'Personal Loan EMI', 'Finance & Loans', 1, 10, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('prepayment-calculator', 'Loan Prepayment', 'Finance & Loans', 1, 12, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('rent-vs-buy', 'Rent vs Buy Calculator', 'Real Estate', 1, 32, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('retirement', 'Retirement Calculator', 'Retirement', 1, 17, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('sip', 'SIP Calculator', 'Investing', 1, 0, 1, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('stamp-duty', 'Stamp Duty Calculator', 'Real Estate', 1, 33, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('step-up-sip', 'Step-up SIP Calculator', 'Investing', 1, 4, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('tax-regime-comparison', 'Old vs New Tax Regime', 'Taxation', 1, 16, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09'),
('term-insurance', 'Term Insurance Planner', 'Insurance', 1, 22, 0, 'GLOBAL', '2026-01-07 11:48:09', '2026-01-07 11:48:09');

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `type` varchar(50) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `status` enum('pending','completed','failed','cancelled') DEFAULT NULL,
  `reference` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `meta_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`meta_data`)),
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `trending_topics`
--

CREATE TABLE `trending_topics` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  `mentions` int(11) DEFAULT NULL,
  `sentiment` varchar(20) DEFAULT NULL,
  `related_symbols` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`related_symbols`)),
  `created_at` datetime DEFAULT NULL,
  `country_code` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `trending_topics`
--

INSERT INTO `trending_topics` (`id`, `title`, `category`, `rank`, `mentions`, `sentiment`, `related_symbols`, `created_at`, `country_code`) VALUES
(1, 'NVIDIA earnings beat expectations', 'Tech', 1, 0, NULL, NULL, '2026-01-07 11:48:09', 'US'),
(2, 'Bitcoin ETF approval speculation', 'Crypto', 2, 0, NULL, NULL, '2026-01-07 11:48:09', 'US'),
(3, 'Fed rate decision impact', 'Economy', 3, 0, NULL, NULL, '2026-01-07 11:48:09', 'US'),
(4, 'Tesla Cybertruck deliveries begin', 'Auto', 4, 0, NULL, NULL, '2026-01-07 11:48:09', 'US'),
(5, 'Oil prices surge on OPEC cuts', 'Energy', 5, 0, NULL, NULL, '2026-01-07 11:48:09', 'US');

-- --------------------------------------------------------

--
-- Table structure for table `tv_channels`
--

CREATE TABLE `tv_channels` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `logo_url` text DEFAULT NULL,
  `stream_url` text DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `language` varchar(50) DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `is_live` tinyint(1) DEFAULT NULL,
  `is_premium` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `sort_order` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `tv_channels`
--

INSERT INTO `tv_channels` (`id`, `name`, `description`, `logo_url`, `stream_url`, `category`, `language`, `country_code`, `is_live`, `is_premium`, `is_active`, `sort_order`, `created_at`) VALUES
('abcnews', 'ABC News', NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/ABC_News_logo.svg/512px-ABC_News_logo.svg.png', 'https://www.youtube.com/embed/vC-ky5VumJI', 'News', 'English', 'US', 1, 0, 1, 0, '2026-01-07 11:48:09'),
('aljazeera', 'Al Jazeera English', NULL, 'https://upload.wikimedia.org/wikipedia/en/thumb/b/bc/Al_Jazeera_English_logo.svg/512px-Al_Jazeera_English_logo.svg.png', 'https://www.youtube.com/embed/bNyUyrR0PHo', 'News', 'English', 'QA', 1, 0, 1, 0, '2026-01-08 12:28:19'),
('bbcworld', 'BBC World News', NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/BBC_World_News_logo.svg/512px-BBC_World_News_logo.svg.png', 'https://www.youtube.com/embed/t8yg8sVoXzU', 'News', 'English', 'UK', 1, 0, 1, 0, '2026-01-08 12:28:19'),
('bloomberg', 'Bloomberg TV', NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Bloomberg_Television_logo.svg/512px-Bloomberg_Television_logo.svg.png', 'https://www.youtube.com/embed/dp8PhLsUcFE', 'Finance', 'English', 'US', 1, 0, 1, 0, '2026-01-07 11:48:09'),
('cnbc', 'CNBC', NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/CNBC_logo.svg/512px-CNBC_logo.svg.png', 'https://www.youtube.com/embed/9wTn9EzrLzk', 'Finance', 'English', 'US', 1, 0, 1, 0, '2026-01-07 11:48:09'),
('cnn', 'CNN', NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/CNN.svg/512px-CNN.svg.png', 'https://www.youtube.com/embed/5anLPw0Efmo', 'News', 'English', 'US', 1, 0, 1, 0, '2026-01-07 11:48:09'),
('espn', 'ESPN', NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/ESPN_wordmark.svg/512px-ESPN_wordmark.svg.png', 'https://www.youtube.com/embed/DTvS9lvRxZ8', 'Sports', 'English', 'US', 1, 0, 1, 0, '2026-01-07 11:48:09'),
('ndtv', 'NDTV', NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/NDTV_logo.svg/512px-NDTV_logo.svg.png', 'https://www.youtube.com/embed/WB9GjZSkSB8', 'News', 'English', 'IN', 1, 0, 1, 0, '2026-01-08 12:28:19'),
('ntv_nepal', 'NTV Nepal', NULL, 'https://i.ytimg.com/vi/h6jqbz_5h5E/maxresdefault.jpg', 'https://www.youtube.com/embed/h6jqbz_5h5E', 'News', 'Nepali', 'NP', 1, 0, 1, 0, '2026-01-08 12:28:19'),
('skynews', 'Sky News', NULL, 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b5/Sky_News.svg/512px-Sky_News.svg.png', 'https://www.youtube.com/embed/9Auq9mYxFEE', 'News', 'English', 'UK', 1, 0, 1, 0, '2026-01-08 12:28:19'),
('techcrunch', 'TechCrunch', NULL, 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/TechCrunch_logo.svg/512px-TechCrunch_logo.svg.png', 'https://www.youtube.com/embed/pMbvxlNB_zs', 'Technology', 'English', 'US', 1, 0, 1, 0, '2026-01-07 11:48:09');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` text NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` varchar(50) NOT NULL,
  `active` smallint(6) DEFAULT NULL,
  `createdAt` datetime DEFAULT NULL,
  `updatedAt` datetime DEFAULT NULL,
  `forceReset` smallint(6) DEFAULT NULL,
  `firebase_uid` varchar(255) DEFAULT NULL,
  `avatar_url` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `account_status` enum('active','deactivated','suspended','deleted') DEFAULT NULL,
  `deactivated_at` datetime DEFAULT NULL,
  `deactivation_reason` text DEFAULT NULL,
  `referred_by` int(11) DEFAULT NULL,
  `total_reward_points` int(11) DEFAULT NULL,
  `email_verified` tinyint(1) DEFAULT NULL,
  `email_verified_at` datetime DEFAULT NULL,
  `phone_verified` tinyint(1) DEFAULT NULL,
  `phone_verified_at` datetime DEFAULT NULL,
  `id_verified` tinyint(1) DEFAULT NULL,
  `id_verified_at` datetime DEFAULT NULL,
  `verified_badge` tinyint(1) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `currency` varchar(3) DEFAULT NULL,
  `tax_residency` varchar(100) DEFAULT NULL,
  `language_pref` varchar(10) DEFAULT NULL,
  `country_code` varchar(2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `role`, `active`, `createdAt`, `updatedAt`, `forceReset`, `firebase_uid`, `avatar_url`, `created_at`, `updated_at`, `last_login_at`, `account_status`, `deactivated_at`, `deactivation_reason`, `referred_by`, `total_reward_points`, `email_verified`, `email_verified_at`, `phone_verified`, `phone_verified_at`, `id_verified`, `id_verified_at`, `verified_badge`, `phone`, `currency`, `tax_residency`, `language_pref`, `country_code`) VALUES
(1, 'Bishal', 'regmibishal964@gmail.com', '$2b$12$DJT31lC19XCmq8UtfXRG1OKWP0jwbEJ7q3xlWaebosq/ZUXVYC.Du', 'user', 1, '2026-01-10 03:48:47', '2026-01-16 02:13:26', 0, '8dgBVkHiN7PpGNVdLJwTAMVa6fD3', 'https://lh3.googleusercontent.com/a/ACg8ocJlB_u6MZrNR2RinMbjEG4XeDld2nLL2vWnoGmrboBtKcu2KA=s96-c', '2026-01-10 03:48:47', '2026-01-16 02:13:26', '2026-01-16 02:05:37', 'active', NULL, NULL, NULL, 0, 0, NULL, 0, NULL, 0, NULL, 0, '', 'USD', NULL, 'en', 'US'),
(2, 'Admin User', 'admin@pearto.com', '$2b$12$z0vbEpuB7tU2Hc7IIltk3en0z5lmezte68SBUeohcFvghCWlzou9m', 'admin', 1, '2026-01-14 21:57:05', '2026-01-14 21:57:05', 0, NULL, NULL, '2026-01-14 21:57:05', '2026-01-14 21:57:05', NULL, 'active', NULL, NULL, NULL, 0, 1, NULL, 0, NULL, 0, NULL, 0, NULL, 'USD', NULL, 'en', 'US'),
(3, 'John Doe', 'john@example.com', '$2b$12$xv/0Djx0NPRwImGB33BiUO38JbhpGGvqS2GiR.G6SpK4TGiXboJF6', 'user', 1, '2026-01-14 21:57:05', '2026-01-14 21:57:05', 0, NULL, NULL, '2026-01-14 21:57:05', '2026-01-14 21:57:05', NULL, 'active', NULL, NULL, NULL, 0, 1, NULL, 0, NULL, 0, NULL, 0, NULL, 'USD', NULL, 'en', 'US'),
(4, 'Jane Smith', 'jane@example.com', '$2b$12$QuUa85lShogE1rOxBS74cu4v6iNnqO9Inm.54tMNztx11mPrwzIrO', 'user', 1, '2026-01-14 21:57:06', '2026-01-14 21:57:06', 0, NULL, NULL, '2026-01-14 21:57:06', '2026-01-14 21:57:06', NULL, 'active', NULL, NULL, NULL, 0, 1, NULL, 0, NULL, 0, NULL, 0, NULL, 'USD', NULL, 'en', 'UK'),
(5, 'Rahul Sharma', 'rahul@example.com', '$2b$12$dBtIQDG.0X5Gc4rpO8ZqIONQthVDxLaEzR8xEbm0brRKu7L8vCeB6', 'user', 1, '2026-01-14 21:57:06', '2026-01-14 21:57:06', 0, NULL, NULL, '2026-01-14 21:57:06', '2026-01-14 21:57:06', NULL, 'active', NULL, NULL, NULL, 0, 1, NULL, 0, NULL, 0, NULL, 0, NULL, 'USD', NULL, 'en', 'IN');

-- --------------------------------------------------------

--
-- Table structure for table `user_activities`
--

CREATE TABLE `user_activities` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `action` varchar(100) NOT NULL,
  `entity_type` varchar(50) DEFAULT NULL,
  `entity_id` varchar(255) DEFAULT NULL,
  `details` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_activities`
--

INSERT INTO `user_activities` (`id`, `user_id`, `action`, `entity_type`, `entity_id`, `details`, `ip_address`, `created_at`) VALUES
('63990e1f-c4ad-42ab-93b4-2387e33150fb', 1, 'alert_created', 'alert', 'fd9a4221-0d51-407f-8b40-53c81bbbd412', 'symbol=AAPL;condition=above;target=258.21', '127.0.0.1', '2026-01-16 02:15:46'),
('64eebe4e-0866-4222-b579-4127c93be4a7', 1, 'holding_added', 'portfolio', 'd03109e1-2605-4d9b-9285-65b07411927d', 'symbol=GOOGL;shares=100.0', '127.0.0.1', '2026-01-16 02:45:04'),
('cdfb6b15-3e7f-4413-bf41-27357c4c1780', 1, 'holding_added', 'portfolio', '385336e4-2da2-4786-af41-e8a0f6989c78', 'symbol=AAPL;shares=10.0', '127.0.0.1', '2026-01-16 02:34:07'),
('d4d518cc-aab2-4425-92d7-b9cf93b8790c', 1, 'watchlist_add', 'watchlist', 'AAPL', NULL, '127.0.0.1', '2026-01-16 02:15:13');

-- --------------------------------------------------------

--
-- Table structure for table `user_alerts`
--

CREATE TABLE `user_alerts` (
  `id` varchar(36) NOT NULL,
  `user_id` int(11) NOT NULL,
  `symbol` varchar(20) DEFAULT NULL,
  `alert_type` varchar(50) DEFAULT NULL,
  `condition` varchar(50) DEFAULT NULL,
  `target_value` decimal(18,4) DEFAULT NULL,
  `is_triggered` tinyint(1) DEFAULT NULL,
  `triggered_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `notify_email` tinyint(1) DEFAULT NULL,
  `notify_push` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_alerts`
--

INSERT INTO `user_alerts` (`id`, `user_id`, `symbol`, `alert_type`, `condition`, `target_value`, `is_triggered`, `triggered_at`, `is_active`, `notify_email`, `notify_push`, `created_at`) VALUES
('5d5ebe25-7274-4bcb-bb15-6f9c85293354', 1, 'AAPL', 'price', 'below', 422.9800, 1, '2026-01-16 01:59:27', 1, 1, 1, '2026-01-16 01:58:08'),
('976857b2-6d85-4d2d-83cc-e50d9b55231f', 1, 'AAPL', 'price', 'above', 100.0000, 1, '2026-01-16 02:06:04', 1, 1, 1, '2026-01-16 02:05:53'),
('c56197a9-6cae-48b9-8fcd-89a7d0e795ea', 1, 'AAPL', 'price', 'below', 422.9800, 1, '2026-01-16 01:55:14', 1, 1, 1, '2026-01-16 01:55:08'),
('e1832822-5c70-41f0-ab66-fcb1a695d4d8', 1, 'AAPL', 'price', 'below', 422.9800, 1, '2026-01-16 01:49:11', 1, 1, 1, '2026-01-16 01:49:06'),
('fd9a4221-0d51-407f-8b40-53c81bbbd412', 1, 'AAPL', 'price', 'above', 258.2100, 1, '2026-01-16 02:16:06', 1, 1, 1, '2026-01-16 02:15:46');

-- --------------------------------------------------------

--
-- Table structure for table `user_dashboard_config`
--

CREATE TABLE `user_dashboard_config` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `layout` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`layout`)),
  `widgets` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`widgets`)),
  `theme` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_devices`
--

CREATE TABLE `user_devices` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `device_type` varchar(50) DEFAULT NULL,
  `device_name` varchar(255) DEFAULT NULL,
  `device_token` text DEFAULT NULL,
  `platform` varchar(50) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `last_used_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_documents`
--

CREATE TABLE `user_documents` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `document_type` varchar(50) DEFAULT NULL,
  `file_url` text DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT NULL,
  `reviewed_by` int(11) DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_documents`
--

INSERT INTO `user_documents` (`id`, `user_id`, `document_type`, `file_url`, `status`, `reviewed_by`, `reviewed_at`, `notes`, `created_at`) VALUES
('0b68b92d-448f-4634-a03c-4fd0c75ae452', 1, 'id_card', '/uploads/documents/28571cd6-6e16-464b-8f47-dc8e039bf3fd.jpg', 'pending', NULL, NULL, NULL, '2026-01-16 02:08:25'),
('3f5271ab-136d-4a48-b491-a485ef960aaf', 1, 'id_card', '/uploads/documents/d495f59b-409a-411a-a47f-f08e23d10f4f.pdf', 'pending', NULL, NULL, NULL, '2026-01-16 02:08:00');

-- --------------------------------------------------------

--
-- Table structure for table `user_economic_events`
--

CREATE TABLE `user_economic_events` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `event_id` varchar(255) NOT NULL,
  `notify_before` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_enrollments`
--

CREATE TABLE `user_enrollments` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `progress` int(11) DEFAULT NULL,
  `current_module_id` int(11) DEFAULT NULL,
  `status` enum('enrolled','in_progress','completed','paused') DEFAULT NULL,
  `enrolled_at` datetime DEFAULT NULL,
  `last_activity_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_enrollments`
--

INSERT INTO `user_enrollments` (`id`, `user_id`, `course_id`, `progress`, `current_module_id`, `status`, `enrolled_at`, `last_activity_at`, `completed_at`) VALUES
(1, 1, 6, 48, 32, 'in_progress', '2026-01-14 22:09:48', '2026-01-15 03:56:07', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `user_notification_prefs`
--

CREATE TABLE `user_notification_prefs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `email_marketing` tinyint(1) DEFAULT NULL,
  `email_alerts` tinyint(1) DEFAULT NULL,
  `email_news` tinyint(1) DEFAULT NULL,
  `push_alerts` tinyint(1) DEFAULT NULL,
  `push_news` tinyint(1) DEFAULT NULL,
  `sms_alerts` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_portfolios`
--

CREATE TABLE `user_portfolios` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `is_default` tinyint(1) DEFAULT NULL,
  `is_public` tinyint(1) DEFAULT NULL,
  `total_value` decimal(18,2) DEFAULT NULL,
  `total_gain_loss` decimal(18,2) DEFAULT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_portfolios`
--

INSERT INTO `user_portfolios` (`id`, `user_id`, `name`, `description`, `is_default`, `is_public`, `total_value`, `total_gain_loss`, `currency`, `created_at`, `updated_at`) VALUES
('12695772-dd94-46c4-a220-bc594cf8af5e', 1, 'My Portfolio', NULL, 0, 0, 0.00, 0.00, 'USD', '2026-01-16 02:33:52', '2026-01-16 02:33:52');

-- --------------------------------------------------------

--
-- Table structure for table `user_saved_terms`
--

CREATE TABLE `user_saved_terms` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `term_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_sessions`
--

CREATE TABLE `user_sessions` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `token` text DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `last_activity` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_watchlist`
--

CREATE TABLE `user_watchlist` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `added_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vendors`
--

CREATE TABLE `vendors` (
  `id` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `logo_url` text DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `status` enum('pending','active','suspended') DEFAULT NULL,
  `country_code` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vendor_api_keys`
--

CREATE TABLE `vendor_api_keys` (
  `id` varchar(255) NOT NULL,
  `vendor_id` varchar(255) NOT NULL,
  `key_name` varchar(100) DEFAULT NULL,
  `api_key` varchar(255) DEFAULT NULL,
  `secret_key` varchar(255) DEFAULT NULL,
  `permissions` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`permissions`)),
  `is_active` tinyint(1) DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  `last_used_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `vendor_custom_apis`
--

CREATE TABLE `vendor_custom_apis` (
  `id` varchar(255) NOT NULL,
  `vendor_id` varchar(255) NOT NULL,
  `endpoint` varchar(255) DEFAULT NULL,
  `method` varchar(10) DEFAULT NULL,
  `headers` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`headers`)),
  `body_template` text DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `watchlists`
--

CREATE TABLE `watchlists` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `is_default` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `watchlists`
--

INSERT INTO `watchlists` (`id`, `user_id`, `name`, `is_default`, `created_at`, `updated_at`) VALUES
('a1eb3df8-396b-4681-b56c-e0bf9a8283d9', 1, 'Default Watchlist', 1, '2026-01-16 02:15:13', '2026-01-16 02:15:13');

-- --------------------------------------------------------

--
-- Table structure for table `watchlist_items`
--

CREATE TABLE `watchlist_items` (
  `id` int(11) NOT NULL,
  `watchlist_id` varchar(255) NOT NULL,
  `symbol` varchar(20) NOT NULL,
  `asset_type` varchar(20) DEFAULT NULL,
  `target_price` decimal(18,4) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `added_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `watchlist_items`
--

INSERT INTO `watchlist_items` (`id`, `watchlist_id`, `symbol`, `asset_type`, `target_price`, `notes`, `added_at`) VALUES
(1, 'a1eb3df8-396b-4681-b56c-e0bf9a8283d9', 'AAPL', 'stock', NULL, NULL, '2026-01-16 02:15:13');

-- --------------------------------------------------------

--
-- Table structure for table `wealth_state`
--

CREATE TABLE `wealth_state` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `total_portfolio_value` decimal(18,2) DEFAULT NULL,
  `total_cash` decimal(18,2) DEFAULT NULL,
  `total_investments` decimal(18,2) DEFAULT NULL,
  `daily_change` decimal(18,2) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `webinars`
--

CREATE TABLE `webinars` (
  `id` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `host_id` int(11) DEFAULT NULL,
  `scheduled_at` datetime DEFAULT NULL,
  `duration_minutes` int(11) DEFAULT NULL,
  `max_attendees` int(11) DEFAULT NULL,
  `meeting_url` text DEFAULT NULL,
  `recording_url` text DEFAULT NULL,
  `status` enum('scheduled','live','completed','cancelled') DEFAULT NULL,
  `is_free` tinyint(1) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `thumbnail_url` text DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `webinar_attendance`
--

CREATE TABLE `webinar_attendance` (
  `id` int(11) NOT NULL,
  `webinar_id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `registered_at` datetime DEFAULT NULL,
  `attended` tinyint(1) DEFAULT NULL,
  `join_time` datetime DEFAULT NULL,
  `leave_time` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `withdrawals`
--

CREATE TABLE `withdrawals` (
  `id` varchar(255) NOT NULL,
  `user_id` int(11) NOT NULL,
  `amount` decimal(18,2) NOT NULL,
  `currency` varchar(10) DEFAULT NULL,
  `payment_method` varchar(50) DEFAULT NULL,
  `account_details` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`account_details`)),
  `status` enum('pending','approved','processing','completed','rejected') DEFAULT NULL,
  `approved_by` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `processed_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `affiliates`
--
ALTER TABLE `affiliates`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `agent_runs`
--
ALTER TABLE `agent_runs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ai_generation_runs`
--
ALTER TABLE `ai_generation_runs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ai_post_drafts`
--
ALTER TABLE `ai_post_drafts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `analyst_recommendations`
--
ALTER TABLE `analyst_recommendations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_symbol` (`symbol`),
  ADD KEY `idx_date` (`date`);

--
-- Indexes for table `analytics_events`
--
ALTER TABLE `analytics_events`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `api_registry`
--
ALTER TABLE `api_registry`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `appearance`
--
ALTER TABLE `appearance`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `articles`
--
ALTER TABLE `articles`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `audit_events`
--
ALTER TABLE `audit_events`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `bulk_transactions`
--
ALTER TABLE `bulk_transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_bulk_transactions_symbol` (`symbol`);

--
-- Indexes for table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `commodities_data`
--
ALTER TABLE `commodities_data`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `contact_messages`
--
ALTER TABLE `contact_messages`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `content_providers`
--
ALTER TABLE `content_providers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `countries`
--
ALTER TABLE `countries`
  ADD PRIMARY KEY (`code`);

--
-- Indexes for table `courses`
--
ALTER TABLE `courses`
  ADD PRIMARY KEY (`id`),
  ADD KEY `instructor_id` (`instructor_id`);

--
-- Indexes for table `course_modules`
--
ALTER TABLE `course_modules`
  ADD PRIMARY KEY (`id`),
  ADD KEY `course_id` (`course_id`);

--
-- Indexes for table `crypto_market_data`
--
ALTER TABLE `crypto_market_data`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `deposits`
--
ALTER TABLE `deposits`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `dividends`
--
ALTER TABLE `dividends`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_dividends_symbol` (`symbol`);

--
-- Indexes for table `earnings_calendar`
--
ALTER TABLE `earnings_calendar`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_symbol` (`symbol`),
  ADD KEY `idx_earnings_date` (`earnings_date`);

--
-- Indexes for table `economic_events`
--
ALTER TABLE `economic_events`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `email_templates`
--
ALTER TABLE `email_templates`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `faqs`
--
ALTER TABLE `faqs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `faq_items`
--
ALTER TABLE `faq_items`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `forex_rates`
--
ALTER TABLE `forex_rates`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `glossary_terms`
--
ALTER TABLE `glossary_terms`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `help_articles`
--
ALTER TABLE `help_articles`
  ADD PRIMARY KEY (`id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `help_categories`
--
ALTER TABLE `help_categories`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `instructors`
--
ALTER TABLE `instructors`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `jobs`
--
ALTER TABLE `jobs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `job_listings`
--
ALTER TABLE `job_listings`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `login_events`
--
ALTER TABLE `login_events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `marketing_campaigns`
--
ALTER TABLE `marketing_campaigns`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `market_cache`
--
ALTER TABLE `market_cache`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `cache_key` (`cache_key`);

--
-- Indexes for table `market_data`
--
ALTER TABLE `market_data`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_market_data_symbol` (`symbol`);

--
-- Indexes for table `market_indices`
--
ALTER TABLE `market_indices`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `symbol` (`symbol`);

--
-- Indexes for table `market_sentiment`
--
ALTER TABLE `market_sentiment`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `navigation_items`
--
ALTER TABLE `navigation_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `parent_id` (`parent_id`);

--
-- Indexes for table `nav_metrics`
--
ALTER TABLE `nav_metrics`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `news_items`
--
ALTER TABLE `news_items`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `order_number` (`order_number`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `order_items`
--
ALTER TABLE `order_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `pages`
--
ALTER TABLE `pages`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `slug` (`slug`);

--
-- Indexes for table `paper_holdings`
--
ALTER TABLE `paper_holdings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `account_id` (`account_id`);

--
-- Indexes for table `paper_trading_accounts`
--
ALTER TABLE `paper_trading_accounts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `paper_transactions`
--
ALTER TABLE `paper_transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `account_id` (`account_id`);

--
-- Indexes for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `token` (`token`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `portfolio_holdings`
--
ALTER TABLE `portfolio_holdings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `portfolio_id` (`portfolio_id`);

--
-- Indexes for table `portfolio_transactions`
--
ALTER TABLE `portfolio_transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `portfolio_id` (`portfolio_id`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `category_id` (`category_id`);

--
-- Indexes for table `post_categories`
--
ALTER TABLE `post_categories`
  ADD PRIMARY KEY (`id`),
  ADD KEY `parent_id` (`parent_id`);

--
-- Indexes for table `pricing`
--
ALTER TABLE `pricing`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `providers`
--
ALTER TABLE `providers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `quizzes`
--
ALTER TABLE `quizzes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `module_id` (`module_id`);

--
-- Indexes for table `quiz_answers`
--
ALTER TABLE `quiz_answers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `attempt_id` (`attempt_id`),
  ADD KEY `question_id` (`question_id`);

--
-- Indexes for table `quiz_attempts`
--
ALTER TABLE `quiz_attempts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `quiz_id` (`quiz_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `quiz_questions`
--
ALTER TABLE `quiz_questions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `quiz_id` (`quiz_id`);

--
-- Indexes for table `radio_stations`
--
ALTER TABLE `radio_stations`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `rss_feeds`
--
ALTER TABLE `rss_feeds`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `rss_items`
--
ALTER TABLE `rss_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `feed_id` (`feed_id`);

--
-- Indexes for table `sellers`
--
ALTER TABLE `sellers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `seller_applications`
--
ALTER TABLE `seller_applications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `seller_categories`
--
ALTER TABLE `seller_categories`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `service_features`
--
ALTER TABLE `service_features`
  ADD PRIMARY KEY (`id`),
  ADD KEY `service_id` (`service_id`);

--
-- Indexes for table `settings`
--
ALTER TABLE `settings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `key` (`key`);

--
-- Indexes for table `sports_events`
--
ALTER TABLE `sports_events`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `stock_offers`
--
ALTER TABLE `stock_offers`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `stock_price_history`
--
ALTER TABLE `stock_price_history`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_symbol_date_interval` (`symbol`,`date`,`interval`),
  ADD KEY `idx_symbol` (`symbol`),
  ADD KEY `idx_date` (`date`);

--
-- Indexes for table `stock_splits`
--
ALTER TABLE `stock_splits`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_symbol` (`symbol`),
  ADD KEY `idx_split_date` (`split_date`);

--
-- Indexes for table `subscribers`
--
ALTER TABLE `subscribers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `tasks`
--
ALTER TABLE `tasks`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `team_members`
--
ALTER TABLE `team_members`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `testimonials`
--
ALTER TABLE `testimonials`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tool_settings`
--
ALTER TABLE `tool_settings`
  ADD PRIMARY KEY (`tool_slug`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `trending_topics`
--
ALTER TABLE `trending_topics`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tv_channels`
--
ALTER TABLE `tv_channels`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `user_activities`
--
ALTER TABLE `user_activities`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_alerts`
--
ALTER TABLE `user_alerts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_dashboard_config`
--
ALTER TABLE `user_dashboard_config`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_devices`
--
ALTER TABLE `user_devices`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_documents`
--
ALTER TABLE `user_documents`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_economic_events`
--
ALTER TABLE `user_economic_events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_enrollments`
--
ALTER TABLE `user_enrollments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `course_id` (`course_id`),
  ADD KEY `current_module_id` (`current_module_id`);

--
-- Indexes for table `user_notification_prefs`
--
ALTER TABLE `user_notification_prefs`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_portfolios`
--
ALTER TABLE `user_portfolios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_saved_terms`
--
ALTER TABLE `user_saved_terms`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_sessions`
--
ALTER TABLE `user_sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `user_watchlist`
--
ALTER TABLE `user_watchlist`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `vendors`
--
ALTER TABLE `vendors`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `vendor_api_keys`
--
ALTER TABLE `vendor_api_keys`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `api_key` (`api_key`),
  ADD KEY `vendor_id` (`vendor_id`);

--
-- Indexes for table `vendor_custom_apis`
--
ALTER TABLE `vendor_custom_apis`
  ADD PRIMARY KEY (`id`),
  ADD KEY `vendor_id` (`vendor_id`);

--
-- Indexes for table `watchlists`
--
ALTER TABLE `watchlists`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `watchlist_items`
--
ALTER TABLE `watchlist_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `watchlist_id` (`watchlist_id`);

--
-- Indexes for table `wealth_state`
--
ALTER TABLE `wealth_state`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `webinars`
--
ALTER TABLE `webinars`
  ADD PRIMARY KEY (`id`),
  ADD KEY `host_id` (`host_id`);

--
-- Indexes for table `webinar_attendance`
--
ALTER TABLE `webinar_attendance`
  ADD PRIMARY KEY (`id`),
  ADD KEY `webinar_id` (`webinar_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `withdrawals`
--
ALTER TABLE `withdrawals`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `analyst_recommendations`
--
ALTER TABLE `analyst_recommendations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `bulk_transactions`
--
ALTER TABLE `bulk_transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `commodities_data`
--
ALTER TABLE `commodities_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT for table `courses`
--
ALTER TABLE `courses`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `course_modules`
--
ALTER TABLE `course_modules`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=61;

--
-- AUTO_INCREMENT for table `crypto_market_data`
--
ALTER TABLE `crypto_market_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `dividends`
--
ALTER TABLE `dividends`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=46;

--
-- AUTO_INCREMENT for table `earnings_calendar`
--
ALTER TABLE `earnings_calendar`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `faq_items`
--
ALTER TABLE `faq_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `forex_rates`
--
ALTER TABLE `forex_rates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `glossary_terms`
--
ALTER TABLE `glossary_terms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `help_articles`
--
ALTER TABLE `help_articles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `help_categories`
--
ALTER TABLE `help_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `instructors`
--
ALTER TABLE `instructors`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `job_listings`
--
ALTER TABLE `job_listings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `market_data`
--
ALTER TABLE `market_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=126;

--
-- AUTO_INCREMENT for table `market_indices`
--
ALTER TABLE `market_indices`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=62;

--
-- AUTO_INCREMENT for table `market_sentiment`
--
ALTER TABLE `market_sentiment`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `navigation_items`
--
ALTER TABLE `navigation_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `nav_metrics`
--
ALTER TABLE `nav_metrics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `news_items`
--
ALTER TABLE `news_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT for table `order_items`
--
ALTER TABLE `order_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `post_categories`
--
ALTER TABLE `post_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `pricing`
--
ALTER TABLE `pricing`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quizzes`
--
ALTER TABLE `quizzes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quiz_answers`
--
ALTER TABLE `quiz_answers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quiz_attempts`
--
ALTER TABLE `quiz_attempts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `quiz_questions`
--
ALTER TABLE `quiz_questions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `radio_stations`
--
ALTER TABLE `radio_stations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `seller_categories`
--
ALTER TABLE `seller_categories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `services`
--
ALTER TABLE `services`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `service_features`
--
ALTER TABLE `service_features`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `sports_events`
--
ALTER TABLE `sports_events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `stock_price_history`
--
ALTER TABLE `stock_price_history`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `stock_splits`
--
ALTER TABLE `stock_splits`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `subscribers`
--
ALTER TABLE `subscribers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `team_members`
--
ALTER TABLE `team_members`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `testimonials`
--
ALTER TABLE `testimonials`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `trending_topics`
--
ALTER TABLE `trending_topics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `user_dashboard_config`
--
ALTER TABLE `user_dashboard_config`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_economic_events`
--
ALTER TABLE `user_economic_events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_enrollments`
--
ALTER TABLE `user_enrollments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `user_notification_prefs`
--
ALTER TABLE `user_notification_prefs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_saved_terms`
--
ALTER TABLE `user_saved_terms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_watchlist`
--
ALTER TABLE `user_watchlist`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `watchlist_items`
--
ALTER TABLE `watchlist_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `wealth_state`
--
ALTER TABLE `wealth_state`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `webinar_attendance`
--
ALTER TABLE `webinar_attendance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `courses`
--
ALTER TABLE `courses`
  ADD CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`instructor_id`) REFERENCES `instructors` (`id`);

--
-- Constraints for table `course_modules`
--
ALTER TABLE `course_modules`
  ADD CONSTRAINT `course_modules_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`);

--
-- Constraints for table `deposits`
--
ALTER TABLE `deposits`
  ADD CONSTRAINT `deposits_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `help_articles`
--
ALTER TABLE `help_articles`
  ADD CONSTRAINT `help_articles_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `help_categories` (`id`);

--
-- Constraints for table `login_events`
--
ALTER TABLE `login_events`
  ADD CONSTRAINT `login_events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `navigation_items`
--
ALTER TABLE `navigation_items`
  ADD CONSTRAINT `navigation_items_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `navigation_items` (`id`);

--
-- Constraints for table `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `order_items`
--
ALTER TABLE `order_items`
  ADD CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`);

--
-- Constraints for table `paper_holdings`
--
ALTER TABLE `paper_holdings`
  ADD CONSTRAINT `paper_holdings_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `paper_trading_accounts` (`id`);

--
-- Constraints for table `paper_trading_accounts`
--
ALTER TABLE `paper_trading_accounts`
  ADD CONSTRAINT `paper_trading_accounts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `paper_transactions`
--
ALTER TABLE `paper_transactions`
  ADD CONSTRAINT `paper_transactions_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `paper_trading_accounts` (`id`);

--
-- Constraints for table `password_reset_tokens`
--
ALTER TABLE `password_reset_tokens`
  ADD CONSTRAINT `password_reset_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `portfolio_holdings`
--
ALTER TABLE `portfolio_holdings`
  ADD CONSTRAINT `portfolio_holdings_ibfk_1` FOREIGN KEY (`portfolio_id`) REFERENCES `user_portfolios` (`id`);

--
-- Constraints for table `portfolio_transactions`
--
ALTER TABLE `portfolio_transactions`
  ADD CONSTRAINT `portfolio_transactions_ibfk_1` FOREIGN KEY (`portfolio_id`) REFERENCES `user_portfolios` (`id`);

--
-- Constraints for table `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `post_categories` (`id`);

--
-- Constraints for table `post_categories`
--
ALTER TABLE `post_categories`
  ADD CONSTRAINT `post_categories_ibfk_1` FOREIGN KEY (`parent_id`) REFERENCES `post_categories` (`id`);

--
-- Constraints for table `quizzes`
--
ALTER TABLE `quizzes`
  ADD CONSTRAINT `quizzes_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  ADD CONSTRAINT `quizzes_ibfk_2` FOREIGN KEY (`module_id`) REFERENCES `course_modules` (`id`);

--
-- Constraints for table `quiz_answers`
--
ALTER TABLE `quiz_answers`
  ADD CONSTRAINT `quiz_answers_ibfk_1` FOREIGN KEY (`attempt_id`) REFERENCES `quiz_attempts` (`id`),
  ADD CONSTRAINT `quiz_answers_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `quiz_questions` (`id`);

--
-- Constraints for table `quiz_attempts`
--
ALTER TABLE `quiz_attempts`
  ADD CONSTRAINT `quiz_attempts_ibfk_1` FOREIGN KEY (`quiz_id`) REFERENCES `quizzes` (`id`),
  ADD CONSTRAINT `quiz_attempts_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `quiz_questions`
--
ALTER TABLE `quiz_questions`
  ADD CONSTRAINT `quiz_questions_ibfk_1` FOREIGN KEY (`quiz_id`) REFERENCES `quizzes` (`id`);

--
-- Constraints for table `rss_items`
--
ALTER TABLE `rss_items`
  ADD CONSTRAINT `rss_items_ibfk_1` FOREIGN KEY (`feed_id`) REFERENCES `rss_feeds` (`id`);

--
-- Constraints for table `sellers`
--
ALTER TABLE `sellers`
  ADD CONSTRAINT `sellers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `seller_applications`
--
ALTER TABLE `seller_applications`
  ADD CONSTRAINT `seller_applications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `service_features`
--
ALTER TABLE `service_features`
  ADD CONSTRAINT `service_features_ibfk_1` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`);

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_activities`
--
ALTER TABLE `user_activities`
  ADD CONSTRAINT `user_activities_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_alerts`
--
ALTER TABLE `user_alerts`
  ADD CONSTRAINT `user_alerts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_dashboard_config`
--
ALTER TABLE `user_dashboard_config`
  ADD CONSTRAINT `user_dashboard_config_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_devices`
--
ALTER TABLE `user_devices`
  ADD CONSTRAINT `user_devices_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_documents`
--
ALTER TABLE `user_documents`
  ADD CONSTRAINT `user_documents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_economic_events`
--
ALTER TABLE `user_economic_events`
  ADD CONSTRAINT `user_economic_events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_enrollments`
--
ALTER TABLE `user_enrollments`
  ADD CONSTRAINT `user_enrollments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `user_enrollments_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`),
  ADD CONSTRAINT `user_enrollments_ibfk_3` FOREIGN KEY (`current_module_id`) REFERENCES `course_modules` (`id`);

--
-- Constraints for table `user_notification_prefs`
--
ALTER TABLE `user_notification_prefs`
  ADD CONSTRAINT `user_notification_prefs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_portfolios`
--
ALTER TABLE `user_portfolios`
  ADD CONSTRAINT `user_portfolios_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_saved_terms`
--
ALTER TABLE `user_saved_terms`
  ADD CONSTRAINT `user_saved_terms_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_sessions`
--
ALTER TABLE `user_sessions`
  ADD CONSTRAINT `user_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `user_watchlist`
--
ALTER TABLE `user_watchlist`
  ADD CONSTRAINT `user_watchlist_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `vendor_api_keys`
--
ALTER TABLE `vendor_api_keys`
  ADD CONSTRAINT `vendor_api_keys_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`);

--
-- Constraints for table `vendor_custom_apis`
--
ALTER TABLE `vendor_custom_apis`
  ADD CONSTRAINT `vendor_custom_apis_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `vendors` (`id`);

--
-- Constraints for table `watchlists`
--
ALTER TABLE `watchlists`
  ADD CONSTRAINT `watchlists_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `watchlist_items`
--
ALTER TABLE `watchlist_items`
  ADD CONSTRAINT `watchlist_items_ibfk_1` FOREIGN KEY (`watchlist_id`) REFERENCES `watchlists` (`id`);

--
-- Constraints for table `wealth_state`
--
ALTER TABLE `wealth_state`
  ADD CONSTRAINT `wealth_state_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `webinars`
--
ALTER TABLE `webinars`
  ADD CONSTRAINT `webinars_ibfk_1` FOREIGN KEY (`host_id`) REFERENCES `instructors` (`id`);

--
-- Constraints for table `webinar_attendance`
--
ALTER TABLE `webinar_attendance`
  ADD CONSTRAINT `webinar_attendance_ibfk_1` FOREIGN KEY (`webinar_id`) REFERENCES `webinars` (`id`),
  ADD CONSTRAINT `webinar_attendance_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `withdrawals`
--
ALTER TABLE `withdrawals`
  ADD CONSTRAINT `withdrawals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
