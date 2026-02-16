"""
Seed the 8 footer CMS pages: about, contact, careers, press, privacy, terms, disclaimer, cookies
Run: python seed_footer_pages.py
"""
import uuid
from app import create_app
from models import db, Page


FOOTER_PAGES = [
    # ──── Company ────
    {
        "slug": "about",
        "title": "About Us",
        "meta_title": "About Pearto Finance | Real-Time Market Data & Investment Tools",
        "meta_description": "Pearto Finance is your premier destination for real-time market data, investment tools, and financial insights. Learn more about our mission and team.",
        "placement": "footer",
        "sort_order": 1,
        "content": """
<section class="space-y-8">
  <div>
    <h2 class="text-2xl font-bold mb-4">Our Mission</h2>
    <p>Pearto Finance is dedicated to democratising financial information and providing everyone access to institutional-grade market data, analysis tools, and educational resources. We believe that informed investors make better decisions, and our platform is built to deliver real-time insights across stocks, crypto, forex, and commodities.</p>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">What We Offer</h2>
    <ul class="list-disc pl-6 space-y-2">
      <li><strong>Real-Time Market Data</strong> — Live quotes for stocks, crypto, forex, and commodities from global exchanges.</li>
      <li><strong>Advanced Charting</strong> — Interactive charts with technical indicators, drawing tools, and multi-timeframe analysis.</li>
      <li><strong>Financial Calculators</strong> — 100+ calculators for SIP, EMI, compound interest, tax, and portfolio planning.</li>
      <li><strong>AI-Powered Insights</strong> — Get instant AI analysis on any asset with our integrated assistant.</li>
      <li><strong>Learning Hub</strong> — Structured courses and glossary to help beginners and experienced traders alike.</li>
      <li><strong>Community</strong> — Share trading ideas, follow top investors, and join groups.</li>
    </ul>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">Our Team</h2>
    <p>We are a team of financial analysts, software engineers, and market enthusiasts passionate about making finance accessible. Headquartered in New York, we serve users worldwide with localised data and multi-currency support.</p>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">Contact</h2>
    <p>Have questions or feedback? Reach us at <a href="mailto:support@pearto.com" class="text-emerald-600 hover:underline">support@pearto.com</a>.</p>
  </div>
</section>
""",
    },
    {
        "slug": "contact",
        "title": "Contact Us",
        "meta_title": "Contact Pearto Finance | Get in Touch",
        "meta_description": "Have questions about Pearto Finance? Contact our support team via email, phone, or our online form.",
        "placement": "footer",
        "sort_order": 2,
        "content": """
<section class="space-y-8">
  <div>
    <h2 class="text-2xl font-bold mb-4">Get in Touch</h2>
    <p>We'd love to hear from you. Whether you have a question about our platform, need technical support, or want to explore partnership opportunities, our team is here to help.</p>
  </div>
  <div class="grid md:grid-cols-2 gap-6">
    <div class="p-6 bg-slate-50 dark:bg-slate-800 rounded-xl">
      <h3 class="font-semibold text-lg mb-2">📧 Email Support</h3>
      <p class="text-slate-600 dark:text-slate-400 mb-2">For general inquiries and support</p>
      <a href="mailto:support@pearto.com" class="text-emerald-600 hover:underline font-medium">support@pearto.com</a>
    </div>
    <div class="p-6 bg-slate-50 dark:bg-slate-800 rounded-xl">
      <h3 class="font-semibold text-lg mb-2">📞 Phone</h3>
      <p class="text-slate-600 dark:text-slate-400 mb-2">Mon–Fri, 9 AM – 6 PM EST</p>
      <a href="tel:+1234567890" class="text-emerald-600 hover:underline font-medium">+1 (234) 567-890</a>
    </div>
    <div class="p-6 bg-slate-50 dark:bg-slate-800 rounded-xl">
      <h3 class="font-semibold text-lg mb-2">📍 Office</h3>
      <p class="text-slate-600 dark:text-slate-400">New York, NY<br/>United States</p>
    </div>
    <div class="p-6 bg-slate-50 dark:bg-slate-800 rounded-xl">
      <h3 class="font-semibold text-lg mb-2">💼 Business Inquiries</h3>
      <p class="text-slate-600 dark:text-slate-400 mb-2">For partnerships and advertising</p>
      <a href="mailto:business@pearto.com" class="text-emerald-600 hover:underline font-medium">business@pearto.com</a>
    </div>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">Response Time</h2>
    <p>We aim to respond to all inquiries within 24 business hours. For urgent issues, please include "URGENT" in your email subject line.</p>
  </div>
</section>
""",
    },
    {
        "slug": "careers",
        "title": "Careers",
        "meta_title": "Careers at Pearto Finance | Join Our Team",
        "meta_description": "Join Pearto Finance and help build the future of financial technology. Explore open positions in engineering, design, finance, and more.",
        "placement": "footer",
        "sort_order": 3,
        "content": """
<section class="space-y-8">
  <div>
    <h2 class="text-2xl font-bold mb-4">Join Our Team</h2>
    <p>We're building the future of financial technology and we're looking for talented, passionate people to join us. At Pearto Finance, you'll work on products that help millions of users make smarter investment decisions.</p>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">Why Pearto?</h2>
    <ul class="list-disc pl-6 space-y-2">
      <li>Work on cutting-edge fintech products used by investors worldwide</li>
      <li>Collaborative, remote-friendly culture</li>
      <li>Competitive compensation and equity</li>
      <li>Continuous learning and development opportunities</li>
      <li>Make a real impact on financial literacy and empowerment</li>
    </ul>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">Open Positions</h2>
    <p class="text-slate-600 dark:text-slate-400">We're always looking for exceptional talent. Even if you don't see a role that fits, feel free to reach out.</p>
    <p class="mt-4">Send your CV and a brief cover letter to <a href="mailto:careers@pearto.com" class="text-emerald-600 hover:underline font-medium">careers@pearto.com</a></p>
  </div>
</section>
""",
    },
    {
        "slug": "press",
        "title": "Press",
        "meta_title": "Press & Media | Pearto Finance",
        "meta_description": "Pearto Finance press resources, media kit, and latest news. For press inquiries, contact our media team.",
        "placement": "footer",
        "sort_order": 4,
        "content": """
<section class="space-y-8">
  <div>
    <h2 class="text-2xl font-bold mb-4">Press & Media</h2>
    <p>For press inquiries, interviews, or media resources, please contact our communications team.</p>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">Media Contact</h2>
    <p>Email: <a href="mailto:press@pearto.com" class="text-emerald-600 hover:underline">press@pearto.com</a></p>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">About Pearto Finance</h2>
    <p>Pearto Finance is a comprehensive financial platform providing real-time market data, advanced charting tools, AI-powered analysis, and educational resources to investors worldwide. Founded with the mission of democratising financial information, Pearto serves users across stocks, cryptocurrency, forex, and commodities markets.</p>
  </div>
  <div>
    <h2 class="text-2xl font-bold mb-4">Brand Assets</h2>
    <p>To download our logo, brand guidelines, and screenshots, please email <a href="mailto:press@pearto.com" class="text-emerald-600 hover:underline">press@pearto.com</a> and we'll send the media kit.</p>
  </div>
</section>
""",
    },

    # ──── Legal ────
    {
        "slug": "privacy",
        "title": "Privacy Policy",
        "meta_title": "Privacy Policy | Pearto Finance",
        "meta_description": "Read the Pearto Finance privacy policy to understand how we collect, use, and protect your personal data.",
        "placement": "footer",
        "sort_order": 10,
        "content": """
<section class="space-y-6">
  <p><strong>Last updated:</strong> February 16, 2026</p>

  <div>
    <h2 class="text-2xl font-bold mb-3">1. Introduction</h2>
    <p>Pearto Finance ("we", "us", "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and services at pearto.com.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">2. Information We Collect</h2>
    <h3 class="text-lg font-semibold mt-4 mb-2">Personal Information</h3>
    <p>When you register, we may collect: name, email address, phone number, and profile information you choose to provide.</p>
    <h3 class="text-lg font-semibold mt-4 mb-2">Usage Data</h3>
    <p>We automatically collect information about how you interact with our platform, including pages visited, features used, IP address, browser type, and device information.</p>
    <h3 class="text-lg font-semibold mt-4 mb-2">Financial Data</h3>
    <p>Watchlist items, portfolio holdings, and preferences you save are stored to provide personalised services. We do not collect or store bank account or brokerage credentials.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">3. How We Use Your Information</h2>
    <ul class="list-disc pl-6 space-y-1">
      <li>Provide, maintain, and improve our services</li>
      <li>Personalise your experience with relevant market data and tools</li>
      <li>Send important notifications (price alerts, watchlist updates)</li>
      <li>Communicate about new features, updates, and promotions</li>
      <li>Ensure security and prevent fraud</li>
      <li>Comply with legal obligations</li>
    </ul>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">4. Data Sharing</h2>
    <p>We do not sell your personal data. We may share information with trusted service providers who assist in operating our platform (hosting, analytics, email delivery) under strict confidentiality agreements.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">5. Data Security</h2>
    <p>We implement industry-standard security measures including encryption in transit (TLS), secure password hashing, and regular security audits to protect your data.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">6. Your Rights</h2>
    <p>You have the right to access, correct, or delete your personal data at any time through your account settings or by contacting us at <a href="mailto:privacy@pearto.com" class="text-emerald-600 hover:underline">privacy@pearto.com</a>.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">7. Cookies</h2>
    <p>We use cookies and similar technologies to enhance your experience. See our <a href="/p/cookies" class="text-emerald-600 hover:underline">Cookie Policy</a> for details.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">8. Contact</h2>
    <p>For privacy-related questions, contact us at <a href="mailto:privacy@pearto.com" class="text-emerald-600 hover:underline">privacy@pearto.com</a>.</p>
  </div>
</section>
""",
    },
    {
        "slug": "terms",
        "title": "Terms of Service",
        "meta_title": "Terms of Service | Pearto Finance",
        "meta_description": "Read the terms and conditions governing your use of Pearto Finance platform and services.",
        "placement": "footer",
        "sort_order": 11,
        "content": """
<section class="space-y-6">
  <p><strong>Last updated:</strong> February 16, 2026</p>

  <div>
    <h2 class="text-2xl font-bold mb-3">1. Acceptance of Terms</h2>
    <p>By accessing or using Pearto Finance (pearto.com), you agree to be bound by these Terms of Service. If you do not agree, please do not use our services.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">2. Description of Services</h2>
    <p>Pearto Finance provides real-time market data, financial calculators, educational content, community features, and AI-powered analysis tools. Our services are provided "as is" for informational and educational purposes.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">3. User Accounts</h2>
    <ul class="list-disc pl-6 space-y-1">
      <li>You must be at least 18 years old to create an account</li>
      <li>You are responsible for maintaining the security of your account credentials</li>
      <li>You agree to provide accurate and up-to-date information</li>
      <li>One person or entity per account unless authorised</li>
    </ul>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">4. Acceptable Use</h2>
    <p>You agree not to: use the platform for illegal activities, scrape or reverse-engineer our data, impersonate others, upload malicious content, or interfere with the platform's operation.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">5. Financial Disclaimer</h2>
    <p>Pearto Finance does not provide investment advice. All market data, analysis, and tools are for informational purposes only. Consult a qualified financial adviser before making investment decisions. See our <a href="/p/disclaimer" class="text-emerald-600 hover:underline">full disclaimer</a>.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">6. Intellectual Property</h2>
    <p>All content, logos, and software on Pearto Finance are owned by us or our licensors and protected by copyright laws. User-generated content remains the property of its creator, but you grant us a licence to display it on the platform.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">7. Limitation of Liability</h2>
    <p>Pearto Finance is not liable for any losses arising from use of our platform, including investment losses based on data or analysis provided. Market data may be delayed or inaccurate.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">8. Changes to Terms</h2>
    <p>We may update these terms from time to time. Continued use of the platform after changes constitutes acceptance of the new terms.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">9. Contact</h2>
    <p>Questions about these terms? Contact <a href="mailto:legal@pearto.com" class="text-emerald-600 hover:underline">legal@pearto.com</a>.</p>
  </div>
</section>
""",
    },
    {
        "slug": "disclaimer",
        "title": "Disclaimer",
        "meta_title": "Disclaimer | Pearto Finance",
        "meta_description": "Important financial disclaimer for Pearto Finance. Our platform provides information only, not investment advice.",
        "placement": "footer",
        "sort_order": 12,
        "content": """
<section class="space-y-6">
  <p><strong>Last updated:</strong> February 16, 2026</p>

  <div class="p-6 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
    <h2 class="text-xl font-bold text-amber-800 dark:text-amber-400 mb-3">⚠️ Important Notice</h2>
    <p class="text-amber-700 dark:text-amber-300">The information provided on Pearto Finance is for <strong>general informational and educational purposes only</strong> and should not be construed as financial, investment, or legal advice.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">No Investment Advice</h2>
    <p>Pearto Finance does not provide personalised investment recommendations. Any data, analysis, AI-generated insights, or opinions on this platform are provided for informational purposes only and do not constitute a solicitation, recommendation, or endorsement to buy, sell, or hold any securities, cryptocurrencies, or financial instruments.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">Market Data Accuracy</h2>
    <p>While we strive to provide accurate and up-to-date market data, we cannot guarantee the completeness, accuracy, or timeliness of any information. Market data may be delayed. Always verify information with official sources before making financial decisions.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">Risk Warning</h2>
    <p>Investing in stocks, cryptocurrencies, forex, and other financial instruments involves significant risk, including the potential loss of principal. Past performance does not guarantee future results. You should only invest money you can afford to lose.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">Third-Party Content</h2>
    <p>Our platform may include links to third-party websites, tools, or services. We are not responsible for the content, accuracy, or practices of any third-party sites.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">Professional Advice</h2>
    <p>Always consult with a qualified financial adviser, accountant, or legal professional before making any investment or financial decisions.</p>
  </div>
</section>
""",
    },
    {
        "slug": "cookies",
        "title": "Cookie Policy",
        "meta_title": "Cookie Policy | Pearto Finance",
        "meta_description": "Learn about how Pearto Finance uses cookies and similar technologies to enhance your browsing experience.",
        "placement": "footer",
        "sort_order": 13,
        "content": """
<section class="space-y-6">
  <p><strong>Last updated:</strong> February 16, 2026</p>

  <div>
    <h2 class="text-2xl font-bold mb-3">What Are Cookies</h2>
    <p>Cookies are small text files stored on your device when you visit a website. They help us remember your preferences, understand how you use our platform, and improve your experience.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">Cookies We Use</h2>
    <h3 class="text-lg font-semibold mt-4 mb-2">Essential Cookies</h3>
    <p>Required for the platform to function. These include authentication tokens, session cookies, and security cookies. You cannot opt out of these.</p>
    <h3 class="text-lg font-semibold mt-4 mb-2">Functional Cookies</h3>
    <p>Remember your preferences such as language, currency, dark mode, and layout settings to provide a personalised experience.</p>
    <h3 class="text-lg font-semibold mt-4 mb-2">Analytics Cookies</h3>
    <p>Help us understand how users interact with our platform so we can improve features and performance. We use privacy-respecting analytics tools.</p>
    <h3 class="text-lg font-semibold mt-4 mb-2">Marketing Cookies</h3>
    <p>Used to deliver relevant advertisements and measure campaign effectiveness. You can opt out of these in your browser settings.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">Managing Cookies</h2>
    <p>You can control cookies through your browser settings. Note that disabling essential cookies may prevent certain features from working. Most browsers allow you to:</p>
    <ul class="list-disc pl-6 space-y-1 mt-2">
      <li>View and delete cookies</li>
      <li>Block all or specific cookies</li>
      <li>Set preferences for specific websites</li>
    </ul>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">Local Storage</h2>
    <p>In addition to cookies, we use browser local storage to save your preferences (theme, currency, country) for a faster experience. This data stays on your device and is not transmitted to our servers.</p>
  </div>

  <div>
    <h2 class="text-2xl font-bold mb-3">Contact</h2>
    <p>For questions about our cookie practices, contact <a href="mailto:privacy@pearto.com" class="text-emerald-600 hover:underline">privacy@pearto.com</a>.</p>
  </div>
</section>
""",
    },
]


