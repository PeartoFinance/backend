# Vendor System API Documentation

This guide documents the Vendor System, a specialized module for managing partner integrations, ad placements, and service providers across the platform.

---

## 1. Overview
The Vendor System allows the admin to:
1.  Manage a directory of service providers (Banks, Insurance Agents, Brokers).
2.  Issue API Keys and Webhooks for partners to send real-time leads.
3.  Collect and moderate User Reviews.
4.  Track historical data (e.g., Interest Rates over time) for visualization.
5.  Integrate these vendors automatically into 50+ calculator tools.

---

## 2. Database Models
*   **`Vendor`**: Core profile (Name, Logo, Description, Rating).
*   **`VendorAPIKey`**: For partners to authenticate with our API.
*   **`VendorCustomAPI`**: Webhook configurations for lead generation.
*   **`VendorReview`**: User-submitted ratings and comments.
*   **`VendorHistory`**: Time-series data points (e.g., "FD Rate" on "2024-01-01") used for charting.

---

## 3. Admin APIs (Management)
Base URL: `/api/admin`
Auth: `Authorization: Bearer <admin_token>`

### Vendor CRUD
*   `GET /vendors`: List all vendors.
*   `POST /vendors`: Create a new vendor.
*   `GET /vendors/<id>`: Get full details + stats (key count, webhook count).
*   `PATCH /vendors/<id>`: Update profile (Name, Logo, Featured Status).
*   `DELETE /vendors/<id>`: Soft delete (suspend) vendor.

### API Keys & Webhooks
*   `GET /vendors/<id>/api-keys`: List active keys.
*   `POST /vendors/<id>/api-keys`: Generate new key pair (Returns Secret Key ONCE).
*   `DELETE /vendors/<id>/api-keys/<key_id>`: Revoke a key.
*   `GET /vendors/<id>/custom-apis`: List configured webhooks.
*   `POST /vendors/<id>/custom-apis`: Configure a new webhook endpoint.

### Content Management
*   `GET /vendors/<id>/reviews`: Get user reviews for moderation.
*   `DELETE /reviews/<id>`: Delete inappropriate reviews.
*   `GET /vendors/<id>/history`: Get historical data points.
*   `POST /vendors/<id>/history`: Add a data point (e.g., today's interest rate).
    *   **Body**: `{"date": "2024-01-01", "metrics": {"interest_rate": 7.5}}`

---

## 4. Public APIs (Integration)
Base URL: `/api/public/vendors`
Auth: None (except for posting reviews)

### Directory & Details
*   `GET /`: List active vendors. Supports filters:
    *   `category` (e.g., "Banking")
    *   `service` (e.g., "Home Loan")
    *   `limit` (e.g., 3)
*   `GET /<id>`: Get public profile, including aggregate rating and review count.

### Reviews & Data
*   `GET /<id>/reviews`: Get paginated user reviews.
*   `POST /<id>/reviews`: Submit a review (**Requires Auth**).
    *   **Body**: `{"rating": 5, "comment": "Great service!"}`
*   `GET /<id>/history`: Get time-series data for valid metrics.
    *   **Params**: `metric=interest_rate&days=365`

---

## 5. Global Tool Integration
The frontend uses a centralized system to inject vendors into tools automatically.

### CalculatorLayout Strategy
Instead of modifying 100+ individual tools, the `CalculatorLayout.tsx` component handles vendor injection.

1.  **Detection**: It checks the `category` prop passed by the tool (e.g., `category="Investing"`).
2.  **Mapping**: It looks up the corresponding Vendor Category in `VENDOR_CATEGORY_MAP`.
    *   *Investing* -> *Investment*
    *   *Finance & Loans* -> *Banking*
    *   *Insurance* -> *Insurance*
3.  **Injection**: If no custom `rightColumn` is provided by the tool, it automatically renders the `VendorList` component with the mapped category.

**Benefits**:
*   **Zero-Config**: New tools get vendor recommendations automatically just by setting a valid category.
*   **Consistency**: All tools in a category show the same high-quality partners.
*   **Optimization**: Updates to vendor logic happen in one place (`CalculatorLayout`).
