# Frontend Integration Guide: New Financial Features
**Date:** 2026-01-31  

This is the Guide for the frontend team to implement the new financial features. Follow these specifications exactly to ensure full functionality.

---

## 1. Financial Goal Tracker 🎯

**Overview:**  
Users can set financial targets to track their wealth. The backend supports two distinct tracking modes:
1.  **Global Net Worth:** Tracks the user's Total Wealth across *all* accounts.
2.  **Specific Portfolio:** Tracks only ONE specific portfolio (e.g., "Retirement Fund").

### 🛠️ Frontend Implementation Requirements:

#### A. Goal Creation (POST)
**UI:** Create a "New Goal" modal/page.
*   **Fields:**
    *   **Goal Name:** (e.g., "Buy a House")
    *   **Target Amount:** (Number, e.g., 50000)
    *   **Target Date:** (Date Picker)
    *   **Start Amount:** (Optional) If left empty, backend uses current value.
    *   **"Track Specific Portfolio?" (Toggle/Checkbox):**
        *   **OFF (Default):** Send `portfolio_id: null`. (Tracks Global Net Worth).
        *   **ON:** Show a dropdown of users' portfolios. Send the selected `portfolio_id`.

**API Endpoint:** `POST /api/portfolio/financial-goals`
**Payload Example:**
```json
{
  "target_amount": 100000,
  "target_date": "2030-12-31",
  "portfolio_id": "uuid-123-456" // OR null for Global
}
```

#### B. Goals Dashboard (GET)
**UI:** Display a list of active goals.
*   **Progress Bar:** Use `progress_percent` from the API.
*   **Badge/Status:**
    *   If `status` is `'achieved'`, show a "🎉 Accomplished" badge.
    *   If `status` is `'active'`, show "In Progress".
*   **Amounts:** Display `current_amount` vs `target_amount`.
    *   *Note:* `current_amount` is auto-calculated by backend based on the chosen tracking mode.

**API Endpoint:** `GET /api/portfolio/financial-goals`
**Response Fields to Use:**
*   `progress_percent` (0-100)
*   `current_amount`
*   `target_amount`
*   `status` ('active', 'achieved')
*   `id` (Needed for deletion)

#### C. Goal Deletion (DELETE)
**UI:** Add a "Delete" (Trash icon) button on each goal card.
*   **Action:** Confirm deletion with user ("Are you sure?"), then call API.
*   **On Success:** Remove the card from the UI immediately.

**API Endpoint:** `DELETE /api/portfolio/financial-goals/<id>`

---

## 2. Earnings Report Reminders 🔔

**Overview:**  
The backend now automatically scans the user's **Holdings** (stocks they own) and sends email/push alerts 1 day before an earnings report.

### 🛠️ Frontend Implementation Requirements:

#### A. Settings Page
**UI:** In the "Notifications" tab of User Settings.
*   **Toggle:** Add a switch labeled **"Earnings Reminders"**.
*   **Mapping:** This controls the `email_earnings` and `push_earnings` preferences.

#### B. Portfolio UI (Enhancement)
**UI:** In the main Portfolio Table (where rows of stocks are shown).
*   **Logic:** Check the `earnings_date` field for each stock.
*   **Visual:** If an earnings date is **Tomorrow** or **Today**:
    *   Show a small **🔔** icon next to the stock symbol.
    *   Tooltip: "Earnings Report Tomorrow".

---

## 3. Daily P&L Email Summary 📉

**Overview:**  
A new "Morning Briefing" email that summarizes yesterday's portfolio performance (Profit/Loss).

### 🛠️ Frontend Implementation Requirements:

#### A. Settings Page
**UI:** In the "Notifications" tab of User Settings.
*   **New Toggle:** Add a NEW switch labeled **"Daily Portfolio Summary"**.
*   **Description:** "Receive a daily email summary of your portfolio's performance."
*   **Mapping:** This MUST update the new `emailPortfolioSummary` field in the user preferences API.
*   **Default State:** On (True).

**API Endpoint:** `PATCH /api/user/notification-preferences`
**Payload to Send:**
```json
{
  "emailPortfolioSummary": true // or false
}
```



1.  **Goal Tracking**: Create two goals—one "Global" and one "Specific Portfolio". Ensure `current_amount` is different for each (if the user has multiple portfolios).
2.  **Goal Deletion**: Ensure you can delete a goal and it disappears.
3.  **P&L Toggle**: Go to Settings -> Notifications. Ensure you see the new "Daily Portfolio Summary" toggle and that it saves its state.
