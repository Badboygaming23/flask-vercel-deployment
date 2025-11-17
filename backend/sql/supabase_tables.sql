-- Supabase Table Creation Scripts

-- Users table
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  firstname VARCHAR(255),
  middlename VARCHAR(255),
  lastname VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password VARCHAR(255),
  profilePicture VARCHAR(255) DEFAULT 'images/default-profile.png',
  token TEXT
);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
  id SERIAL PRIMARY KEY,
  site VARCHAR(255) NOT NULL,
  username VARCHAR(255) NOT NULL,
  password VARCHAR(255) NOT NULL,
  image VARCHAR(255),
  user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- OTPs table
CREATE TABLE IF NOT EXISTS otps (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  otp_code VARCHAR(6) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL
);