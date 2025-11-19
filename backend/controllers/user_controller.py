import bcrypt
import jwt
import os
import logging
from flask import request, jsonify, current_app
from supabase_client import supabase
from config import Config
from utils.supabase_storage import upload_file_to_supabase, delete_file_from_supabase
from middleware.auth import authenticate_token

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_info():
    """
    Get user information.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        logger.info(f"getUserInfo: Fetching user info for user ID: {user_id}")
        
        response = supabase.table('users').select('id, firstname, middlename, lastname, email, profilepicture').eq('id', user_id).execute()
        
        if response.error:
            logger.error(f"Error in getUserInfo - Supabase query failed: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred while fetching user information.'}), 500
        
        users = response.data
        
        if users and len(users) > 0:
            user_data = users[0]
            logger.info(f"getUserInfo: User found: {user_data['email']}")
            
            # Ensure profilePicture has a default value if null
            if not user_data.get('profilepicture'):
                user_data['profilepicture'] = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png'
            
            # For Supabase Storage URLs, return as-is since they're already full URLs
            # For local images, return relative path
            if user_data.get('profilepicture') and not user_data['profilepicture'].startswith('http'):
                user_data['profilepicture'] = user_data['profilepicture'].replace('\\', '/')
            
            logger.info(f"getUserInfo: Returning user data with profile picture: {user_data['profilepicture']}")
            return jsonify({'success': True, 'user': user_data})
        else:
            logger.info(f"getUserInfo: User not found for ID: {user_id}")
            return jsonify({'success': False, 'message': 'User not found.'}), 404
            
    except Exception as e:
        logger.error(f"Error in getUserInfo - Unexpected error: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred while fetching user information.'}), 500

def update_user_info(user_id):
    """
    Update user information.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        # Check if user is authorized to update this user
        if user['id'] != user_id:
            return jsonify({'success': False, 'message': 'Unauthorized to update this user.'}), 403
        
        data = request.get_json()
        firstname = data.get('firstname')
        middlename = data.get('middlename')
        lastname = data.get('lastname')
        email = data.get('email')
        
        if not firstname or not lastname or not email:
            return jsonify({'success': False, 'message': 'First name, last name, and email are required.'}), 400
        
        response = supabase.table('users').update({
            'firstname': firstname,
            'middlename': middlename,
            'lastname': lastname,
            'email': email
        }).eq('id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error updating user information.'}), 500
        
        return jsonify({'success': True, 'message': 'Account information updated successfully!'})
        
    except Exception as e:
        logger.error(f"Error in update_user_info: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def upload_profile_picture():
    """
    Upload profile picture.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        # Check if a file was uploaded
        if 'profilePicture' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded.'}), 400
        
        file = request.files['profilePicture']
        
        # First, get the current user data to retrieve the existing profile picture URL
        response = supabase.table('users').select('profilepicture').eq('id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error fetching current user data.'}), 500
        
        current_user_data = response.data
        
        # Check if user exists
        if not current_user_data or len(current_user_data) == 0:
            return jsonify({'success': False, 'message': 'User not found.'}), 404
        
        current_profile_picture = current_user_data[0].get('profilepicture')
        profile_picture_path = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png'
        
        # Upload file to Supabase Storage
        if file:
            try:
                # Read file content
                file_content = file.read()
                file_name = f"profile-pictures/{user_id}_{file.filename}"
                
                result = upload_file_to_supabase(file_content, file_name, 'images')
                
                if result['error']:
                    logger.error(f"Error uploading profile picture to Supabase Storage: {result['error']}")
                    return jsonify({
                        'success': False,
                        'message': result['error'] or 'Failed to upload profile picture to Supabase Storage. Please try again or contact support.'
                    }), 500
                else:
                    profile_picture_path = result['public_url']
                    
                    # If there was a previous profile picture stored in Supabase Storage, delete it
                    # But only if it's not the default profile picture
                    if (current_profile_picture and 
                        current_profile_picture.startswith('http') and 
                        'supabase.co/storage' in current_profile_picture and
                        current_profile_picture != 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png'):
                        try:
                            # Extract the file path from the URL
                            url_parts = current_profile_picture.split('/')
                            # Find the index of 'object' in the URL parts
                            object_index = url_parts.index('object')
                            if object_index != -1 and object_index + 2 < len(url_parts):
                                # Get everything after 'object/public/<bucket>/'
                                old_file_path = '/'.join(url_parts[object_index + 3:])
                                logger.info(f"Deleting old profile picture file: {old_file_path}")
                                delete_result = delete_file_from_supabase(old_file_path, 'images')
                                
                                if delete_result['error']:
                                    logger.error(f"Error deleting old profile picture from Supabase Storage: {delete_result['error']}")
                                else:
                                    logger.info("Old profile picture deleted successfully from Supabase Storage")
                        except Exception as delete_err:
                            logger.error(f"Error deleting old profile picture file: {str(delete_err)}")
            
            except Exception as file_read_error:
                logger.error(f"Error reading file for Supabase upload: {str(file_read_error)}")
                profile_picture_path = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png'
        
        response = supabase.table('users').update({'profilepicture': profile_picture_path}).eq('id', user_id).execute()
        
        if response.error:
            logger.error(f"Error updating profile picture in DB: {response.error}")
            # If there was an error, try to delete the uploaded file from Supabase
            # But only if it's not the default profile picture
            if (profile_picture_path.startswith('http') and 
                profile_picture_path != 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png'):
                try:
                    url_parts = profile_picture_path.split('/')
                    file_name = url_parts[-1]
                    file_path = f"profile-pictures/{file_name}"
                    delete_file_from_supabase(file_path, 'images')
                except Exception as delete_err:
                    logger.error(f"Error deleting uploaded file: {str(delete_err)}")
            
            return jsonify({'success': False, 'message': 'Error saving profile picture.'}), 500
        
        return jsonify({
            'success': True, 
            'message': 'Profile picture updated successfully!', 
            'profilepicture': profile_picture_path
        })
        
    except Exception as e:
        logger.error(f"Error in upload_profile_picture: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def get_profile_picture():
    """
    Get profile picture.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        logger.info(f"getProfilePicture: Fetching profile picture for user ID: {user_id}")
        
        response = supabase.table('users').select('profilepicture').eq('id', user_id).execute()
        
        if response.error:
            logger.error(f"Error in getProfilePicture - Supabase query failed: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred while fetching profile picture.'}), 500
        
        users = response.data
        
        if users and len(users) > 0:
            profile_picture = users[0].get('profilepicture')
            logger.info(f"getProfilePicture: Profile picture from DB: {profile_picture}")
            
            # Ensure profilePicture has a default value if null
            if not profile_picture:
                profile_picture = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default-profile.png'
            
            # For Supabase Storage URLs, return as-is since they're already full URLs
            # For local images, return relative path
            if profile_picture and not profile_picture.startswith('http'):
                # Ensure the path is properly formatted
                profile_picture = profile_picture.replace('\\', '/')
            
            logger.info(f"getProfilePicture: Returning profile picture: {profile_picture}")
            return jsonify({'success': True, 'profilepicture': profile_picture})
        else:
            logger.info(f"getProfilePicture: User not found for ID: {user_id}")
            return jsonify({'success': False, 'message': 'User not found.'}), 404
            
    except Exception as e:
        logger.error(f"Error in getProfilePicture - Unexpected error: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred while fetching profile picture.'}), 500

def verify_current_password():
    """
    Verify current password.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        data = request.get_json()
        current_password = data.get('currentPassword')
        
        if not current_password:
            return jsonify({'success': False, 'message': 'Current password is required.'}), 400
        
        response = supabase.table('users').select('password').eq('id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'An error occurred.'}), 500
        
        users = response.data
        
        if len(users) == 0:
            return jsonify({'success': False, 'message': 'User not found.'}), 404
        
        hashed_password = users[0]['password']
        
        if bcrypt.checkpw(current_password.encode('utf-8'), hashed_password.encode('utf-8')):
            return jsonify({'success': True, 'message': 'Current password matches.'})
        else:
            return jsonify({'success': False, 'message': 'Current password does not match.'}), 401
            
    except Exception as e:
        logger.error(f"Error in verify_current_password: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def change_password():
    """
    Change user password.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        user_email = user['email']
        
        logger.info(f"/change-password: Request received for user ID: {user_id}, Email: {user_email}")
        
        data = request.get_json()
        current_password = data.get('currentPassword')
        new_password = data.get('newPassword')
        confirm_new_password = data.get('confirmNewPassword')
        
        if not current_password or not new_password or not confirm_new_password:
            return jsonify({'success': False, 'message': 'All password fields are required.'}), 400
        
        if new_password != confirm_new_password:
            return jsonify({'success': False, 'message': 'New password and confirm password do not match.'}), 400
        
        response = supabase.table('users').select('password').eq('id', user_id).execute()
        
        if response.error:
            logger.error(f"/change-password: Error verifying current password from DB: {response.error}")
            return jsonify({'success': False, 'message': 'An error occurred while verifying current password.'}), 500
        
        users = response.data
        
        if len(users) == 0:
            logger.info(f"/change-password: User not found for ID: {user_id}")
            return jsonify({'success': False, 'message': 'User not found.'}), 404
        
        hashed_password = users[0]['password']
        
        if not bcrypt.checkpw(current_password.encode('utf-8'), hashed_password.encode('utf-8')):
            logger.info(f"/change-password: Invalid current password for user ID: {user_id}")
            return jsonify({'success': False, 'message': 'Invalid current password.'}), 401
        
        # Hash new password
        new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        update_response = supabase.table('users').update({'password': new_hashed_password}).eq('id', user_id).execute()
        
        if update_response.error:
            logger.error(f"/change-password: Error updating password in DB: {update_response.error}")
            return jsonify({'success': False, 'message': 'An error occurred while changing password.'}), 500
        
        logger.info(f"/change-password: Password updated in DB for user ID: {user_id}")
        
        # Generate new JWT token
        token_payload = {
            'id': user_id,
            'email': user_email
        }
        
        new_access_token = jwt.encode(token_payload, Config.JWT_SECRET, algorithm='HS256')
        logger.info(f"/change-password: Generated new token: {new_access_token[:10]}...")
        
        token_update_response = supabase.table('users').update({'token': new_access_token}).eq('id', user_id).execute()
        
        if token_update_response.error:
            logger.error(f"/change-password: Error updating token after password change: {token_update_response.error}")
            return jsonify({'success': False, 'message': 'An error occurred while updating session.'}), 500
        
        logger.info(f"/change-password: Token updated in DB for user ID: {user_id}")
        return jsonify({'success': True, 'message': 'Password changed successfully!', 'token': new_access_token})
        
    except Exception as e:
        logger.error(f"Error in change_password: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500