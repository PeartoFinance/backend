# Subscription System Architecture Proposal

## Executive Summary
**Key Goal:** Allow the Admin to manage Plans, Pricing, and Festival Discounts dynamically without developer involvement, while maintaining a flexible payment layer that allows switching from PayPal to any other gateway (Stripe, Razorpay) in the future seamlessly.

---

## 1. High-Level Architecture: "The Adapter Pattern" 🔌

To prevent Vendor Lock-in (getting stuck with PayPal), we will implement a **Payment Gateway Interface**.

### How it works:
The core backend Logic never talks to PayPal directly. It talks to a generic internal interface.

Payment confirmation and renewals will be handled via gateway webhooks, which update internal subscription state independently of the adapter

1.  **Core System Command:** `PaymentManager.create_subscription(user, plan)`
2.  **The Switch (Config):** The system checks `ENV['PAYMENT_PROVIDER']` (currently 'PAYPAL').
3.  **The Adapter:** It loads `adapters/paypal_adapter.py`.
    *   *This adapter translates our command into PayPal's specific API JSON.*
4.  **Future Switch:** If we switch to Stripe later:
    *   We change the Config to 'STRIPE'.
    *   We add `adapters/stripe_adapter.py`.
    *   **Result:** The Core Logic (Routes, Models, Admin Panel) does **NOT** change.

---

## 2. Admin Control Panel Features 

The Admin Dashboard will have full control over the business logic.

### A. Dynamic Plan Management
Admins can create/edit plans on the fly.
*   **Plan Name:** "Pro", "Elite", "Diwali Special(etc)".
*   **Billing:** Monthly, Yearly, Lifetime.
*   **Feature Locking:** Admin can check/uncheck features per plan (e.g., "Access to Advanced Charts").
    *   *Technical Implementation:* Features are stored as a JSON object, allowing instant updates without coding.

### B. Marketing & Discounts (Coupons)
Admins can run marketing campaigns independently.
*   **Promo Codes:** Create codes like "SUMMER2026".
*   **Logic:**
    *   Percentage Off (20%) OR Fixed Amount ($10 off).
    *   **Expiry Dates:** Auto-disable coupons after the festival ends.
    *   **Usage Limits:** "First 500 users only".

### C. Revenue Dashboard
A centralized view of all money flowing in, regardless of which Gateway (PayPal/Stripe) processed it.

---

## 3. Database Schema Strategy 

We need 4 new Tables to support this robustly.

| Table Name | Purpose | Key Fields |
| :--- | :--- | :--- |
| **`SubscriptionPlans`** | Defines what is for sale. | `name`, `price`, `interval`, `features (JSON)` |
| **`SubscriptionCoupons`** | Handles discounts. | `code`, `discount_value`, `valid_until` |
| **`UserSubscriptions`** | Tracks who has access. | `user_id`, `status`, `next_billing_date` |
| **`PaymentTransactions`** | Audit log for accounting. | `amount`, `status`, `gateway_ref_id` |

---

## 4. Future-Proofing Features 

We are architecting the database *now* to support these features *later* without a rewrite:

1.  **Team/Family Plans:** The database will support a `max_members` field, allowing a manager to buy one generic subscription and invite 5 team members.
2.  **Grandfathering:** Existing users keep their old price when you raise prices for new users.
3.  **Geo-Pricing:** Show UPI to Indian users and PayPal to US users automatically.

---

## 5. Development Phases

1.  **Phase 1 (Foundation):** Create Database Models & Admin API for Plans/Coupons.
2.  **Phase 2 (The Logic):** Implement the "Feature Gating" decorator (`@requires_feature`) to lock routes.
3.  **Phase 3 (The Gateway):** Build the `PaymentManager` and the `PayPalAdapter` (Initial Provider).
4.  **Phase 4 (Frontend):** Build the Admin UI tabs and User Pricing Page.

---

