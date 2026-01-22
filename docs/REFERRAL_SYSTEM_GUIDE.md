# Referral System Documentation

This document explains how the new Referral System works and how to implement it on the frontend.

---

## 1. Overview
Every user now has a unique **Referral Code** (e.g., `PEARTO-X8K2fg`). They can share this code or a link with others. When a new user signs up using this code, they are automatically linked to the person who invited them.

---

## 2. Backend Changes
- **Database**: Added `referral_code` (unique string) and `referred_by` (ID of the referrer) to the `users` table.
- **Service**: Created `services/referral_service.py` to handle generating unique, readable codes and validating them.
- **Signup API**: Updated `/api/auth/signup` to accept an optional `referralCode` and link users.
- **Profile API**: Updated `/api/user/profile` to include the user's own `referralCode`.

---

## 3. API Endpoints for Frontend

### A. Get User's Referral Data
- **Endpoint**: `GET /api/user/referrals`
- **Auth**: Required (Bearer Token)
- **Response**:
```json
{
  "referralCode": "PEARTO-X8K2",
  "totalReferrals": 5,
  "totalRewardPoints": 500,
  "referrals": [
    {
      "id": 10,
      "name": "Jane Doe",
      "email": "jan***@gmail.com",
      "createdAt": "2026-01-22T12:00:00",
      "status": "active"
    }
  ]
}
```

### B. Signup with Referral
- **Endpoint**: `POST /api/auth/signup`
- **Body**:
```json
{
  "name": "New User",
  "email": "new@example.com",
  "password": "password123",
  "referralCode": "PEARTO-X8K2"  // Optional
}
```

---

## 4. Frontend Implementation Guide

### Step 1: Showing the Referral Link
The frontend can generate a sharing link using the `referralCode` found in the user's profile or the `/referrals` API:
`const shareLink = "https://pearto.com/signup?ref=" + user.referralCode;`

### Step 2: Capturing the Code from URL
When a guest lands on the signup page, check for the `ref` parameter in the URL:
```javascript
// Example: pearto.com/signup?ref=PEARTO-X8K2
const urlParams = new URLSearchParams(window.location.search);
const referralCode = urlParams.get('ref');
```

### Step 3: The Signup Form
1.  **Automatic**: If a code is found in the URL, pre-fill a (possibly hidden) input field in the signup form.
2.  **Manual**: Allow users to manually type a referral code into an optional input box if they have one.
3.  **Submit**: Send the code in the `referralCode` field of the signup JSON request.

---

## 5. Security & Privacy
- **Email Masking**: The list of referred users masks emails (e.g., `joh***@gmail.com`) to protect user privacy.
- **Validation**: If an invalid or expired referral code is sent, the backend will still complete the signup normally but will simply not link the user to a referrer.
