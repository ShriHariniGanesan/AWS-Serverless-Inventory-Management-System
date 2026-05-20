# AWS Serverless Inventory Management System

A cloud-native inventory management application built using AWS serverless services. The application provides secure CRUD (Create, Read, Update, Delete) APIs for managing inventory records and uses Amazon Cognito for authentication and role-based access control.

---

## Live API Endpoint

**Base URL:** `https://w4tngaheg4.execute-api.us-east-2.amazonaws.com`

### API Endpoints

| Method | Endpoint      | Description                  | Access              |
| -----: | ------------- | ---------------------------- | ------------------- |
|    GET | `/items`      | Retrieve all inventory items | Authenticated users |
|    GET | `/items/{id}` | Retrieve a single item by ID | Authenticated users |
|   POST | `/items`      | Create a new inventory item  | Editors only        |
|    PUT | `/items/{id}` | Update an existing item      | Editors only        |
| DELETE | `/items/{id}` | Delete an item               | Editors only        |

---

## Demo Login URL (Amazon Cognito Managed Login)

```text
https://us-east-27oyven0wv.auth.us-east-2.amazoncognito.com/login?client_id=6o7ph8r40e9724heq245h9kg2l&response_type=code&scope=email+openid+phone&redirect_uri=http%3A%2F%2Flocalhost
```

> After signing in, Cognito redirects to `http://localhost/?code=...`. Exchange the authorization code for an `id_token` and use it in the `Authorization: Bearer <id_token>` header.

---

# Architecture Diagram

```text
┌─────────────┐
│    User     │
└──────┬──────┘
       │ Login
       ▼
┌──────────────────────┐
│ Amazon Cognito       │
│ Authentication + JWT │
└──────┬───────────────┘
       │ id_token
       ▼
┌──────────────────────┐
│ Amazon API Gateway   │
│ JWT Authorizer       │
└──────┬───────────────┘
       │ Validated Request
       ▼
┌──────────────────────┐
│ AWS Lambda (Python)  │
│ CRUD Business Logic  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│ Amazon DynamoDB      │
│ InventoryItems Table │
└──────────────────────┘
```

---

# Process Flow

## Authentication Flow

1. User opens the Cognito managed login page.
2. User signs in with username and password.
3. Amazon Cognito validates credentials.
4. Cognito redirects with an authorization code.
5. Authorization code is exchanged for an `id_token` (JWT).
6. The JWT is included in API requests.

## API Request Flow

1. Client sends a request to API Gateway.
2. API Gateway validates the JWT using the Cognito JWT Authorizer.
3. If valid, API Gateway invokes the Lambda function.
4. Lambda checks the user's Cognito group:

   * `viewers` → read-only access
   * `editors` → full CRUD access
5. Lambda performs DynamoDB operations.
6. JSON response is returned to the client.

---

# Features

* Serverless architecture using AWS managed services
* RESTful CRUD APIs in Python
* Secure authentication with Amazon Cognito
* JWT-based authorization
* Role-based access control (RBAC)
* NoSQL storage using DynamoDB
* CORS-enabled APIs
* End-to-end testing using Postman

---

# Technology Stack

* AWS Lambda
* Amazon API Gateway
* Amazon DynamoDB
* Amazon Cognito
* Python 3.13
* Postman
* OAuth 2.0
* JWT

---

# DynamoDB Schema

**Table Name:** `InventoryItems`

| Attribute | Type                   | Description        |
| --------- | ---------------------- | ------------------ |
| itemId    | String (Partition Key) | Unique identifier  |
| itemName  | String                 | Name of the item   |
| quantity  | Number                 | Available quantity |
| category  | String                 | Item category      |
| location  | String                 | Storage location   |

---

# Sample Inventory Record

```json
{
  "itemId": "1001",
  "itemName": "Laptop",
  "quantity": 8,
  "category": "Electronics",
  "location": "Waterloo Office"
}
```

---

# Lambda Function Responsibilities

* Route requests based on HTTP method and path
* Validate JWT claims and Cognito groups
* Perform CRUD operations in DynamoDB
* Convert DynamoDB Decimal values to JSON-friendly types
* Return structured JSON responses

---

# Cognito Groups

| Group   | Permissions            |
| ------- | ---------------------- |
| viewers | GET only               |
| editors | GET, POST, PUT, DELETE |

---

# API Examples

## Create Item

```http
POST /items
Authorization: Bearer <id_token>
Content-Type: application/json
```

```json
{
  "itemId": "1001",
  "itemName": "Laptop",
  "quantity": 8,
  "category": "Electronics",
  "location": "Waterloo Office"
}
```

## Get All Items

```http
GET /items
Authorization: Bearer <id_token>
```

## Update Item

```http
PUT /items/1001
Authorization: Bearer <id_token>
```

## Delete Item

```http
DELETE /items/1001
Authorization: Bearer <id_token>
```

---

# Deployment Steps

1. Create DynamoDB table `InventoryItems`
2. Create Lambda function and configure IAM role
3. Upload Python CRUD code
4. Set environment variable `TABLE_NAME=InventoryItems`
5. Create HTTP API in API Gateway
6. Configure JWT Authorizer with Cognito
7. Create Cognito User Pool and Groups
8. Assign users to `viewers` and `editors`
9. Test using Postman

---

# Testing with Postman

1. Login through Cognito Managed Login URL.
2. Copy the authorization `code` from the redirect URL.
3. Exchange the code for an `id_token`.
4. Use the token in the `Authorization` header.
5. Call secured API endpoints.

---

# Future Enhancements

* Static frontend hosted on Amazon S3
* CI/CD with GitHub Actions
* Custom domain with HTTPS
* CloudWatch dashboards and alarms
* Unit and integration tests

---

# Author

**Shri Harini Ganesan**

* LinkedIn: [https://www.linkedin.com/](https://www.linkedin.com/)
* GitHub: [https://github.com/](https://github.com/)

---

# License

This project is intended for educational and portfolio purposes.