def seed_footer_pages():
    app = create_app()
    with app.app_context():
        created = 0
        updated = 0
        for page_data in FOOTER_PAGES:
            existing = Page.query.filter_by(slug=page_data["slug"]).first()
            if existing:
                # Update existing page
                existing.title = page_data["title"]
                existing.content = page_data["content"].strip()
                existing.meta_title = page_data["meta_title"]
                existing.meta_description = page_data["meta_description"]
                existing.placement = page_data["placement"]
                existing.sort_order = page_data["sort_order"]
                existing.status = "published"
                existing.country_code = "GLOBAL"
                updated += 1
                print(f"  [UPDATED] /{existing.slug} — {existing.title}")
            else:
                new_page = Page(
                    id=str(uuid.uuid4()),
                    slug=page_data["slug"],
                    title=page_data["title"],
                    content=page_data["content"].strip(),
                    meta_title=page_data["meta_title"],
                    meta_description=page_data["meta_description"],
                    placement=page_data["placement"],
                    sort_order=page_data["sort_order"],
                    status="published",
                    country_code="GLOBAL",
                    template="default",
                )
                db.session.add(new_page)
                created += 1
                print(f"  [CREATED] /{new_page.slug} — {new_page.title}")

        db.session.commit()
        print(f"\nDone! Created: {created}, Updated: {updated}, Total: {created + updated}")


if __name__ == "__main__":
    seed_footer_pages()
