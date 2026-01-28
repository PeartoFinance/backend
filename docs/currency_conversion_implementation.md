# 💱 Currency Conversion API: Frontend Implementation Guide

This API allows the frontend to convert USD values into target currencies (like NPR, EUR, INR) for display purposes. The backend remains USD-denominated, and this API is used only to show localized values to the user.

---

## 🚀 The Workflow

1.  **Fetch Rates**: (Optional) Get a list of all available exchange rates to show in a settings menu.
2.  **Convert Value**: Call the conversion endpoint whenever you need to display a USD value in a local currency.

---

## 🛠 API Endpoints

### 1. Convert USD to Target Currency
**Endpoint:** `GET /api/currency/convert`  
**Parameters:**
*   `amount`: The USD value to convert (e.g., `150.25`)
*   `to`: The 3-letter target currency code (e.g., `NPR`, `EUR`, `INR`)

**Response Example:**
```json
{
    "original_amount_usd": 100.0,
    "converted_amount": 13350.0,
    "rate": 133.5,
    "currency": "NPR",
    "last_updated": "2024-01-28T10:00:00Z",
    "status": "success"
}
```

### 2. Get All Available Rates
**Endpoint:** `GET /api/currency/rates`

**Response Example:**
```json
{
    "status": "success",
    "rates": [
        {
            "pair": "USD/EUR",
            "rate": 0.92,
            "targetCurrency": "EUR",
            "last_updated": "2024-01-28T10:00:00Z"
        },
        {
            "pair": "USD/NPR",
            "rate": 133.5,
            "targetCurrency": "NPR",
            "last_updated": "2024-01-28T10:00:00Z"
        }
    ]
}
```

---

## 🎨 UI/UX Recommendations

### 1. Global Currency Selector
Add a currency dropdown in the user settings or navigation bar. When the user changes it, save their preference in `localStorage`.

### 2. Displaying Values
When displaying prices or portfolio totals:
*   If the user's preference is **USD**, show the value directly.
*   If the user's preference is **NPR**, call the conversion API and show the result with the appropriate symbol (e.g., `Rs. 13,350`).

### 3. Formatting
Always round the `converted_amount` to 2 decimal places for a clean look.

---

## 💡 Pro-Tips for Developers
*   **Caching**: Since exchange rates don't change every second, you can cache the rates in the frontend (e.g., for 30 minutes) to avoid making too many API calls.
*   **Bulk Conversion**: If you have a list of many stocks, it's better to fetch the rate once and do the math in the frontend rather than calling the API for every single row.

---

