-- Migration: Add all tools to tool_settings table
-- This script adds all tools from the old frontend with proper categorization
-- Existing tools implemented: marked as is_implemented = true
-- Coming soon tools: marked as is_implemented = false

-- Delete existing entries to avoid duplicates (optional - comment out if you want to preserve existing)
-- DELETE FROM tool_settings WHERE country_code = 'GLOBAL';

-- Upsert all tools using INSERT ... ON CONFLICT
-- PostgreSQL-compatible syntax

-- ===== INVESTING TOOLS (Implemented) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('sip', 'SIP Calculator', 'Investing', true, 1, true, 'GLOBAL'),
('compound', 'Compound Interest Calculator', 'Investing', true, 2, true, 'GLOBAL'),
('lumpsum', 'Lumpsum Calculator', 'Investing', true, 3, true, 'GLOBAL'),
('step-up-sip', 'Step-Up SIP Calculator', 'Investing', true, 4, true, 'GLOBAL'),
('cagr', 'CAGR Calculator', 'Investing', true, 5, true, 'GLOBAL'),
('dividend-yield', 'Dividend Yield Calculator', 'Investing', true, 6, true, 'GLOBAL'),
('ppf', 'PPF Calculator', 'Investing', true, 7, true, 'GLOBAL'),
('fd', 'FD Calculator', 'Investing', true, 8, true, 'GLOBAL'),
('rd', 'RD Calculator', 'Investing', true, 9, true, 'GLOBAL'),
('nsc', 'NSC Calculator', 'Investing', true, 10, true, 'GLOBAL'),
('ssy', 'SSY Calculator', 'Investing', true, 11, true, 'GLOBAL'),
('elss', 'ELSS Calculator', 'Investing', true, 12, true, 'GLOBAL'),
('gold-investment', 'Gold Investment Calculator', 'Investing', true, 13, true, 'GLOBAL'),
('swp', 'SWP Calculator', 'Investing', true, 14, true, 'GLOBAL'),
('roi-calculator', 'ROI Calculator', 'Investing', true, 15, true, 'GLOBAL'),
('goal-planner', 'Goal Planner', 'Investing', true, 16, true, 'GLOBAL'),
('risk-level-assessment', 'Risk Level Assessment', 'Investing', true, 17, false, 'GLOBAL'),
('volatility-measurement', 'Volatility Measurement', 'Investing', true, 18, false, 'GLOBAL'),
('beta-calculator', 'Beta Calculator', 'Investing', true, 19, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    enabled = EXCLUDED.enabled,
    is_implemented = EXCLUDED.is_implemented;

-- ===== RETIREMENT TOOLS (Implemented) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('retirement', 'Retirement Calculator', 'Retirement', true, 1, true, 'GLOBAL'),
('epf', 'EPF Calculator', 'Retirement', true, 2, true, 'GLOBAL'),
('nps', 'NPS Calculator', 'Retirement', true, 3, true, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== PORTFOLIO ANALYSIS (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('correlation-matrix', 'Correlation Matrix', 'Portfolio Analysis', true, 1, false, 'GLOBAL'),
('fee-analyzer', 'Investment Fee Analyzer', 'Portfolio Analysis', true, 2, false, 'GLOBAL'),
('etf-overlap', 'ETF Overlap Checker', 'Portfolio Analysis', true, 3, false, 'GLOBAL'),
('esg-scoring', 'ESG Scoring Dashboard', 'Portfolio Analysis', true, 4, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== FINANCE & LOANS (Implemented) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('emi', 'Loan EMI Calculator', 'Finance & Loans', true, 1, true, 'GLOBAL'),
('mortgage', 'Mortgage Calculator', 'Real Estate', true, 2, true, 'GLOBAL'),
('car-loan', 'Car Loan Calculator', 'Finance & Loans', true, 3, true, 'GLOBAL'),
('education-loan', 'Education Loan Calculator', 'Education', true, 4, true, 'GLOBAL'),
('loan-compare', 'Loan Comparison', 'Finance & Loans', true, 5, true, 'GLOBAL'),
('budget-planner', 'Budget Planner', 'Personal Finance', true, 6, true, 'GLOBAL'),
('income-tax', 'Income Tax Calculator', 'Taxation', true, 7, true, 'GLOBAL'),
('gst', 'GST Calculator', 'Taxation', true, 8, true, 'GLOBAL'),
('hra', 'HRA Calculator', 'Taxation', true, 9, true, 'GLOBAL'),
('inflation', 'Inflation Calculator', 'Personal Finance', true, 10, true, 'GLOBAL'),
('salary-converter', 'Salary Converter', 'Personal Finance', true, 11, true, 'GLOBAL'),
('debt-payoff', 'Debt Payoff Calculator', 'Debt', true, 12, true, 'GLOBAL'),
('credit-card-payoff', 'Credit Card Payoff', 'Debt', true, 13, true, 'GLOBAL'),
('emergency-fund', 'Emergency Fund Calculator', 'Personal Finance', true, 14, true, 'GLOBAL'),
('net-worth', 'Net Worth Calculator', 'Personal Finance', true, 15, true, 'GLOBAL'),
('rent-vs-buy', 'Rent vs Buy Calculator', 'Real Estate', true, 16, true, 'GLOBAL'),
('stamp-duty', 'Stamp Duty Calculator', 'Real Estate', true, 17, true, 'GLOBAL'),
('education-cost', 'Education Cost Planner', 'Education', true, 18, true, 'GLOBAL'),
('equity-dilution', 'Equity Dilution Calculator', 'Business', true, 19, true, 'GLOBAL'),
('break-even', 'Break-Even Calculator', 'Business', true, 20, true, 'GLOBAL'),
('margin', 'Profit Margin Calculator', 'Business', true, 21, true, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== INSURANCE (Implemented + Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('life-insurance', 'Life Insurance Needs', 'Insurance', true, 1, true, 'GLOBAL'),
('car-insurance', 'Car Insurance Calculator', 'Insurance', true, 2, true, 'GLOBAL'),
('health-premium', 'Health Premium Estimator', 'Insurance', true, 3, true, 'GLOBAL'),
('term-insurance', 'Term Insurance Planner', 'Insurance', true, 4, false, 'GLOBAL'),
('term-life', 'Term Life Calculator', 'Insurance', true, 5, false, 'GLOBAL'),
('human-life-value', 'Human Life Value', 'Insurance', true, 6, false, 'GLOBAL'),
('nri-term', 'NRI Term Calculator', 'Insurance', true, 7, false, 'GLOBAL'),
('parents-health', 'Parents Health Cover', 'Insurance', true, 8, false, 'GLOBAL'),
('bike-insurance', 'Bike Insurance Calculator', 'Insurance', true, 9, false, 'GLOBAL'),
('travel-insurance', 'Travel Insurance Calculator', 'Insurance', true, 10, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== HEALTH & FITNESS (Implemented) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('bmi-calculator', 'BMI Calculator', 'Health & Fitness', true, 1, true, 'GLOBAL'),
('calorie-calculator', 'Calorie Calculator', 'Health & Fitness', true, 2, true, 'GLOBAL'),
('ideal-weight', 'Ideal Weight Calculator', 'Health & Fitness', true, 3, true, 'GLOBAL'),
('water-intake', 'Water Intake Calculator', 'Health & Fitness', true, 4, true, 'GLOBAL'),
('sleep', 'Sleep Calculator', 'Health & Fitness', true, 5, true, 'GLOBAL'),
('pregnancy-due-date', 'Pregnancy Due Date', 'Health & Fitness', true, 6, true, 'GLOBAL'),
('macro-nutrient-calculator', 'Macro Nutrient Calculator', 'Health & Fitness', true, 7, false, 'GLOBAL'),
('one-rep-max', 'One Rep Max Calculator', 'Health & Fitness', true, 8, false, 'GLOBAL'),
('target-heart-rate', 'Target Heart Rate Calculator', 'Health & Fitness', true, 9, false, 'GLOBAL'),
('body-fat-percentage', 'Body Fat Percentage Calculator', 'Health & Fitness', true, 10, false, 'GLOBAL'),
('running-pace', 'Running Pace Calculator', 'Health & Fitness', true, 11, false, 'GLOBAL'),
('meal-planner', 'Meal Planner Generator', 'Health & Fitness', true, 12, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== UTILITIES (Implemented) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('currency-converter', 'Currency Converter', 'Utilities', true, 1, true, 'GLOBAL'),
('password-generator', 'Password Generator', 'Security', true, 2, true, 'GLOBAL'),
('age-calculator', 'Age Calculator', 'Utilities', true, 3, true, 'GLOBAL'),
('percentage', 'Percentage Calculator', 'Utilities', true, 4, true, 'GLOBAL'),
('tip', 'Tip Calculator', 'Utilities', true, 5, true, 'GLOBAL'),
('fuel-cost', 'Fuel Cost Calculator', 'Utilities', true, 6, true, 'GLOBAL'),
('date-difference', 'Date Difference Calculator', 'Utilities', true, 7, true, 'GLOBAL'),
('unit-converter', 'Unit Converter', 'Utilities', true, 8, true, 'GLOBAL'),
('time-zone-converter', 'Time Zone Converter', 'Utilities', true, 9, false, 'GLOBAL'),
('countdown-timer', 'Countdown Timer', 'Utilities', true, 10, false, 'GLOBAL'),
('decision-maker', 'Decision Maker', 'Utilities', true, 11, false, 'GLOBAL'),
('url-shortener', 'URL Shortener', 'Utilities', true, 12, false, 'GLOBAL'),
('ip-address-lookup', 'IP Address Lookup', 'Utilities', true, 13, false, 'GLOBAL'),
('pdf-to-word', 'PDF to Word Converter', 'Utilities', true, 14, false, 'GLOBAL'),
('file-format-converter', 'File Format Converter', 'Utilities', true, 15, false, 'GLOBAL'),
('language-translator', 'Language Translator', 'Utilities', true, 16, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== REAL ESTATE (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('mortgage-affordability', 'Mortgage Affordability', 'Real Estate', true, 1, false, 'GLOBAL'),
('home-loan-comparison', 'Home Loan Comparison', 'Real Estate', true, 2, false, 'GLOBAL'),
('moving-cost', 'Moving Cost Calculator', 'Real Estate', true, 3, false, 'GLOBAL'),
('square-footage', 'Square Footage Calculator', 'Real Estate', true, 4, false, 'GLOBAL'),
('paint-calculator', 'Paint Calculator', 'Real Estate', true, 5, false, 'GLOBAL'),
('mortgage-refinance', 'Mortgage Refinance Calculator', 'Real Estate', true, 6, false, 'GLOBAL'),
('home-value-estimator', 'Home Value Estimator', 'Real Estate', true, 7, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== PRODUCTIVITY (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('pomodoro-timer', 'Pomodoro Timer', 'Productivity', true, 1, false, 'GLOBAL'),
('habit-tracker', 'Habit Tracker', 'Productivity', true, 2, false, 'GLOBAL'),
('task-priority-matrix', 'Task Priority Matrix', 'Productivity', true, 3, false, 'GLOBAL'),
('goal-setting-template', 'Goal Setting Template', 'Productivity', true, 4, false, 'GLOBAL'),
('mind-map-generator', 'Mind Map Generator', 'Productivity', true, 5, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== TRAVEL (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('trip-cost', 'Trip Cost Calculator', 'Travel', true, 1, false, 'GLOBAL'),
('travel-itinerary', 'Travel Itinerary Builder', 'Travel', true, 2, false, 'GLOBAL'),
('packing-list', 'Packing List Generator', 'Travel', true, 3, false, 'GLOBAL'),
('flight-price-tracker', 'Flight Price Tracker', 'Travel', true, 4, false, 'GLOBAL'),
('mileage-calculator', 'Mileage Calculator', 'Travel', true, 5, false, 'GLOBAL'),
('travel-destination-quiz', 'Where Should I Travel Quiz', 'Travel', true, 6, false, 'GLOBAL'),
('airport-code-lookup', 'Airport Code Lookup', 'Travel', true, 7, false, 'GLOBAL'),
('visa-requirement-checker', 'Visa Requirement Checker', 'Travel', true, 8, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== COOKING & RECIPES (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('recipe-nutrition', 'Recipe Nutrition Calculator', 'Cooking & Recipes', true, 1, false, 'GLOBAL'),
('meal-calorie', 'Meal Calorie Calculator', 'Cooking & Recipes', true, 2, false, 'GLOBAL'),
('recipe-scaler', 'Recipe Scaler', 'Cooking & Recipes', true, 3, false, 'GLOBAL'),
('substitution-finder', 'Substitution Finder', 'Cooking & Recipes', true, 4, false, 'GLOBAL'),
('baking-pan-converter', 'Baking Pan Size Converter', 'Cooking & Recipes', true, 5, false, 'GLOBAL'),
('what-can-i-make', 'What Can I Make Tool', 'Cooking & Recipes', true, 6, false, 'GLOBAL'),
('wine-pairing', 'Wine Pairing Helper', 'Cooking & Recipes', true, 7, false, 'GLOBAL'),
('cooking-timer', 'Cooking Timer', 'Cooking & Recipes', true, 8, false, 'GLOBAL'),
('grocery-list', 'Grocery List Generator', 'Cooking & Recipes', true, 9, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== MARKETING (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('email-subject-tester', 'Email Subject Line Tester', 'Marketing', true, 1, false, 'GLOBAL'),
('social-bio-generator', 'Social Media Bio Generator', 'Marketing', true, 2, false, 'GLOBAL'),
('cpc-calculator', 'CPC Calculator', 'Marketing', true, 3, false, 'GLOBAL'),
('hashtag-generator', 'Hashtag Generator', 'Marketing', true, 4, false, 'GLOBAL'),
('instagram-caption', 'Instagram Caption Generator', 'Marketing', true, 5, false, 'GLOBAL'),
('linkedin-headline', 'LinkedIn Headline Generator', 'Marketing', true, 6, false, 'GLOBAL'),
('tiktok-idea-generator', 'TikTok Video Idea Generator', 'Marketing', true, 7, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== SEO (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('keyword-difficulty', 'Keyword Difficulty Checker', 'SEO', true, 1, false, 'GLOBAL'),
('meta-tag-generator', 'Meta Tag Generator', 'SEO', true, 2, false, 'GLOBAL'),
('backlink-analyzer', 'Backlink Analyzer', 'SEO', true, 3, false, 'GLOBAL'),
('serp-preview', 'SERP Preview Tool', 'SEO', true, 4, false, 'GLOBAL'),
('website-rank-checker', 'Website Rank Checker', 'SEO', true, 5, false, 'GLOBAL'),
('readability-analyzer', 'Content Readability Analyzer', 'SEO', true, 6, false, 'GLOBAL'),
('sitemap-generator', 'Sitemap Generator', 'SEO', true, 7, false, 'GLOBAL'),
('robots-txt-tester', 'Robots.txt Tester', 'SEO', true, 8, false, 'GLOBAL'),
('website-speed-test', 'Website Speed Test', 'SEO', true, 9, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== E-COMMERCE (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('profit-margin', 'Profit Margin Calculator', 'E-commerce', true, 1, false, 'GLOBAL'),
('shipping-cost', 'Shipping Cost Calculator', 'E-commerce', true, 2, false, 'GLOBAL'),
('product-description', 'Product Description Generator', 'E-commerce', true, 3, false, 'GLOBAL'),
('sales-tax', 'Sales Tax Calculator', 'E-commerce', true, 4, false, 'GLOBAL'),
('amazon-fba-fee', 'Amazon FBA Fee Calculator', 'E-commerce', true, 5, false, 'GLOBAL'),
('dropshipping-profit', 'Dropshipping Profit Calculator', 'E-commerce', true, 6, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== LEGAL (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('legal-document-generator', 'Legal Document Generator', 'Legal', true, 1, false, 'GLOBAL'),
('bill-of-sale', 'Bill of Sale Generator', 'Legal', true, 2, false, 'GLOBAL'),
('lease-agreement', 'Lease Agreement Generator', 'Legal', true, 3, false, 'GLOBAL'),
('legal-word-counter', 'Legal Word Counter', 'Legal', true, 4, false, 'GLOBAL'),
('statute-of-limitations', 'Statute of Limitations Checker', 'Legal', true, 5, false, 'GLOBAL'),
('power-of-attorney', 'Power of Attorney Generator', 'Legal', true, 6, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== GAMING (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('character-name-generator', 'Character Name Generator', 'Gaming', true, 1, false, 'GLOBAL'),
('loot-drop-chance', 'Loot Drop Chance Calculator', 'Gaming', true, 2, false, 'GLOBAL'),
('game-fps-calculator', 'Game Frame Rate Calculator', 'Gaming', true, 3, false, 'GLOBAL'),
('team-composition', 'Team Composition Builder', 'Gaming', true, 4, false, 'GLOBAL'),
('xp-calculator', 'Experience Calculator', 'Gaming', true, 5, false, 'GLOBAL'),
('random-dungeon', 'Random Dungeon Generator', 'Gaming', true, 6, false, 'GLOBAL'),
('speedrun-timer', 'Speedrunning Timer', 'Gaming', true, 7, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== DATA & CODE (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('json-formatter', 'JSON Formatter', 'Data & Code', true, 1, false, 'GLOBAL'),
('code-beautifier', 'Code Beautifier/Minifier', 'Data & Code', true, 2, false, 'GLOBAL'),
('sql-query-generator', 'SQL Query Generator', 'Data & Code', true, 3, false, 'GLOBAL'),
('api-request-builder', 'API Request Builder', 'Data & Code', true, 4, false, 'GLOBAL'),
('csv-to-json', 'CSV to JSON Converter', 'Data & Code', true, 5, false, 'GLOBAL'),
('user-agent-parser', 'User Agent Parser', 'Data & Code', true, 6, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== DESIGN (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('color-palette', 'Color Palette Generator', 'Design', true, 1, false, 'GLOBAL'),
('font-pairing', 'Font Pairing Tool', 'Design', true, 2, false, 'GLOBAL'),
('logo-maker', 'Logo Maker', 'Design', true, 3, false, 'GLOBAL'),
('image-background-remover', 'Image Background Remover', 'Design', true, 4, false, 'GLOBAL'),
('qr-code-generator', 'QR Code Generator', 'Design', true, 5, false, 'GLOBAL'),
('gradient-generator', 'Gradient Generator', 'Design', true, 6, false, 'GLOBAL'),
('color-picker', 'Color Picker', 'Design', true, 7, false, 'GLOBAL'),
('image-compressor', 'Image Compressor', 'Design', true, 8, false, 'GLOBAL'),
('social-image-resizer', 'Social Media Image Resizer', 'Design', true, 9, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== WRITING (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('word-counter', 'Word Counter', 'Writing', true, 1, false, 'GLOBAL'),
('reading-time', 'Reading Time Calculator', 'Writing', true, 2, false, 'GLOBAL'),
('text-summarizer', 'Text Summarizer', 'Writing', true, 3, false, 'GLOBAL'),
('case-converter', 'Case Converter', 'Writing', true, 4, false, 'GLOBAL'),
('lorem-ipsum', 'Lorem Ipsum Generator', 'Writing', true, 5, false, 'GLOBAL'),
('grammar-checker', 'Grammar & Spell Checker', 'Writing', true, 6, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== CONTENT (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('youtube-title-generator', 'YouTube Title Generator', 'Content', true, 1, false, 'GLOBAL'),
('twitter-thread', 'Twitter Thread Generator', 'Content', true, 2, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== EDUCATION & STUDY (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('gpa-calculator', 'GPA Calculator', 'Education & Study', true, 1, false, 'GLOBAL'),
('citation-generator', 'Citation Generator', 'Education & Study', true, 2, false, 'GLOBAL'),
('plagiarism-checker', 'Plagiarism Checker', 'Education & Study', true, 3, false, 'GLOBAL'),
('flashcards', 'Flashcards Generator', 'Education & Study', true, 4, false, 'GLOBAL'),
('reading-speed-test', 'Reading Speed Test', 'Education & Study', true, 5, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== HEALTH & MEDICAL (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('symptom-checker', 'Symptom Checker', 'Health & Medical', true, 1, false, 'GLOBAL'),
('drug-interaction-checker', 'Drug Interaction Checker', 'Health & Medical', true, 2, false, 'GLOBAL'),
('pill-identifier', 'Pill Identifier', 'Health & Medical', true, 3, false, 'GLOBAL'),
('dosage-calculator', 'Dosage Calculator', 'Health & Medical', true, 4, false, 'GLOBAL'),
('heart-age-calculator', 'Heart Age Calculator', 'Health & Medical', true, 5, false, 'GLOBAL'),
('vaccination-schedule', 'Vaccination Schedule Tracker', 'Health & Medical', true, 6, false, 'GLOBAL'),
('medical-dictionary', 'Medical Dictionary Lookup', 'Health & Medical', true, 7, false, 'GLOBAL'),
('blood-alcohol-calculator', 'Blood Alcohol Calculator', 'Health & Medical', true, 8, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== FUN & ENTERTAINMENT (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('meme-generator', 'Meme Generator', 'Fun & Entertainment', true, 1, false, 'GLOBAL'),
('ascii-art', 'ASCII Art Generator', 'Fun & Entertainment', true, 2, false, 'GLOBAL'),
('love-calculator', 'Love Calculator', 'Fun & Entertainment', true, 3, false, 'GLOBAL'),
('personality-quiz', 'Personality Quiz Generator', 'Fun & Entertainment', true, 4, false, 'GLOBAL'),
('truth-or-dare', 'Truth or Dare Generator', 'Fun & Entertainment', true, 5, false, 'GLOBAL'),
('pet-name-generator', 'Pet Name Generator', 'Fun & Entertainment', true, 6, false, 'GLOBAL'),
('boredom-buster', 'Boredom Buster', 'Fun & Entertainment', true, 7, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== ENTERTAINMENT (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('what-to-watch', 'What Should I Watch Picker', 'Entertainment', true, 1, false, 'GLOBAL'),
('book-picker', 'What Book Should I Read Picker', 'Entertainment', true, 2, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== BUSINESS (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('meeting-cost-calculator', 'Meeting Cost Calculator', 'Business Operations', true, 1, false, 'GLOBAL'),
('project-timeline-generator', 'Project Timeline Generator', 'Project Management', true, 2, false, 'GLOBAL'),
('invoice-generator', 'Invoice Generator', 'Business Operations', true, 3, false, 'GLOBAL'),
('swot-analysis', 'SWOT Analysis Generator', 'Business Strategy', true, 4, false, 'GLOBAL'),
('business-name-generator', 'Business Name Generator', 'Startup', true, 5, false, 'GLOBAL'),
('markup-margin', 'Markup & Margin Calculator', 'Business Operations', true, 6, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== SECURITY (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('ssl-checker', 'SSL Checker', 'Security', true, 1, false, 'GLOBAL'),
('password-strength', 'Password Strength Checker', 'Security', true, 2, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== INCOME & EMPLOYMENT (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('work-hours', 'Work Hours Calculator', 'Income & Employment', true, 1, false, 'GLOBAL'),
('salary-comparison', 'Salary Comparison Tool', 'Income & Employment', true, 2, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== FAMILY & GOALS (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('baby-name-generator', 'Baby Name Generator', 'Family & Goals', true, 1, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== MATH & SCIENCE (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('equation-solver', 'Equation Solver', 'Math & Science', true, 1, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== WEATHER & ASTRONOMY (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('weather-comparison', 'Weather Comparison Tool', 'Weather & Astronomy', true, 1, false, 'GLOBAL'),
('sunrise-sunset', 'Sunrise/Sunset Calculator', 'Weather & Astronomy', true, 2, false, 'GLOBAL'),
('moon-phase', 'Moon Phase Calendar', 'Weather & Astronomy', true, 3, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== SUSTAINABILITY (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('carbon-footprint', 'Carbon Footprint Calculator', 'Sustainability', true, 1, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== WELLNESS (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('gratitude-journal', 'Gratitude Journal Prompts', 'Wellness', true, 1, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== ADDITIONAL TAXATION (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('tax-refund-estimator', 'Tax Refund Estimator', 'Taxation', true, 10, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;

-- ===== ADDITIONAL DEBT (Coming Soon) =====
INSERT INTO tool_settings (tool_slug, tool_name, category, enabled, order_index, is_implemented, country_code)
VALUES
('debt-snowball-avalanche', 'Debt Snowball vs Avalanche', 'Debt', true, 14, false, 'GLOBAL')
ON CONFLICT (tool_slug) DO UPDATE SET 
    tool_name = EXCLUDED.tool_name,
    category = EXCLUDED.category,
    is_implemented = EXCLUDED.is_implemented;
