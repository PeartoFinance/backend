# Frontend Integration Guide

This document outlines the new data and features added to the backend, specifically related to User Management and Tools, and provides instructions for frontend integration.

## 1. User Management & Authentication

### Default Seed Data
The database seed script (`seed_demo_data.py`) now includes default users and roles to facilitate development and testing.

**Roles:**
- `admin`: Full access to all system features.
- `user`: Standard user access.

**Default Users Example:**

| Name | Email | Password | Role
|------|-------|----------|------|---------|
| Admin User | `admin@pearto.com` | `admin123` | `admin`

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
````markdown
# Frontend Integration Guide

This document outlines the new data and features added to the backend, specifically related to User Management, Tools, and Admin endpoints, and provides instructions for frontend integration.

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

## 4. Admin Authentication (headers)

Admin endpoints require admin authentication. The backend accepts either:

- `Authorization: Bearer {{admin_token}}`  — preferred (JWT or shared secret)
- `X-Admin-Secret: {{admin_token}}` — legacy header (still supported)

Notes:
- For local development, when `ADMIN_SECRET_KEY` is not configured, the server accepts the fallback value `dev-admin-secret` for requests coming from `localhost` / `127.0.0.1`.
- Do not remove either header type in the frontend until server-side token issuance/validation is fully agreed upon.

Example header (Postman / curl):
```
Authorization: Bearer dev-admin-secret
X-Admin-Country: US
Content-Type: application/json
```

## 5. Country filtering (admin)

Admin APIs are country-aware. The server determines the effective country in this order:

1. `X-Admin-Country` header (used by admin routes and `get_country_context()`)
2. `X-User-Country` header (middleware sets `request.user_country`)
3. Fallback: `'US'`

Frontend guidance:
- To scope admin list endpoints to a specific country, send `X-Admin-Country: <ISO-2>` (e.g. `US`, `IN`, `GLOBAL`).
- When creating/updating records, include `countryCode` in the request body to ensure the stored object has the correct country.

## 6. Education admin APIs

Endpoints (admin):
- `GET /api/admin/education/courses` — list courses (respects `X-Admin-Country` / `X-User-Country`)
- `POST /api/admin/education/courses` — create course
- `PUT /api/admin/education/courses/<id>` — update course
- `DELETE /api/admin/education/courses/<id>` — delete course
- `GET /api/admin/education/instructors` — list instructors
- `POST /api/admin/education/instructors` — create instructor
- `GET /api/admin/education/stats` — aggregate stats

Create course — minimal JSON body:
```
{
	"title": "Intro to Investing",
	"description": "A short course on investing basics",
	"category": "Finance",
	"level": "Beginner",
	"durationHours": 8,
	"price": 0,
	"isPublished": true,
	"countryCode": "US",
	"instructorId": 1
}
```

Create instructor — example:
```
{
	"name": "Jane Doe",
	"title": "Senior Instructor",
	"bio": "Expert in personal finance and investing.",
	"avatarUrl": "",
	"expertise": "Finance",
	"isActive": true,
	"countryCode": "US"
}
```

Quick curl example (list courses scoped to US):
```bash
curl -H "Authorization: Bearer dev-admin-secret" -H "X-Admin-Country: US" \
	"http://127.0.0.1:5000/api/admin/education/courses"
```

---

If you want, I can add a ready-to-import Postman collection containing these admin requests (with environment variables `base_url` and `admin_token`).

````
