# User Data Backup & Account Security Update

This document summarizes the new features and security improvements implemented to handle user data portability and account lifecycle management.

---

## 1. User Data Backup & Restore
Users can now export their entire financial profile as a JSON file and restore it later (even on a new account).

### Backend Components:
- **`services/backup_service.py`**: The core logic that gathers data from 8+ tables (Portfolios, Holdings, Transactions, Watchlists, Alerts, etc.) and handles the complex restoration process.
- **`routes/backup.py`**: Exposes the APIs for the frontend.

### APIs for Frontend:
1. **Export Data**
   - **Endpoint**: `GET /api/backup/export`
   - **Auth**: Required (Bearer Token)
   - **Response**: A downloadable `.json` file containing the user's profile, portfolios, and settings.

2. **Import Data**
   - **Endpoint**: `POST /api/backup/import`
   - **Auth**: Required (Bearer Token)
   - **Body**: `multipart/form-data` with a field named `file`.
   - **Logic**: It deletes existing portfolios/watchlists and replaces them with the data from the file. It generates fresh IDs for everything to prevent database conflicts.

---

## 2. Enhanced Account Security
We fixed a vulnerability where deleted or deactivated users could still log in or use their old tokens.

### Changes:
- **Login Block**: The `/api/auth/login` route now checks `account_status`. If the account is `deleted`, `deactivated`, or `suspended`, login is denied with a `403 Forbidden` error.
- **Global API Protection**: The `@auth_required` decorator now checks the account status on **every single request**. If an account is deleted, all active tokens are instantly invalidated.
- **Helper Protection**: The `get_current_user` utility in `user.py` also enforces these status checks.

---

## 3. Automated Account Cleanup (Maintenance)
To save database costs and respect user privacy, we implemented an automated "Hard Delete" system.

### How it works:
- **Soft Delete**: When a user clicks "Delete," their status changes to `deleted`. They are locked out, but their data stays in the DB for **30 days**.
- **Reactivation**: Within those 30 days, a user can use the `/api/account/reactivate` route to restore their account.
- **Hard Delete**: After 30 days, a background job permanently wipes all their data from the database.

### Maintenance (DevOps):
- **Job**: `jobs/system_jobs.py` contains the `cleanup_deleted_accounts` function.
- **Trigger**: A new route `GET /api/cron/cleanup-accounts?token=...` has been added to `routes/cron.py`.
- **Action**: This URL should be called once every 24 hours via **cPanel Cron Handler**.

---

## 4. Frontend Implementation Guide

### Handling Export (Download)
When the user clicks "Export," use a method that handles file streams:
```javascript
const downloadBackup = async () => {
  const response = await fetch('/api/backup/export', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `pearto_backup_${new Date().toISOString().split('T')[0]}.json`;
  a.click();
};
```

### Handling Import (Upload)
Use `FormData` to send the file:
```javascript
const importBackup = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/backup/import', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  const result = await response.json();
  if (result.success) alert("Data Restored!");
};
```

### Handling Security Errors
If the user is deleted or deactivated, the backend will return a `403` status. The frontend should catch this and redirect the user to a "Reactivate Account" or "Account Deleted" page.
