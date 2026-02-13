# Frontend Integration Guide

This document details the recent critical backend fixes (Security, Portfolio, and Notifications) and the required actions for the frontend team.

---

## 1. Security & Authentication Fix
We have removed insecure authentication fallbacks to ensure user data integrity.

### Changes:
- **Removed Header Fallback:** The backend no longer supports the `X-User-Email` header for authentication.
- **Enforced JWT:** All user-specific routes (Profile, Preferences, Portfolio, Watchlist, etc.) now strictly require a valid JWT token.

### Action for Frontend:
- **Authorization Header:** Ensure every request to `/api/user/*` endpoints includes the standard header:
  ```http
  Authorization: Bearer <your_jwt_token>
  ```
- **Session Handling:** If a request returns a `401 Unauthorized`, the frontend must redirect the user to the login page as the session has expired or the token is invalid.

---

## 2. Portfolio Transaction Stability
Fixed a runtime crash that occurred when adding or selling stocks in a portfolio.

### Changes:
- **Fixed NameError:** The server no longer returns a `500 Internal Server Error` when submitting a trade.
- **Real-time Valuation:** The backend now fetches live market data immediately after a transaction to recalculate your portfolio's current value and gain/loss.

### Action for Frontend:
- **Success Handling:** You can now reliably expect a `201 Created` response with the updated transaction details.
- **Data Refresh:** After receiving a successful response from `POST /api/portfolio/<id>/transactions`, it is recommended to refresh the portfolio view to show the newly calculated totals.

---

## 3. Notification Anti-Spam (Watchlist Alerts)
Improved the legacy watchlist alert system to stop sending repetitive emails.

### Changes:
- **One-Time Alerts:** The system now "remembers" a price hit for 30 days. It will not send duplicate emails if a stock price stays near the target.
- **Precision:** The "hit" threshold has been narrowed from 1% to **0.5%** for better accuracy.

### Action for Frontend:
- **User Messaging:** Update the UI for Watchlist price targets (legacy) to inform users: *"You will receive a one-time notification when this price is reached."*
- **Best Practice:** Migration to the new `UserAlert` model is highly encouraged. Use `POST /api/user/alerts` which supports specific "Above" or "Below" conditions.

---

