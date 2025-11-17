# FullStack Express Application

A full-stack web application with user authentication, dashboard, and account management features.

## Features
- User Registration with OTP verification
- User Login/Logout
- Password Reset with OTP
- Dashboard with account management
- CRUD operations for accounts
- Responsive design

## Technologies Used

### Backend
- Node.js
- Express.js
- Supabase (Database and Storage)
- bcrypt (password hashing)
- jsonwebtoken (JWT authentication)
- nodemailer (sending OTP emails)

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- DataTables
- Toastify-JS

## Prerequisites

- Node.js (v14 or higher)
- Supabase account (free tier available)
- npm package manager

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/badboygamingph/express-vercel-deployment.git
cd "fullstack express final backup/fullstack"
```

### 2. Install Backend Dependencies
```bash
cd backend
npm install
```

### 3. Set up Supabase

#### Create Supabase Project
1. Go to [Supabase](https://supabase.io/) and create a free account
2. Create a new project
3. Note down your Project URL and API Key (anon key)

#### Configure Environment Variables
1. Copy `.env.example` to `.env` in the backend directory:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   JWT_SECRET=your_jwt_secret_key
   ```

#### Create Database Tables
Run the table creation script:
```bash
node create_supabase_tables.js
```

### 4. Configure Email (Nodemailer)
Update the email configuration in `backend/utils/mailer.js` with your SMTP settings:
- Gmail, Outlook, or any SMTP provider
- Username and password or app-specific password

### 5. Install Frontend Dependencies (Optional)
```bash
cd ../frontend
# Frontend dependencies are mostly CDN-based, but you can install any needed packages
```

### 6. Run the Application
```bash
cd ../backend
npm start
```

### 7. Access the Application
Open your browser and navigate to `http://localhost:5000`

## Project Structure
```
.
├── backend/
│   ├── config/
│   │   └── config.js          # Configuration settings
│   ├── controllers/
│   │   ├── authController.js  # Authentication logic
│   │   ├── userController.js  # User management logic
│   │   ├── itemController.js  # Item management logic
│   │   └── accountController.js # Account management logic
│   ├── middleware/
│   │   └── auth.js            # Authentication middleware
│   ├── routes/
│   │   ├── authRoutes.js      # Authentication routes
│   │   ├── userRoutes.js      # User routes
│   │   ├── itemRoutes.js      # Item routes
│   │   └── accountRoutes.js   # Account routes
│   ├── sql/
│   │   └── create_tables.sql  # SQL table definitions
│   ├── utils/
│   │   └── mailer.js          # Email utility
│   ├── app.js                 # Main application file
│   ├── db.js                  # Database connection
│   ├── package.json           # Backend dependencies
│   └── vercel.json            # Vercel deployment configuration
└── frontend/
    ├── css/
    │   └── style.css          # Main stylesheet
    ├── js/
    │   └── script.js          # Main JavaScript file
    ├── templates/
    │   ├── otp_email.html     # OTP email template
    │   └── forgot_password_otp_email.html # Password reset OTP template
    ├── dashboard.html         # Dashboard page
    └── index.html             # Main login/registration page
```

## How to Use the Application

### User Registration
1. Click "Sign Up" on the main page
2. Enter your details (firstname, middlename, lastname, email, password)
3. Click "Request OTP"
4. Check your email for the OTP code
5. Enter the OTP in the verification modal
6. You'll be automatically logged in

### User Login
1. Enter your email and password
2. Click "Sign In"
3. You'll be redirected to the dashboard

### Password Reset
1. Click "Forgot Password" on the login page
2. Enter your email address
3. Click "Request OTP"
4. Check your email for the OTP code
5. Enter the OTP in the verification form
6. Enter your new password and confirm it
7. Click "Reset Password"

### Dashboard Features
- View your profile information
- Update your profile details
- Change your password
- Manage accounts (create, read, update, delete)

## API Endpoints

### Authentication
- `POST /request-otp` - Request OTP for registration
- `POST /verify-otp-and-register` - Verify OTP and complete registration
- `POST /login` - User login
- `POST /logout` - User logout
- `POST /forgot-password/request-otp` - Request OTP for password reset
- `POST /forgot-password/verify-otp` - Verify OTP for password reset
- `POST /forgot-password/reset` - Reset password

### User Management
- `GET /user/profile` - Get user profile
- `PUT /user/profile` - Update user profile
- `PUT /user/password` - Change password

### Account Management
- `GET /accounts` - Get all accounts for user
- `POST /accounts` - Create new account
- `PUT /accounts/:id` - Update account
- `DELETE /accounts/:id` - Delete account

## Deployment to Vercel

1. Push your code to GitHub
2. Sign up for a Vercel account
3. Import your GitHub repository
4. Configure environment variables in Vercel dashboard:
   - SUPABASE_URL
   - SUPABASE_KEY
   - JWT_SECRET
5. Deploy!

## Troubleshooting

### Common Issues

1. **Forgot Password 404 Error**
   - Ensure the backend server is running
   - Check that the endpoint `POST /forgot-password/reset` is accessible
   - Verify CORS configuration in `app.js`

2. **OTP Not Received**
   - Check your email configuration in `backend/utils/mailer.js`
   - Verify SMTP settings and credentials
   - Check spam/junk folder

3. **Database Connection Issues**
   - Verify Supabase credentials in `.env` file
   - Ensure Supabase project URL and API key are correct
   - Check network connectivity

### Testing Endpoints
You can test the endpoints using the provided test scripts:
```bash
cd backend
node test_endpoint.js          # Test forgot password endpoint
node test_forgot_password.js   # Test Supabase password reset
```

## Contributing
Feel free to fork this repository and submit pull requests.

## License
This project is licensed under the MIT License.