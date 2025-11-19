# Flask Backend for FullStack Application

This is a Python Flask implementation of the backend that maintains the same functionality as the original Express.js backend with Supabase integration.

## Features

- User authentication with JWT tokens
- OTP-based registration and password reset
- User profile management
- Account management (create, read, update, delete)
- Item management (create, read, update, delete)
- Supabase database integration
- Supabase Storage integration for file uploads
- Email notifications for OTPs

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Setup Instructions

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Copy the `.env.example` file to `.env` and update the values:
   ```bash
   cp .env.example .env
   ```
   
   Update the following variables in `.env`:
   - `SUPABASE_URL` - Your Supabase project URL
   - `SUPABASE_KEY` - Your Supabase anon key
   - `JWT_SECRET` - Your JWT secret (change this to a strong secret in production)
   - `EMAIL_HOST` - Your email SMTP host
   - `EMAIL_PORT` - Your email SMTP port
   - `EMAIL_USER` - Your email address
   - `EMAIL_PASS` - Your email app password

3. **Database Setup:**
   Make sure your Supabase database has the required tables:
   - `users` (with columns: id, firstname, middlename, lastname, email, password, profilePicture, token)
   - `accounts` (with columns: id, site, username, password, image, user_id)
   - `otps` (with columns: id, email, otp_code, created_at, expires_at)
   - `items` (with columns: id, name, description, user_id)

4. **Storage Setup:**
   Create a storage bucket named `images` in your Supabase project.

## Running the Application

```bash
python flask_app.py
```

The application will start on `http://localhost:5000` by default.

## API Endpoints

### Authentication
- `POST /request-otp` - Request OTP for registration
- `POST /forgot-password/request-otp` - Request OTP for password reset
- `POST /verify-otp-and-register` - Verify OTP and register user
- `POST /forgot-password/verify-otp` - Verify OTP for password reset
- `POST /forgot-password/reset` - Reset password
- `POST /login` - User login
- `POST /logout` - User logout

### User Management
- `GET /user-info` - Get user information
- `PUT /users/:id` - Update user information
- `POST /upload-profile-picture` - Upload profile picture
- `GET /profile-picture` - Get profile picture
- `POST /verify-current-password` - Verify current password
- `POST /change-password` - Change password

### Account Management
- `POST /accounts` - Create account
- `GET /accounts` - Get all accounts
- `PUT /accounts/:id` - Update account
- `DELETE /accounts/:id` - Delete account

### Item Management
- `POST /create` - Create item
- `GET /read` - Get all items
- `PUT /update` - Update item
- `DELETE /delete` - Delete item

## Project Structure

```
backend/
├── flask_app.py              # Main Flask application
├── config.py                 # Configuration settings
├── supabase_client.py        # Supabase client initialization
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
├── controllers/             # Controller functions
│   ├── auth_controller.py   # Authentication controllers
│   ├── user_controller.py   # User management controllers
│   ├── account_controller.py # Account management controllers
│   └── item_controller.py   # Item management controllers
├── routes/                  # API route definitions
│   ├── auth.py             # Authentication routes
│   ├── user.py             # User management routes
│   ├── account.py          # Account management routes
│   └── item.py             # Item management routes
├── middleware/              # Middleware functions
│   └── auth.py             # Authentication middleware
└── utils/                   # Utility functions
    ├── mailer.py           # Email sending utilities
    └── supabase_storage.py # Supabase Storage utilities
```

## Notes

- This Flask backend maintains 100% compatibility with the original Express.js backend functionality
- All Supabase database operations are preserved
- File upload functionality with Supabase Storage is maintained
- Email notifications for OTPs are implemented
- JWT token-based authentication is preserved
- All error handling and logging mechanisms are maintained