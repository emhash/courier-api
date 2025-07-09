# Courier Management System Backend API

This is a RESTful backend API for a Courier Management System, built with Django and Django REST Framework. It supports multiple user roles (Admin, Delivery Man, User) and provides functionality for user authentication, order management, and payment processing with Stripe.

## Features
- Swagger for API Documentation
- User registration and authentication using JWT
- Role-based access control (Admin, Delivery Man, User)
- Order creation, retrieval, and updates
- Payment integration with Stripe (Checkout Sessions, Payment Intents, and Webhooks)
- Admin management of orders and delivery assignments
- API documentation with Swagger UI
- Payment success and cancel pages for frontend integration

## Setup Instructions

To set up and run the API locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/courier-management-system.git
   cd courier-management-system
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *Note:* Ensure you have a `requirements.txt` file with dependencies like `django`, `djangorestframework`, `djangorestframework-simplejwt`, `drf-spectacular`, and `stripe`.

4. **Set up environment variables:**
   Create a `.env` file in the project root with the following:
   ```env
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   STRIPE_SECRET_KEY=your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
   FRONTEND_URL=http://localhost:8000
   ```
   - Replace `your_django_secret_key` with a secure key (e.g., generated via Django's `get_random_secret_key()`).
   - Obtain `your_stripe_secret_key` from your Stripe dashboard (use a test key for development).
   - Get `your_stripe_webhook_secret` from your Stripe webhook endpoint configuration.
   - Set `FRONTEND_URL` to your frontend application URL (defaults to backend URL for development).

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://localhost:8000/`.

8. **Access API Documentation:**
   - Swagger UI: `http://localhost:8000/api/docs/`
   - ReDoc: `http://localhost:8000/api/redoc/`
   - Homepage automatically redirects to Swagger UI

## Authentication

The API uses JSON Web Tokens (JWT) for authentication. Users must register and log in to obtain an access token, which is required for authenticated endpoints.

### Register a New User
- **Endpoint:** `POST /api/v1/auth/register/`
- **Description:** Register a new user with a specified role.
- **Request:**
  ```bash
  curl --location 'http://localhost:8000/api/v1/auth/register/' \
  --form 'email="md.e.h.ashiq@gmail.com"' \
  --form 'password="111111qqqqqq"' \
  --form 'username="ashiq"' \
  --form 'confirm_password="111111qqqqqq"' \
  --form 'role="admin"'
  ```
- **Response:**
  ```json
  {
      "success": true,
      "statusCode": 201,
      "message": "User Registration successful",
      "data": {
          "username": "ashiq",
          "email": "md.e.h.ashiq@gmail.com",
          "role": "admin",
          "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
  }
  ```

### Log In
- **Endpoint:** `POST /api/v1/auth/login/`
- **Description:** Log in to obtain access and refresh tokens.
- **Request:**
  ```bash
  curl --location 'http://localhost:8000/api/v1/auth/login/' \
  --form 'username_or_email="md.e.h.ashiq@gmail.com"' \
  --form 'password="111111qqqqqq"'
  ```
- **Response:**
  ```json
  {
      "success": true,
      "statusCode": 200,
      "message": "Login successful",
      "data": {
          "username": "ashiq",
          "email": "md.e.h.ashiq@gmail.com",
          "role": "admin",
          "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
  }
  ```

### Get Profile
- **Endpoint:** `GET /api/v1/auth/profile/`
- **Description:** Retrieve the authenticated user's profile (requires token).
- **Request:**
  ```bash
  curl --location --request GET 'http://localhost:8000/api/v1/auth/profile/' \
  --header 'Authorization: Bearer <access_token>'
  ```
- **Response:**
  ```json
  {
      "success": true,
      "statusCode": 200,
      "message": "User profile loaded successfully",
      "data": {
          "id": 5,
          "username": "ashiq",
          "first_name": "",
          "last_name": "",
          "email": "md.e.h.ashiq@gmail.com",
          "role": "admin"
      }
  }
  ```

### Update Profile
- **Endpoint:** `PUT /api/v1/auth/profile/`
- **Description:** Update the authenticated user's profile (requires token).
- **Request:**
  ```bash
  curl --location --request PUT 'http://localhost:8000/api/v1/auth/profile/' \
  --header 'Authorization: Bearer <access_token>' \
  --form 'first_name="E. H."' \
  --form 'last_name="Ashiq"'
  ```
- **Response:**
  ```json
  {
      "success": true,
      "statusCode": 200,
      "message": "User profile updated successfully",
      "data": {
          "id": 5,
          "username": "ashiq",
          "first_name": "E. H.",
          "last_name": "Ashiq",
          "email": "md.e.h.ashiq@gmail.com",
          "role": "admin"
      }
  }
  ```

## API Endpoints

### Orders

#### Create Order
- **Endpoint:** `POST /api/v1/orders/`
- **Description:** Create a new order (users only, requires token).
- **Request:**
  ```bash
  curl --location 'http://localhost:8000/api/v1/orders/' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <access_token>' \
  --data '{
      "description": "Pickup documents from Gulshan office and deliver to Dhanmondi residence",
      "address": "House 45, Road 12A, Dhanmondi, Dhaka-1209",
      "cost": "250.00"
  }'
  ```
- **Response:**
  ```json
  {
      "success": true,
      "statusCode": 201,
      "message": "Order created successfully",
      "data": {
          "id": 1,
          "customer": "nasir_ahmed",
          "delivery_man": null,
          "description": "Pickup documents from Gulshan office and deliver to Dhanmondi residence",
          "address": "House 45, Road 12A, Dhanmondi, Dhaka-1209",
          "cost": "250.00",
          "status": "PENDING",
          "created_at": "2025-07-08T17:46:17.043515Z",
          "updated_at": "2025-07-08T17:46:17.043515Z"
      }
  }
  ```

#### List Orders
- **Endpoint:** `GET /api/v1/orders/`
- **Description:** Retrieve a list of orders (filtered by role, requires token).
- **Request:**
  ```bash
  curl --location 'http://localhost:8000/api/v1/orders/' \
  --header 'Authorization: Bearer <access_token>'
  ```
- **Response:**
  ```json
  {
      "success": true,
      "statusCode": 200,
      "message": "Orders retrieved successfully",
      "data": {
          "count": 1,
          "next": null,
          "previous": null,
          "results": [
              {
                  "id": 1,
                  "customer": "nasir_ahmed",
                  "delivery_man": null,
                  "description": "Pickup documents from Gulshan office and deliver to Dhanmondi residence",
                  "address": "House 45, Road 12A, Dhanmondi, Dhaka-1209",
                  "cost": "250.00",
                  "status": "PENDING",
                  "created_at": "2025-07-08T17:46:17.043515Z",
                  "updated_at": "2025-07-08T17:46:17.043515Z"
              }
          ]
      }
  }
  ```

#### Get Order Details
- **Endpoint:** `GET /api/v1/orders/{id}/`
- **Description:** Retrieve details of a specific order (role-based access, requires token).
- **Request:**
  ```bash
  curl --location 'http://localhost:8000/api/v1/orders/1/' \
  --header 'Authorization: Bearer <access_token>'
  ```
- **Response:**
  ```json
  {
      "success": true,
      "statusCode": 200,
      "message": "Order retrieved successfully",
      "data": {
          "id": 1,
          "customer": "nasir_ahmed",
          "delivery_man": null,
          "description": "Pickup documents from Gulshan office and deliver to Dhanmondi residence",
          "address": "House 45, Road 12A, Dhanmondi, Dhaka-1209",
          "cost": "250.00",
          "status": "PENDING",
          "created_at": "2025-07-08T17:46:17.043515Z",
          "updated_at": "2025-07-08T17:46:17.043515Z"
      }
  }
  ```

#### Update Order (Admin Only)
- **Endpoint:** `PATCH /api/v1/orders/{id}/update/`
- **Description:** Update an order, e.g., assign a delivery man (admins only, requires token).
- **Request:**
  ```bash
  curl --location --request PATCH 'http://localhost:8000/api/v1/orders/1/update/' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <access_token>' \
  --data '{
      "delivery_man": "rafiq_delivery",
      "status": "PENDING",
      "description": "Get the delivery fast",
      "address": "Dhaka"
  }'
  ```
- **Response:**
  ```json
  {
      "success": true,
      "statusCode": 200,
      "message": "Order updated successfully",
      "data": {
          "id": 1,
          "customer": "nasir_ahmed",
          "delivery_man": "rafiq_delivery",
          "description": "Get the delivery fast",
          "address": "Dhaka",
          "cost": "250.00",
          "status": "PENDING",
          "created_at": "2025-07-08T17:46:17.043515Z",
          "updated_at": "2025-07-08T18:03:09.510283Z"
      }
  }
  ```

### Payments

**SIMPLIFIED PAYMENT FLOW:**
1. User creates order (no payment)
2. User hits checkout API to get Stripe payment URL
3. User pays on Stripe → webhook updates order status
4. Done!

#### Create Stripe Checkout Session (ONLY Payment Method)
- **Endpoint:** `POST /api/v1/payments/checkout/`
- **Description:** Create a Stripe Checkout Session for order payment (users only, requires token).
- **Request:**
  ```bash
  curl --location 'http://localhost:8000/api/v1/payments/checkout/' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer <access_token>' \
  --data '{
      "order_id": 1
  }'
  ```
- **Response:**
  ```json
  {
      "message": "Checkout session created successfully. Redirect user to checkout_url",
      "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
      "session_id": "cs_test_...",
      "order_id": 1,
      "amount": "250.00"
  }
  ```

#### Stripe Webhook Endpoint
- **Endpoint:** `POST /api/v1/payments/webhook/`
- **Description:** Handle Stripe webhook events (no authentication required, secured by webhook signature).
- **Note:** This endpoint is automatically called by Stripe to notify about payment status changes.

## Payment Success and Cancel Pages

The system includes built-in HTML pages for handling payment success and cancellation:

### Payment Success Page
- **URL:** `http://localhost:8000/payment/success/`
- **Features:**
  - Displays payment confirmation
  - Shows order details via JavaScript API calls
  - Handles session ID from Stripe redirect
  - Responsive design with loading states
  - Links to view orders and return home

### Payment Cancel Page
- **URL:** `http://localhost:8000/payment/cancel/`
- **Features:**
  - Shows payment cancellation message
  - Displays order summary
  - Provides retry payment functionality
  - Links to view orders and return home

These pages are designed to work with both backend and frontend teams, using JavaScript to make API calls for dynamic content loading.

## Roles and Permissions

- **Admin:** Full access to manage users, orders, and assign delivery men.
- **Delivery Man:** Can view and update the status of their assigned orders (not fully detailed in provided CURLs; assumed to use standard endpoints with permission checks).
- **User:** Can register, log in, create orders, view their own orders, and process payments.

## Payment Integration

The API integrates with Stripe for payment processing using a simple checkout flow:

### Simple Payment Flow
1. **User creates order** - No payment required during creation
2. **User calls checkout API** - Gets Stripe hosted checkout URL  
3. **User pays on Stripe** - Secure payment processing
4. **Webhook updates status** - Payment completion handled automatically

### Stripe Checkout (ONLY Payment Method)
- **Use Case:** Hosted payment page with built-in security and compliance
- **Implementation:** Create checkout session via `/api/v1/payments/checkout/`
- **Redirect URLs:** Configurable success and cancel URLs (defaults to FRONTEND_URL)
- **Features:** Automatic webhook handling, PCI compliance, mobile responsive

### Environment Variables
Ensure the following are set in your `.env` file:
- `STRIPE_SECRET_KEY`: Your Stripe secret key (use test keys for development)
- `STRIPE_WEBHOOK_SECRET`: Webhook endpoint secret for signature verification
- `FRONTEND_URL`: Base URL for success/cancel redirects (defaults to http://localhost:8000)

### Test Payment Methods
Use Stripe's test payment methods for development:
- **Visa:** Card number `4242424242424242`
- **Mastercard:** Card number `5555555555554444`
- **Declined:** Card number `4000000000000002`

## Database Schema

The Entity-Relationship Diagram (ERD) is available in the repository as `erd.png`. It includes:
- **User:** id, username, email, role, etc.
- **Order:** id, customer (FK to User), delivery_man (FK to User, nullable), description, address, cost, status, payment_status, etc.
- **Payment:** id, order (FK to Order), amount, stripe_payment_intent_id, status, etc.

![ERD](erd.png)

## API Documentation

The API includes comprehensive documentation accessible at:
- **Swagger UI:** `http://localhost:8000/api/docs/` (Interactive documentation)
- **ReDoc:** `http://localhost:8000/api/redoc/` (Alternative documentation view)
- **OpenAPI Schema:** `http://localhost:8000/api/schema/` (Raw OpenAPI 3.0 schema)

The documentation includes:
- Authentication examples with JWT Bearer tokens
- Request/response schemas for all endpoints
- Interactive testing interface
- Role-based access documentation
- Payment flow examples

## Sample Credentials

For testing, register users with the following details via the `/api/v1/auth/register/` endpoint:
| Role         | Username       | Password       | Email                  |
|--------------|----------------|----------------|------------------------|
| Admin        | ashiq          | 111111qqqqqq   | md.e.h.ashiq@gmail.com |
| User         | nasir_ahmed    | (set via register) | (set via register)  |
| Delivery Man | rafiq_delivery | (set via register) | (set via register)  |

## Postman Collection

A Postman collection with all endpoints and example requests is available in the repository as `Courier_Management_System.postman_collection.json`. Import it into Postman to test the API.

## Error Responses

- **Unauthorized:**
  ```json
  {
      "success": false,
      "message": "Authentication credentials were not provided."
  }
  ```
- **Not Found:**
  ```json
  {
      "success": false,
      "message": "Order not found."
  }
  ```
- **Validation Error:**
  ```json
  {
      "success": false,
      "message": "Invalid data.",
      "errorDetails": {
          "cost": ["A valid number is required."]
      }
  }
  ```