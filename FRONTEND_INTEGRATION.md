# Frontend Integration Guide

This document outlines the new data and features added to the backend, specifically related to User Management and Tools, and provides instructions for frontend integration.

## 1. User Management & Authentication

### Default Seed Data
The database seed script (`seed_demo_data.py`) now includes default users and roles to facilitate development and testing.

**Roles:**
- `admin`: Full access to all system features.
- `user`: Standard user access.
- `editor`: Access to content management features.

**Default Users:**

| Name | Email | Password | Role | Country |
|------|-------|----------|------|---------|
| Admin User | `admin@pearto.com` | `admin123` | `admin` | US |
| John Doe | `john@example.com` | `password123` | `user` | US |
| Jane Smith | `jane@example.com` | `password123` | `user` | UK |
| Rahul Sharma | `rahul@example.com` | `password123` | `user` | IN |

### Integration Points
- **Login Page**: Use the credentials above to test login functionality for different roles.
- **Admin Dashboard**: Log in as `admin@pearto.com` to access the Admin Dashboard.
- **User Profile**: Log in as any user to view and edit their profile.

## 2. Admin Tools Management

The backend provides API endpoints to manage system tools (calculators, planners, etc.).

### API Endpoints
- `GET /api/admin/tools`: List all available tools and their status.
- `POST /api/admin/tools`: Create a new tool configuration.
- `PATCH /api/admin/tools/<slug>`: Update a tool's settings (enable/disable, change name).
- `POST /api/admin/tools/bulk-toggle`: Bulk enable/disable tools.

### Seeded Tools
The following tools are seeded by default:
- SIP Calculator
- Compound Interest Calculator
- Loan EMI Calculator
- Goal Planner
- Income Tax Calculator
- ...and more.

### Integration Instructions
- **Admin Panel**: Create a "Tools Management" section in the admin panel where admins can toggle tools on/off.
- **Frontend Features**: Use the `enabled` flag from the API to conditionally render or hide tools in the main application menu.

## 3. Running the Seed Script

To populate your local database with this data:

```bash
# Ensure you are in the backend directory and venv is active
python seed_demo_data.py
```

This will create the necessary tables (if they don't exist) and populate them with the demo data described above.
