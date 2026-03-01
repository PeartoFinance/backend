# 📘 Frontend Integration Guide: Pearto Updates

This document outlines recent backend changes that require updates or integration in the Pearto frontend.

---

## 1. Course Enrollment (NEW: Paywall)
**Endpoint:** `POST /api/education/courses/<course_id>/enroll`

Previously, this allowed any logged-in user to enroll. Now, it checks if a course is **Paid** or **Free**.

### 🔴 NEW: Payment Flow (Step-by-Step)

If the user receives a `402` error or clicks a "Buy Now" button, follow this flow:

**Step 1: Initiate Checkout**
- **Endpoint:** `POST /api/education/courses/<course_id>/checkout`
- **Body:** `{"gateway": "stripe"}` or `{"gateway": "paypal"}`
- **Response:** 
```json
{
  "order_id": "...", 
  "approval_url": "https://..." 
}
```
- **UI:** Redirect the browser to the `approval_url`.

**Step 2: Payment Verification (On Return)**
- After the user pays, the gateway redirects them back to your `success_url`.
- From that page, call the Capture endpoint:
- **Endpoint:** `POST /api/education/courses/<course_id>/capture`
- **Body:** `{"gateway": "stripe/paypal", "order_id": "...session_id_from_url..."}`
- **Response:** `{"success": true, "message": "Purchase confirmed"}`
- **UI:** Show a success message and allow the user to access the course content!

---

### 🟢 Testing Purchases (Manual)
**Endpoint:** `POST /api/education/courses/<course_id>/purchase-manual`  
**Auth:** Required (Bearer Token)  
*Use this endpoint to instantly grant access to a course for testing purposes.*

---

## 2. Account Reactivation (NEW: Facebook-style)
**Endpoints:** `POST /api/auth/login` and `POST /api/auth/google-signin`

We now support automatic reactivation. If a user logs in with a previously deactivated account, the backend **instantly reactivates them** and completes the login.

### 🟢 NEW: Success Message
When a reactivation occurs, the success response includes an extra `message` field.

**JSON Response:**
```json
{
  "user": { ... },
  "token": "...",
  "message": "Your account has been reactivated. Welcome back!"
}
```

**UI Implementation:**
- Check for `response.data.message`.
- If present, show a "Welcome Back" notification/toast during redirection to the dashboard.

---

## 3. User Logout Integration
**Endpoint:** `POST /api/auth/logout`  
**Authentication:** Required (Bearer Token)

Previously, logging out on the frontend only cleared the local storage. The new endpoint ensures the session is permanently destroyed in the backend.

---

## 4. Market Overview Breadth Stats (Fixed)
**Endpoint:** `GET /api/market/overview`

The counts for Advancers, Decliners, and Unchanged now respect the `X-User-Country` header correctly. You can now rely on these fields for regional market summaries.

---

## 5. Security: Admin Privilege Escalation
**Endpoints:** `POST /api/admin/users` and `PATCH /api/admin/users/:id`

Only **Superadmins** can now create or modify accounts with administrative roles. Regular admins will receive a `403 Forbidden` if they attempt to escalate privileges.

---

*Guides maintained by Backend Team.*
