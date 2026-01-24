"""
Migration Script: Add All Tools to Database
Run this script to populate the tool_settings table with all tools
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.base import db
from models.settings import ToolSettings
from datetime import datetime

# Tool definitions organized by category
TOOLS = [
    # ===== INVESTING (Implemented) =====
    ('sip', 'SIP Calculator', 'Investing', True, 1),
    ('compound', 'Compound Interest Calculator', 'Investing', True, 2),
    ('lumpsum', 'Lumpsum Calculator', 'Investing', True, 3),
    ('step-up-sip', 'Step-Up SIP Calculator', 'Investing', True, 4),
    ('cagr', 'CAGR Calculator', 'Investing', True, 5),
    ('dividend-yield', 'Dividend Yield Calculator', 'Investing', True, 6),
    ('ppf', 'PPF Calculator', 'Investing', True, 7),
    ('fd', 'FD Calculator', 'Investing', True, 8),
    ('rd', 'RD Calculator', 'Investing', True, 9),
    ('nsc', 'NSC Calculator', 'Investing', True, 10),
    ('ssy', 'SSY Calculator', 'Investing', True, 11),
    ('elss', 'ELSS Calculator', 'Investing', True, 12),
    ('gold-investment', 'Gold Investment Calculator', 'Investing', True, 13),
    ('swp', 'SWP Calculator', 'Investing', True, 14),
    ('roi-calculator', 'ROI Calculator', 'Investing', True, 15),
    ('goal-planner', 'Goal Planner', 'Investing', True, 16),
    ('risk-level-assessment', 'Risk Level Assessment', 'Investing', False, 17),
    ('volatility-measurement', 'Volatility Measurement', 'Investing', False, 18),
    ('beta-calculator', 'Beta Calculator', 'Investing', False, 19),
    
    # ===== RETIREMENT (Implemented) =====
    ('retirement', 'Retirement Calculator', 'Retirement', True, 1),
    ('epf', 'EPF Calculator', 'Retirement', True, 2),
    ('nps', 'NPS Calculator', 'Retirement', True, 3),
    
    # ===== PORTFOLIO ANALYSIS (Coming Soon) =====
    ('correlation-matrix', 'Correlation Matrix', 'Portfolio Analysis', False, 1),
    ('fee-analyzer', 'Investment Fee Analyzer', 'Portfolio Analysis', False, 2),
    ('etf-overlap', 'ETF Overlap Checker', 'Portfolio Analysis', False, 3),
    ('esg-scoring', 'ESG Scoring Dashboard', 'Portfolio Analysis', False, 4),
    
    # ===== FINANCE & LOANS (Implemented) =====
    ('emi', 'Loan EMI Calculator', 'Finance & Loans', True, 1),
    ('mortgage', 'Mortgage Calculator', 'Real Estate', True, 2),
    ('car-loan', 'Car Loan Calculator', 'Finance & Loans', True, 3),
    ('education-loan', 'Education Loan Calculator', 'Education', True, 4),
    ('loan-compare', 'Loan Comparison', 'Finance & Loans', True, 5),
    ('budget-planner', 'Budget Planner', 'Personal Finance', True, 6),
    ('income-tax', 'Income Tax Calculator', 'Taxation', True, 7),
    ('gst', 'GST Calculator', 'Taxation', True, 8),
    ('hra', 'HRA Calculator', 'Taxation', True, 9),
    ('inflation', 'Inflation Calculator', 'Personal Finance', True, 10),
    ('salary-converter', 'Salary Converter', 'Personal Finance', True, 11),
    ('debt-payoff', 'Debt Payoff Calculator', 'Debt', True, 12),
    ('credit-card-payoff', 'Credit Card Payoff', 'Debt', True, 13),
    ('emergency-fund', 'Emergency Fund Calculator', 'Personal Finance', True, 14),
    ('net-worth', 'Net Worth Calculator', 'Personal Finance', True, 15),
    ('rent-vs-buy', 'Rent vs Buy Calculator', 'Real Estate', True, 16),
    ('stamp-duty', 'Stamp Duty Calculator', 'Real Estate', True, 17),
    ('education-cost', 'Education Cost Planner', 'Education', True, 18),
    ('equity-dilution', 'Equity Dilution Calculator', 'Business', True, 19),
    ('break-even', 'Break-Even Calculator', 'Business', True, 20),
    ('margin', 'Profit Margin Calculator', 'Business', True, 21),
    
    # ===== INSURANCE (Mixed) =====
    ('life-insurance', 'Life Insurance Needs', 'Insurance', True, 1),
    ('car-insurance', 'Car Insurance Calculator', 'Insurance', True, 2),
    ('health-premium', 'Health Premium Estimator', 'Insurance', True, 3),
    ('term-insurance', 'Term Insurance Planner', 'Insurance', False, 4),
    ('term-life', 'Term Life Calculator', 'Insurance', False, 5),
    ('human-life-value', 'Human Life Value', 'Insurance', False, 6),
    ('nri-term', 'NRI Term Calculator', 'Insurance', False, 7),
    ('parents-health', 'Parents Health Cover', 'Insurance', False, 8),
    ('bike-insurance', 'Bike Insurance Calculator', 'Insurance', False, 9),
    ('travel-insurance', 'Travel Insurance Calculator', 'Insurance', False, 10),
    
    # ===== HEALTH & FITNESS (Mixed) =====
    ('bmi-calculator', 'BMI Calculator', 'Health & Fitness', True, 1),
    ('calorie-calculator', 'Calorie Calculator', 'Health & Fitness', True, 2),
    ('ideal-weight', 'Ideal Weight Calculator', 'Health & Fitness', True, 3),
    ('water-intake', 'Water Intake Calculator', 'Health & Fitness', True, 4),
    ('sleep', 'Sleep Calculator', 'Health & Fitness', True, 5),
    ('pregnancy-due-date', 'Pregnancy Due Date', 'Health & Fitness', True, 6),
    ('macro-nutrient-calculator', 'Macro Nutrient Calculator', 'Health & Fitness', False, 7),
    ('one-rep-max', 'One Rep Max Calculator', 'Health & Fitness', False, 8),
    ('target-heart-rate', 'Target Heart Rate Calculator', 'Health & Fitness', False, 9),
    ('body-fat-percentage', 'Body Fat Percentage Calculator', 'Health & Fitness', False, 10),
    ('running-pace', 'Running Pace Calculator', 'Health & Fitness', False, 11),
    ('meal-planner', 'Meal Planner Generator', 'Health & Fitness', False, 12),
    
    # ===== UTILITIES (Mixed) =====
    ('currency-converter', 'Currency Converter', 'Utilities', True, 1),
    ('password-generator', 'Password Generator', 'Security', True, 2),
    ('age-calculator', 'Age Calculator', 'Utilities', True, 3),
    ('percentage', 'Percentage Calculator', 'Utilities', True, 4),
    ('tip', 'Tip Calculator', 'Utilities', True, 5),
    ('fuel-cost', 'Fuel Cost Calculator', 'Utilities', True, 6),
    ('date-difference', 'Date Difference Calculator', 'Utilities', True, 7),
    ('unit-converter', 'Unit Converter', 'Utilities', True, 8),
    ('time-zone-converter', 'Time Zone Converter', 'Utilities', False, 9),
    ('countdown-timer', 'Countdown Timer', 'Utilities', False, 10),
    ('decision-maker', 'Decision Maker', 'Utilities', False, 11),
    ('url-shortener', 'URL Shortener', 'Utilities', False, 12),
    ('ip-address-lookup', 'IP Address Lookup', 'Utilities', False, 13),
    ('pdf-to-word', 'PDF to Word Converter', 'Utilities', False, 14),
    ('file-format-converter', 'File Format Converter', 'Utilities', False, 15),
    ('language-translator', 'Language Translator', 'Utilities', False, 16),
    
    # ===== REAL ESTATE (Coming Soon) =====
    ('mortgage-affordability', 'Mortgage Affordability', 'Real Estate', False, 18),
    ('home-loan-comparison', 'Home Loan Comparison', 'Real Estate', False, 19),
    ('moving-cost', 'Moving Cost Calculator', 'Real Estate', False, 20),
    ('square-footage', 'Square Footage Calculator', 'Real Estate', False, 21),
    ('paint-calculator', 'Paint Calculator', 'Real Estate', False, 22),
    ('mortgage-refinance', 'Mortgage Refinance Calculator', 'Real Estate', False, 23),
    ('home-value-estimator', 'Home Value Estimator', 'Real Estate', False, 24),
    
    # ===== PRODUCTIVITY (Coming Soon) =====
    ('pomodoro-timer', 'Pomodoro Timer', 'Productivity', False, 1),
    ('habit-tracker', 'Habit Tracker', 'Productivity', False, 2),
    ('task-priority-matrix', 'Task Priority Matrix', 'Productivity', False, 3),
    ('goal-setting-template', 'Goal Setting Template', 'Productivity', False, 4),
    ('mind-map-generator', 'Mind Map Generator', 'Productivity', False, 5),
    
    # ===== TRAVEL (Coming Soon) =====
    ('trip-cost', 'Trip Cost Calculator', 'Travel', False, 1),
    ('travel-itinerary', 'Travel Itinerary Builder', 'Travel', False, 2),
    ('packing-list', 'Packing List Generator', 'Travel', False, 3),
    ('flight-price-tracker', 'Flight Price Tracker', 'Travel', False, 4),
    ('mileage-calculator', 'Mileage Calculator', 'Travel', False, 5),
    ('travel-destination-quiz', 'Where Should I Travel Quiz', 'Travel', False, 6),
    ('airport-code-lookup', 'Airport Code Lookup', 'Travel', False, 7),
    ('visa-requirement-checker', 'Visa Requirement Checker', 'Travel', False, 8),
    
    # ===== COOKING & RECIPES (Coming Soon) =====
    ('recipe-nutrition', 'Recipe Nutrition Calculator', 'Cooking & Recipes', False, 1),
    ('meal-calorie', 'Meal Calorie Calculator', 'Cooking & Recipes', False, 2),
    ('recipe-scaler', 'Recipe Scaler', 'Cooking & Recipes', False, 3),
    ('substitution-finder', 'Substitution Finder', 'Cooking & Recipes', False, 4),
    ('baking-pan-converter', 'Baking Pan Size Converter', 'Cooking & Recipes', False, 5),
    ('what-can-i-make', 'What Can I Make Tool', 'Cooking & Recipes', False, 6),
    ('wine-pairing', 'Wine Pairing Helper', 'Cooking & Recipes', False, 7),
    ('cooking-timer', 'Cooking Timer', 'Cooking & Recipes', False, 8),
    ('grocery-list', 'Grocery List Generator', 'Cooking & Recipes', False, 9),
    
    # ===== MARKETING (Coming Soon) =====
    ('email-subject-tester', 'Email Subject Line Tester', 'Marketing', False, 1),
    ('social-bio-generator', 'Social Media Bio Generator', 'Marketing', False, 2),
    ('cpc-calculator', 'CPC Calculator', 'Marketing', False, 3),
    ('hashtag-generator', 'Hashtag Generator', 'Marketing', False, 4),
    ('instagram-caption', 'Instagram Caption Generator', 'Marketing', False, 5),
    ('linkedin-headline', 'LinkedIn Headline Generator', 'Marketing', False, 6),
    ('tiktok-idea-generator', 'TikTok Video Idea Generator', 'Marketing', False, 7),
    
    # ===== SEO (Coming Soon) =====
    ('keyword-difficulty', 'Keyword Difficulty Checker', 'SEO', False, 1),
    ('meta-tag-generator', 'Meta Tag Generator', 'SEO', False, 2),
    ('backlink-analyzer', 'Backlink Analyzer', 'SEO', False, 3),
    ('serp-preview', 'SERP Preview Tool', 'SEO', False, 4),
    ('website-rank-checker', 'Website Rank Checker', 'SEO', False, 5),
    ('readability-analyzer', 'Content Readability Analyzer', 'SEO', False, 6),
    ('sitemap-generator', 'Sitemap Generator', 'SEO', False, 7),
    ('robots-txt-tester', 'Robots.txt Tester', 'SEO', False, 8),
    ('website-speed-test', 'Website Speed Test', 'SEO', False, 9),
    
    # ===== E-COMMERCE (Coming Soon) =====
    ('profit-margin', 'Profit Margin Calculator', 'E-commerce', False, 1),
    ('shipping-cost', 'Shipping Cost Calculator', 'E-commerce', False, 2),
    ('product-description', 'Product Description Generator', 'E-commerce', False, 3),
    ('sales-tax', 'Sales Tax Calculator', 'E-commerce', False, 4),
    ('amazon-fba-fee', 'Amazon FBA Fee Calculator', 'E-commerce', False, 5),
    ('dropshipping-profit', 'Dropshipping Profit Calculator', 'E-commerce', False, 6),
    
    # ===== LEGAL (Coming Soon) =====
    ('legal-document-generator', 'Legal Document Generator', 'Legal', False, 1),
    ('bill-of-sale', 'Bill of Sale Generator', 'Legal', False, 2),
    ('lease-agreement', 'Lease Agreement Generator', 'Legal', False, 3),
    ('legal-word-counter', 'Legal Word Counter', 'Legal', False, 4),
    ('statute-of-limitations', 'Statute of Limitations Checker', 'Legal', False, 5),
    ('power-of-attorney', 'Power of Attorney Generator', 'Legal', False, 6),
    
    # ===== GAMING (Coming Soon) =====
    ('character-name-generator', 'Character Name Generator', 'Gaming', False, 1),
    ('loot-drop-chance', 'Loot Drop Chance Calculator', 'Gaming', False, 2),
    ('game-fps-calculator', 'Game Frame Rate Calculator', 'Gaming', False, 3),
    ('team-composition', 'Team Composition Builder', 'Gaming', False, 4),
    ('xp-calculator', 'Experience Calculator', 'Gaming', False, 5),
    ('random-dungeon', 'Random Dungeon Generator', 'Gaming', False, 6),
    ('speedrun-timer', 'Speedrunning Timer', 'Gaming', False, 7),
    
    # ===== DATA & CODE (Coming Soon) =====
    ('json-formatter', 'JSON Formatter', 'Data & Code', False, 1),
    ('code-beautifier', 'Code Beautifier/Minifier', 'Data & Code', False, 2),
    ('sql-query-generator', 'SQL Query Generator', 'Data & Code', False, 3),
    ('api-request-builder', 'API Request Builder', 'Data & Code', False, 4),
    ('csv-to-json', 'CSV to JSON Converter', 'Data & Code', False, 5),
    ('user-agent-parser', 'User Agent Parser', 'Data & Code', False, 6),
    
    # ===== DESIGN (Coming Soon) =====
    ('color-palette', 'Color Palette Generator', 'Design', False, 1),
    ('font-pairing', 'Font Pairing Tool', 'Design', False, 2),
    ('logo-maker', 'Logo Maker', 'Design', False, 3),
    ('image-background-remover', 'Image Background Remover', 'Design', False, 4),
    ('qr-code-generator', 'QR Code Generator', 'Design', False, 5),
    ('gradient-generator', 'Gradient Generator', 'Design', False, 6),
    ('color-picker', 'Color Picker', 'Design', False, 7),
    ('image-compressor', 'Image Compressor', 'Design', False, 8),
    ('social-image-resizer', 'Social Media Image Resizer', 'Design', False, 9),
    
    # ===== WRITING (Coming Soon) =====
    ('word-counter', 'Word Counter', 'Writing', False, 1),
    ('reading-time', 'Reading Time Calculator', 'Writing', False, 2),
    ('text-summarizer', 'Text Summarizer', 'Writing', False, 3),
    ('case-converter', 'Case Converter', 'Writing', False, 4),
    ('lorem-ipsum', 'Lorem Ipsum Generator', 'Writing', False, 5),
    ('grammar-checker', 'Grammar & Spell Checker', 'Writing', False, 6),
    
    # ===== CONTENT (Coming Soon) =====
    ('youtube-title-generator', 'YouTube Title Generator', 'Content', False, 1),
    ('twitter-thread', 'Twitter Thread Generator', 'Content', False, 2),
    
    # ===== EDUCATION & STUDY (Coming Soon) =====
    ('gpa-calculator', 'GPA Calculator', 'Education & Study', False, 1),
    ('citation-generator', 'Citation Generator', 'Education & Study', False, 2),
    ('plagiarism-checker', 'Plagiarism Checker', 'Education & Study', False, 3),
    ('flashcards', 'Flashcards Generator', 'Education & Study', False, 4),
    ('reading-speed-test', 'Reading Speed Test', 'Education & Study', False, 5),
    
    # ===== HEALTH & MEDICAL (Coming Soon) =====
    ('symptom-checker', 'Symptom Checker', 'Health & Medical', False, 1),
    ('drug-interaction-checker', 'Drug Interaction Checker', 'Health & Medical', False, 2),
    ('pill-identifier', 'Pill Identifier', 'Health & Medical', False, 3),
    ('dosage-calculator', 'Dosage Calculator', 'Health & Medical', False, 4),
    ('heart-age-calculator', 'Heart Age Calculator', 'Health & Medical', False, 5),
    ('vaccination-schedule', 'Vaccination Schedule Tracker', 'Health & Medical', False, 6),
    ('medical-dictionary', 'Medical Dictionary Lookup', 'Health & Medical', False, 7),
    ('blood-alcohol-calculator', 'Blood Alcohol Calculator', 'Health & Medical', False, 8),
    
    # ===== FUN & ENTERTAINMENT (Coming Soon) =====
    ('meme-generator', 'Meme Generator', 'Fun & Entertainment', False, 1),
    ('ascii-art', 'ASCII Art Generator', 'Fun & Entertainment', False, 2),
    ('love-calculator', 'Love Calculator', 'Fun & Entertainment', False, 3),
    ('personality-quiz', 'Personality Quiz Generator', 'Fun & Entertainment', False, 4),
    ('truth-or-dare', 'Truth or Dare Generator', 'Fun & Entertainment', False, 5),
    ('pet-name-generator', 'Pet Name Generator', 'Fun & Entertainment', False, 6),
    ('boredom-buster', 'Boredom Buster', 'Fun & Entertainment', False, 7),
    
    # ===== ENTERTAINMENT (Coming Soon) =====
    ('what-to-watch', 'What Should I Watch Picker', 'Entertainment', False, 1),
    ('book-picker', 'What Book Should I Read Picker', 'Entertainment', False, 2),
    
    # ===== BUSINESS (Coming Soon) =====
    ('meeting-cost-calculator', 'Meeting Cost Calculator', 'Business Operations', False, 1),
    ('project-timeline-generator', 'Project Timeline Generator', 'Project Management', False, 2),
    ('invoice-generator', 'Invoice Generator', 'Business Operations', False, 3),
    ('swot-analysis', 'SWOT Analysis Generator', 'Business Strategy', False, 4),
    ('business-name-generator', 'Business Name Generator', 'Startup', False, 5),
    ('markup-margin', 'Markup & Margin Calculator', 'Business Operations', False, 6),
    
    # ===== SECURITY (Coming Soon) =====
    ('ssl-checker', 'SSL Checker', 'Security', False, 3),
    ('password-strength', 'Password Strength Checker', 'Security', False, 4),
    
    # ===== INCOME & EMPLOYMENT (Coming Soon) =====
    ('work-hours', 'Work Hours Calculator', 'Income & Employment', False, 1),
    ('salary-comparison', 'Salary Comparison Tool', 'Income & Employment', False, 2),
    
    # ===== FAMILY & GOALS (Coming Soon) =====
    ('baby-name-generator', 'Baby Name Generator', 'Family & Goals', False, 1),
    
    # ===== MATH & SCIENCE (Coming Soon) =====
    ('equation-solver', 'Equation Solver', 'Math & Science', False, 1),
    
    # ===== WEATHER & ASTRONOMY (Coming Soon) =====
    ('weather-comparison', 'Weather Comparison Tool', 'Weather & Astronomy', False, 1),
    ('sunrise-sunset', 'Sunrise/Sunset Calculator', 'Weather & Astronomy', False, 2),
    ('moon-phase', 'Moon Phase Calendar', 'Weather & Astronomy', False, 3),
    
    # ===== SUSTAINABILITY (Coming Soon) =====
    ('carbon-footprint', 'Carbon Footprint Calculator', 'Sustainability', False, 1),
    
    # ===== WELLNESS (Coming Soon) =====
    ('gratitude-journal', 'Gratitude Journal Prompts', 'Wellness', False, 1),
    
    # ===== TAXATION (Coming Soon) =====
    ('tax-refund-estimator', 'Tax Refund Estimator', 'Taxation', False, 10),
    
    # ===== DEBT (Coming Soon) =====
    ('debt-snowball-avalanche', 'Debt Snowball vs Avalanche', 'Debt', False, 14),
]


def run_migration():
    """Run the tool migration"""
    app = create_app()
    
    with app.app_context():
        added = 0
        updated = 0
        
        for tool_data in TOOLS:
            slug, name, category, is_implemented, order_index = tool_data
            
            # Check if tool exists
            existing = ToolSettings.query.get(slug)
            
            if existing:
                # Update existing tool
                existing.tool_name = name
                existing.category = category
                existing.is_implemented = is_implemented
                existing.order_index = order_index
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                # Create new tool
                tool = ToolSettings(
                    tool_slug=slug,
                    tool_name=name,
                    category=category,
                    enabled=True,
                    order_index=order_index,
                    is_implemented=is_implemented,
                    country_code='GLOBAL'
                )
                db.session.add(tool)
                added += 1
        
        db.session.commit()
        print(f"Migration complete! Added: {added}, Updated: {updated}")
        print(f"Total tools in database: {ToolSettings.query.count()}")


if __name__ == '__main__':
    run_migration()
