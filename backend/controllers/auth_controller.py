import bcrypt
import jwt
import os
import random
import datetime
import logging
from flask import request, jsonify, current_app
from supabase_client import supabase
from config import Config
from utils.mailer import send_otp_email, send_password_reset_email

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def request_otp():
    """
    Request OTP for user registration.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        logger.info(f"OTP request for email: {email}")
        
        if not email:
            logger.info("Email is required")
            return jsonify({'success': False, 'message': 'Email is required.'}), 400
        
        # Check if user already exists
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if response.error:
            logger.error(f"Database error during email check: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred during email check.'}), 500
        
        users = response.data
        logger.info(f"Existing users with email: {len(users)}")
        
        if len(users) > 0:
            logger.info(f"Email already in use: {email}")
            return jsonify({'success': False, 'message': 'Email already in use. Please try logging in.'}), 409
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
        
        logger.info(f"Generated OTP: {otp}, Expires at: {expires_at}")
        
        # Insert or update OTP
        response = supabase.table('otps').upsert({
            'email': email,
            'otp_code': otp,
            'expires_at': expires_at.isoformat()
        }).execute()
        
        if response.error:
            logger.error(f"Error storing OTP in DB: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred while storing OTP.'}), 500
        
        logger.info("OTP stored successfully")
        
        # Send OTP email
        if send_otp_email(email, otp):
            logger.info(f"OTP email sent successfully to: {email}")
            return jsonify({'success': True, 'message': f'OTP sent successfully to {email}'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send OTP. Mailer Error.'}), 500
            
    except Exception as e:
        logger.error(f"Error in request_otp: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def request_password_reset_otp():
    """
    Request OTP for password reset.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email is required.'}), 400
        
        # Check if user exists
        response = supabase.table('users').select('id').eq('email', email).execute()
        
        if response.error:
            logger.error(f"Database error during user check for forgot password: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred.'}), 500
        
        users = response.data
        
        if len(users) == 0:
            return jsonify({'success': False, 'message': 'Email not found.'}), 404
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
        
        # Insert or update OTP
        response = supabase.table('otps').upsert({
            'email': email,
            'otp_code': otp,
            'expires_at': expires_at.isoformat()
        }).execute()
        
        if response.error:
            logger.error(f"Error storing OTP for forgot password in DB: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred while storing OTP.'}), 500
        
        # Send password reset email
        if send_password_reset_email(email, otp):
            return jsonify({'success': True, 'message': f'Password reset OTP sent successfully to {email}'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send password reset OTP. Mailer Error.'}), 500
            
    except Exception as e:
        logger.error(f"Error in request_password_reset_otp: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def verify_otp_and_register():
    """
    Verify OTP and register user.
    """
    try:
        data = request.get_json()
        firstname = data.get('firstname')
        middlename = data.get('middlename')
        lastname = data.get('lastname')
        email = data.get('email')
        password = data.get('password')
        otp = data.get('otp')
        
        logger.info(f"Registration attempt for email: {email}")
        logger.info(f"Registration data: {{firstname: {firstname}, middlename: {middlename}, lastname: {lastname}, email: {email}, password: ***, otp: ***}}")
        
        if not firstname or not lastname or not email or not password or not otp:
            logger.info("Missing required fields")
            return jsonify({'success': False, 'message': 'All fields including OTP are required.'}), 400
        
        # Get OTP from database
        response = supabase.table('otps').select('otp_code, expires_at').eq('email', email).execute()
        
        if response.error:
            logger.error(f"Error retrieving OTP from DB: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred during OTP verification.'}), 500
        
        otps = response.data
        logger.info(f"OTPs found: {len(otps)}")
        
        if len(otps) == 0:
            logger.info(f"No OTP found for email: {email}")
            return jsonify({'success': False, 'message': 'Invalid or expired OTP.'}), 400
        
        stored_otp = otps[0]
        current_time = datetime.datetime.now()
        expires_at = datetime.datetime.fromisoformat(stored_otp['expires_at'])
        
        logger.info(f"Stored OTP: {stored_otp['otp_code']}, Provided OTP: {otp}")
        logger.info(f"Current time: {current_time}, Expires at: {expires_at}")
        
        if stored_otp['otp_code'] != otp:
            logger.info("OTP mismatch")
            return jsonify({'success': False, 'message': 'Invalid OTP. Please try again.'}), 400
        
        if current_time > expires_at:
            logger.info("OTP expired")
            # Delete expired OTP
            delete_response = supabase.table('otps').delete().eq('email', email).execute()
            
            if delete_response.error:
                logger.error(f"Error deleting expired OTP: {delete_response.error}")
            
            return jsonify({'success': False, 'message': 'OTP has expired. Please request a new one.'}), 400
        
        # Check if email already exists
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if response.error:
            logger.error(f"Error checking existing user: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred.'}), 500
        
        existing_users = response.data
        logger.info(f"Existing users with email: {len(existing_users)}")
        
        if len(existing_users) > 0:
            logger.info(f"Email already in use: {email}")
            return jsonify({'success': False, 'message': 'Email already in use.'}), 409
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        logger.info("Password hashed successfully")
        
        # Insert user
        response = supabase.table('users').insert({
            'firstname': firstname,
            'middlename': middlename,
            'lastname': lastname,
            'email': email,
            'password': hashed_password,
            'profilepicture': 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png'
        }).execute()
        
        if response.error:
            logger.error(f"Error inserting user: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred.'}), 500
        
        new_user = response.data
        logger.info(f"User inserted successfully: {new_user}")
        
        # Delete OTP after successful registration
        delete_response = supabase.table('otps').delete().eq('email', email).execute()
        
        if delete_response.error:
            logger.error(f"Error deleting OTP after successful registration: {delete_response.error}")
        
        # Generate JWT token
        token_payload = {
            'id': new_user[0]['id'],
            'email': email
        }
        
        access_token = jwt.encode(token_payload, Config.JWT_SECRET, algorithm='HS256')
        return jsonify({'success': True, 'message': 'Registration successful!', 'token': access_token})
        
    except Exception as e:
        logger.error(f"Error in verify_otp_and_register: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def verify_password_reset_otp():
    """
    Verify OTP for password reset.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({'success': False, 'message': 'Email and OTP are required.'}), 400
        
        # Get OTP from database
        response = supabase.table('otps').select('otp_code, expires_at').eq('email', email).execute()
        
        if response.error:
            logger.error(f"Error retrieving OTP for password reset from DB: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred during OTP verification.'}), 500
        
        otps = response.data
        
        if len(otps) == 0:
            return jsonify({'success': False, 'message': 'Invalid or expired OTP.'}), 400
        
        stored_otp = otps[0]
        current_time = datetime.datetime.now()
        expires_at = datetime.datetime.fromisoformat(stored_otp['expires_at'])
        
        if stored_otp['otp_code'] != otp or current_time > expires_at:
            return jsonify({'success': False, 'message': 'Invalid or expired OTP.'}), 400
        
        # Delete OTP after successful verification
        delete_response = supabase.table('otps').delete().eq('email', email).execute()
        
        if delete_response.error:
            logger.error(f"Error deleting OTP after successful verification: {delete_response.error}")
        
        return jsonify({'success': True, 'message': 'OTP verified successfully. You can now reset your password.'})
        
    except Exception as e:
        logger.error(f"Error in verify_password_reset_otp: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def reset_password():
    """
    Reset user password.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        new_password = data.get('newPassword')
        confirm_new_password = data.get('confirmNewPassword')
        
        logger.info(f"resetPassword called with body: {data}")
        
        if not email or not new_password or not confirm_new_password:
            logger.info("Missing required fields")
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400
        
        if new_password != confirm_new_password:
            logger.info("Passwords do not match")
            return jsonify({'success': False, 'message': 'New password and confirm password do not match.'}), 400
        
        # Hash new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        logger.info("Password hashed successfully")
        
        # Update password
        response = supabase.table('users').update({'password': hashed_password}).eq('email', email).execute()
        
        if response.error:
            logger.error(f"Error updating password: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred while resetting password.'}), 500
        
        logger.info("Password updated successfully")
        
        # Clear token
        clear_token_response = supabase.table('users').update({'token': None}).eq('email', email).execute()
        
        if clear_token_response.error:
            logger.error(f"Error clearing token after password reset: {clear_token_response.error}")
        
        return jsonify({'success': True, 'message': 'Password has been reset successfully! Please log in with your new password.'})
        
    except Exception as e:
        logger.error(f"Error in reset_password: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def login():
    """
    User login.
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        logger.info(f"Login attempt for email: {email}")
        
        # Get user
        response = supabase.table('users').select('*').eq('email', email).execute()
        
        if response.error:
            logger.error(f"Database error during login: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred.'}), 500
        
        users = response.data
        logger.info(f"Users found: {len(users)}")
        
        if len(users) > 0:
            user = users[0]
            logger.info(f"User found: {user['email']}")
            
            # Check password
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                # Generate JWT token
                token_payload = {
                    'id': user['id'],
                    'email': user['email']
                }
                
                access_token = jwt.encode(token_payload, Config.JWT_SECRET, algorithm='HS256')
                
                # Update token in database
                update_response = supabase.table('users').update({'token': access_token}).eq('id', user['id']).execute()
                
                if update_response.error:
                    logger.error(f"Error storing token in DB: {update_response.error}")
                    return jsonify({'success': False, 'message': 'An error occurred during login.'}), 500
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful!',
                    'token': access_token
                })
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials!'}), 401
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials!'}), 401
            
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def logout():
    """
    User logout.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        # Clear token
        response = supabase.table('users').update({'token': None}).eq('id', user_id).execute()
        
        if response.error:
            logger.error(f"Error clearing token from DB on logout: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred during logout.'}), 500
        
        return jsonify({'success': True, 'message': 'Logout successful!'})
        
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500