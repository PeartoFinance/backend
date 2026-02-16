# Frontend Integration Guide: Session & Market Data Updates

This document outlines recent backend changes that require updates or integration in the Pearto frontend.

## 1. User Logout Integration (NEW)

**Endpoint:** `POST /api/auth/logout`  
**Authentication:** Required (Bearer Token)

### Why this is needed:
Previously, logging out on the frontend only cleared the local storage. This left the user's session active in our database ("Ghost Sessions"). The new endpoint ensures the session is permanently destroyed in the backend for security and performance.

### Implementation Task:
In your `authService.js` (or equivalent), update your logout function to call the backend before clearing local storage.

```javascript
// Example implementation
const logout = async () => {
  try {
    const token = localStorage.getItem('token');
    await axios.post('/api/auth/logout', {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
  } catch (err) {
    console.error("Logout failed in backend, clearing local storage anyway", err);
  } finally {
    // Standard cleanup
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }
};
```

---

## 2. Market Overview Breadth Stats (FIXED)

**Endpoint:** `GET /api/market/overview`

### What changed:
The summary statistics at the bottom of the Market Overview page (Advancers, Decliners, Total Volume) were previously showing **Global** data even when a user had selected a specific country. 

### Implementation Note:
The counts now correctly respect the `X-User-Country` header. 
- If you send `X-User-Country: NP`, the summary will show stats for Nepal.
- If you send no header, it defaults to Global/US stats.

**UI Side:** Check if you were manually calculating or hiding these counts due to data mismatches. You can now rely on the `advancers`, `decliners`, and `unchanged` fields returned by the `/overview` endpoint as they are now accurate to the selected region.

---

## 3. Security Warning: Admin Privilege Escalation

**Endpoint:** `POST /api/admin/users` and `PATCH /api/admin/users/:id`

### What changed:
We have implemented **Superadmin-only** checks for role modifications. 

### Implementation Note:
If a "Junior Admin" tries to create another Admin or promote someone to Admin, the API will return:
- **Status:** `403 Forbidden`
- **Error:** `Only Superadmins can create/modify admin accounts`

**UI Side:** You should hide the "Role" dropdown or disable the "Admin" option if the current user is not a Superadmin to prevent users from seeing these errors.

---

*Guides maintained by Backend Team.*
