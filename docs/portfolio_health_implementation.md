# 📊 Portfolio Health Score: Frontend Implementation Guide

This guide explains how to implement the **Portfolio Health Score** feature. This feature compares a user's actual holdings against their target goals to give them a "Health Score" (0-100) and actionable advice.

---

## 🚀 The Workflow (User Journey)

1.  **Check Score**: User clicks a "Check My Portfolio Score" button.
2.  **Check for Goals**:
    *   If the user **has not** set goals, show them the **"Set Your Strategy"** form.
    *   If the user **has** set goals, show them their **Health Score Dashboard**.
3.  **Update Strategy**: Users can update their target percentages at any time to change how their score is calculated.

---

## 🛠 API Endpoints

### 1. Get Current Health Score
**Endpoint:** `GET /api/portfolio/analysis/health-score`  
**Headers:** `Authorization: Bearer <token>`

**Response Example:**
```json
{
    "score": 85.5,
    "status": "Very Good",
    "total_value": 12500.0,
    "actual_allocation": {
        "stocks": 80.0,
        "crypto": 15.0,
        "cash": 5.0
    },
    "target_allocation": {
        "stocks": 70.0,
        "crypto": 10.0,
        "cash": 20.0
    },
    "recommendations": [
        "Your stocks allocation is 10% higher than your target. Consider selling some to rebalance.",
        "Your cash allocation is 15% lower than your target. Consider adding more."
    ],
    "benchmark": {
        "symbol": "^IXIC",
        "name": "NASDAQ Composite",
        "price": 15450.2,
        "change_percent": 1.2
    }
}
```

### 2. Get/Set Investment Goals
**Fetch Goals:** `GET /api/portfolio/goals`  
**Save Goals:** `POST /api/portfolio/goals`

**Request Body for Saving:**
```json
{
    "target_stocks_percent": 70,
    "target_bonds_percent": 10,
    "target_cash_percent": 10,
    "target_crypto_percent": 5,
    "target_commodities_percent": 5,
    "risk_tolerance": "moderate",
    "benchmark_symbol": "^GSPC"
}
```
> ⚠️ **Note:** All percentages must add up to exactly **100**. The `benchmark_symbol` can be `^GSPC` (S&P 500), `^IXIC` (NASDAQ), or `^DJI` (Dow Jones).

---

## 🎨 UI/UX Recommendations

### 1. The Score Gauge
Use a circular gauge or a progress bar to show the score (0-100).
*   **0-50**: Red (Needs Attention)
*   **51-75**: Yellow (Good)
*   **76-100**: Green (Excellent)

### 2. Comparison Chart
Use a **grouped bar chart** or two **pie charts** side-by-side:
*   **Chart A**: "My Current Portfolio" (Actual Allocation)
*   **Chart B**: "My Target Strategy" (Target Allocation)

### 3. Action Plan (Recommendations)
Display the `recommendations` array as a list of "Smart Tips." 
*   *Example:* "💡 Tip: You have too much Crypto. Sell some to stay safe!"

---

## Pro-Tips for Developers
*   **Empty State**: If the API returns `needs_setup: true`, automatically open the "Set Goals" modal.
*   **Defaults**: When the user opens the "Set Goals" form for the first time, call `GET /api/portfolio/goals` to get the default numbers (60/20/10/5/5) to pre-fill the inputs.
*   **Real-time Update**: After the user saves their goals, immediately call the `health-score` API again to refresh the dashboard without a page reload.

---

