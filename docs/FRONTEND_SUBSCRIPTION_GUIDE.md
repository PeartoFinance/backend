# 🚀 Frontend Integration Guide: Subscription System

This guide explains how to implement the Pearto Finance subscription and payment flow in the frontend.

## 📌 Overview
The system uses **PayPal** as the primary gateway. The flow follows a "Create Order -> User Approval -> Backend Capture" pattern.

**Base URL:** `/api/subscription`  
**Auth:** All user endpoints (except listing plans) require `Authorization: Bearer <JWT_TOKEN>`

---

## 1. The Subscription Flow

### Step A: Display Pricing Plans
*   **Endpoint:** `GET /plans`
*   **Action:** Loop through these to create your pricing cards.

### Step B: The Checkout Process
When the user clicks "Subscribe":
1.  **POST `/checkout`**: Send `{ "plan_id": ID }`.
2.  **Redirect**: Open the `approval_url` from the response (PayPal site).
3.  **Return**: User is sent back to your `success` page.

### Step C: Finalizing (Capture)
*   **Endpoint:** `POST /capture`
*   **Payload:** `{ "order_id": "ID_FROM_URL", "plan_id": ID }`
*   **Crucial:** Do not show success until this API returns 200 OK.

---

## 2. 🔐 Feature Locking (The 403 Handler)
The backend returns a **403 Forbidden** if a user hits a locked route.
```json
{
    "error": "Subscription required",
    "feature_required": "portfolio_score",
    "action": "upgrade"
}
```
**Tip:** Use the `feature_required` string to show a specific "Locked" UI for that feature.

---

## 3. 🛠️ Admin Dashboard (New!)
If you are building the Admin Panel for plans, use this endpoint to fetch the list of available feature keys. **Do not hardcode these names.**

*   **Endpoint:** `GET /admin/available-features`
*   **Response:**
    ```json
    {
      "features": ["portfolio_score", "advanced_analytics", "ai_insights", "basic", "premium", "elite"],
      "description": "..."
    }
    ```
**Action:** Use this list to generate a **Checklist** when creating or editing a Plan.

---

## 4. Current Feature Registry
These are the keys currently defined in the backend logic:
- `portfolio_score`: Access to health scores.
- `advanced_analytics`: Deeper data insights.
- `wealth_history`: Historical tracking.
- `ai_insights`: AI signals.
- `real_time_data`: Live updates.
- `basic`, `premium`, `elite`: Tier-based access.

---
**Testing Note:** Set `PAYPAL_BYPASS_APPROVAL=true` in `.env` to skip PayPal login during dev testing.
