import logging
from flask import request, jsonify
from supabase_client import supabase
from config import Config
from utils.supabase_storage import upload_file_to_supabase, delete_file_from_supabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_account():
    """
    Create a new account.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        data = request.get_json()
        site = data.get('site')
        username = data.get('username')
        password = data.get('password')
        
        if not site or not username or not password:
            return jsonify({'success': False, 'message': 'Site, username, and password are required.'}), 400
        
        image_path = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'
        
        # Check if a file was uploaded
        if 'image' in request.files:
            file = request.files['image']
            if file:
                # Upload file to Supabase Storage
                try:
                    # Read file content
                    file_content = file.read()
                    file_name = f"accounts/{user_id}_{file.filename}"
                    
                    result = upload_file_to_supabase(file_content, file_name)
                    
                    if result['error']:
                        logger.error(f"Error uploading file to Supabase Storage: {result['error']}")
                        return jsonify({
                            'success': False,
                            'message': result['error'] or 'Failed to upload image to Supabase Storage. Please try again or contact support.'
                        }), 500
                    else:
                        image_path = result['public_url']
                
                except Exception as file_read_error:
                    logger.error(f"Error reading file for Supabase upload: {str(file_read_error)}")
                    image_path = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'
        
        # If no file was uploaded, use the default image path that was sent from frontend
        # This handles the case where req.body.image === 'images/default.png'
        
        # Log the image path for debugging
        logger.info(f"/accounts: Image path being stored: {image_path}")
        
        response = supabase.table('accounts').insert({
            'site': site,
            'username': username,
            'password': password,
            'image': image_path,
            'user_id': user_id
        }).execute()
        
        if response.error:
            logger.error(response.error)
            # If there was an error and we uploaded a file, try to delete it from Supabase
            if 'image' in request.files and image_path.startswith('http'):
                try:
                    file_name = f"accounts/{user_id}_{request.files['image'].filename}"
                    delete_file_from_supabase(file_name, 'images')
                except Exception as delete_err:
                    logger.error(f"Error deleting uploaded file: {str(delete_err)}")
            
            return jsonify({'success': False, 'message': 'Error creating account.'}), 500
        
        return jsonify({'success': True, 'message': 'Account created successfully!', 'accountId': response.data[0]['id']})
        
    except Exception as e:
        logger.error(f"Error in create_account: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def get_accounts():
    """
    Get all accounts for the user.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        logger.info(f"/accounts: Request received for user ID: {user_id}")
        
        response = supabase.table('accounts').select('id, site, username, password, image').eq('user_id', user_id).execute()
        
        if response.error:
            logger.error(f"/accounts: DB Error reading accounts: {response.error}")
            return jsonify({'success': False, 'message': 'Error reading accounts.'}), 500
        
        accounts = response.data
        
        # Log the raw accounts data for debugging
        logger.info(f"/accounts: Raw accounts data: {accounts}")
        
        # Process accounts to handle image paths correctly
        accounts_with_full_image_urls = []
        for account in accounts:
            # Ensure image field has a default value if null
            if not account.get('image'):
                account['image'] = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'
            
            # For Supabase Storage URLs, return as-is since they're already full URLs
            # For local images or default images, return relative path
            if (account['image'] and 
                not account['image'].startswith('http') and 
                account['image'] != 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'):
                account['image'] = account['image'].replace('\\', '/')
            
            accounts_with_full_image_urls.append(account)
        
        # Log the processed accounts data for debugging
        logger.info(f"/accounts: Processed accounts data: {accounts_with_full_image_urls}")
        
        logger.info(f"/accounts: Successfully retrieved accounts for user ID: {user_id}, Count: {len(accounts)}")
        return jsonify({
            'success': True, 
            'message': 'Accounts retrieved successfully!', 
            'accounts': accounts_with_full_image_urls
        })
        
    except Exception as e:
        logger.error(f"Error in get_accounts: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def update_account(account_id):
    """
    Update an account.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        data = request.get_json()
        site = data.get('site')
        username = data.get('username')
        password = data.get('password')
        
        if not site or not username or not password:
            return jsonify({'success': False, 'message': 'Site, username, and password are required.'}), 400
        
        # First, get the current account data to retrieve the existing image URL
        response = supabase.table('accounts').select('image').eq('id', account_id).eq('user_id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error fetching current account data.'}), 500
        
        current_account_data = response.data
        
        # Check if account exists
        if not current_account_data or len(current_account_data) == 0:
            return jsonify({'success': False, 'message': 'Account not found or you do not have permission to update it.'}), 404
        
        current_image = current_account_data[0].get('image')
        image_path = current_image or 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'
        
        # Check if a file was uploaded
        if 'image' in request.files:
            file = request.files['image']
            if file:
                # Upload new file to Supabase Storage
                try:
                    # Read file content
                    file_content = file.read()
                    file_name = f"accounts/{user_id}_{file.filename}"
                    
                    result = upload_file_to_supabase(file_content, file_name)
                    
                    if result['error']:
                        logger.error(f"Error uploading file to Supabase Storage: {result['error']}")
                        return jsonify({
                            'success': False,
                            'message': result['error'] or 'Failed to upload image to Supabase Storage. Please try again or contact support.'
                        }), 500
                    else:
                        image_path = result['public_url']
                        
                        # If there was a previous image stored in Supabase Storage, delete it
                        # But only if it's not the default account image
                        if (current_image and 
                            current_image.startswith('http') and 
                            'supabase.co/storage' in current_image and
                            current_image != 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'):
                            try:
                                # Extract the file path from the URL
                                url_parts = current_image.split('/')
                                # Find the index of 'object' in the URL parts
                                object_index = url_parts.index('object')
                                if object_index != -1 and object_index + 2 < len(url_parts):
                                    # Get everything after 'object/public/<bucket>/'
                                    old_file_path = '/'.join(url_parts[object_index + 3:])
                                    logger.info(f"Deleting old image file: {old_file_path}")
                                    delete_result = delete_file_from_supabase(old_file_path, 'images')
                                    
                                    if delete_result['error']:
                                        logger.error(f"Error deleting old image from Supabase Storage: {delete_result['error']}")
                                    else:
                                        logger.info("Old image deleted successfully from Supabase Storage")
                            except Exception as delete_err:
                                logger.error(f"Error deleting old image file: {str(delete_err)}")
                
                except Exception as file_read_error:
                    logger.error(f"Error reading file for Supabase upload: {str(file_read_error)}")
        elif data.get('image') == 'images/default.png' or data.get('image') == 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png':
            # If user explicitly selected default image, use it
            image_path = 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'
            
            # If there was a previous image stored in Supabase Storage, delete it
            # But only if it's not the default account image
            if (current_image and 
                current_image.startswith('http') and 
                'supabase.co/storage' in current_image and
                current_image != 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'):
                try:
                    # Extract the file path from the URL
                    url_parts = current_image.split('/')
                    # Find the index of 'object' in the URL parts
                    object_index = url_parts.index('object')
                    if object_index != -1 and object_index + 2 < len(url_parts):
                        # Get everything after 'object/public/<bucket>/'
                        old_file_path = '/'.join(url_parts[object_index + 3:])
                        logger.info(f"Deleting old image file: {old_file_path}")
                        delete_result = delete_file_from_supabase(old_file_path, 'images')
                        
                        if delete_result['error']:
                            logger.error(f"Error deleting old image from Supabase Storage: {delete_result['error']}")
                        else:
                            logger.info("Old image deleted successfully from Supabase Storage")
                except Exception as delete_err:
                    logger.error(f"Error deleting old image file: {str(delete_err)}")
        
        # Log the image path for debugging
        logger.info(f"/accounts/:id: Image path being updated: {image_path}")
        
        response = supabase.table('accounts').update({
            'site': site,
            'username': username,
            'password': password,
            'image': image_path
        }).eq('id', account_id).eq('user_id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error updating account.'}), 500
        
        # Check if no rows were affected (account not found or not owned by user)
        if response.data and len(response.data) == 0:
            # If we uploaded a new file but the update failed, try to delete the uploaded file
            if 'image' in request.files and image_path and image_path.startswith('http'):
                try:
                    file_name = f"accounts/{user_id}_{request.files['image'].filename}"
                    delete_file_from_supabase(file_name, 'images')
                except Exception as delete_err:
                    logger.error(f"Error deleting uploaded file: {str(delete_err)}")
            
            return jsonify({'success': False, 'message': 'Account not found or you do not have permission to update it.'}), 404
        
        return jsonify({'success': True, 'message': 'Account updated successfully!'})
        
    except Exception as e:
        logger.error(f"Error in update_account: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def delete_account(account_id):
    """
    Delete an account.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        # First, get the account to retrieve the image URL
        response = supabase.table('accounts').select('image').eq('id', account_id).eq('user_id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error fetching account for deletion.'}), 500
        
        account_data = response.data
        
        # Check if account exists
        if not account_data or len(account_data) == 0:
            return jsonify({'success': False, 'message': 'Account not found or you do not have permission to delete it.'}), 404
        
        account_image = account_data[0].get('image')
        
        # Delete the account
        response = supabase.table('accounts').delete().eq('id', account_id).eq('user_id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error deleting account.'}), 500
        
        # Check if no rows were affected (account not found or not owned by user)
        if response.data and len(response.data) == 0:
            return jsonify({'success': False, 'message': 'Account not found or you do not have permission to delete it.'}), 404
        
        # If the account had an image stored in Supabase Storage, delete it
        # But only if it's not the default account image
        if (account_image and 
            account_image.startswith('http') and 
            'supabase.co/storage' in account_image and
            account_image != 'https://nttadnyxpbuwuhgtpvjh.supabase.co/storage/v1/object/public/images/default.png'):
            try:
                # Extract the file path from the URL
                url_parts = account_image.split('/')
                # Find the index of 'object' in the URL parts
                object_index = url_parts.index('object')
                if object_index != -1 and object_index + 2 < len(url_parts):
                    # Get everything after 'object/public/<bucket>/'
                    file_path = '/'.join(url_parts[object_index + 3:])
                    
                    logger.info(f"Deleting image file: {file_path}")
                    delete_result = delete_file_from_supabase(file_path, 'images')
                    
                    if delete_result['error']:
                        logger.error(f"Error deleting image from Supabase Storage: {delete_result['error']}")
                    else:
                        logger.info("Image deleted successfully from Supabase Storage")
            except Exception as delete_err:
                logger.error(f"Error deleting image file: {str(delete_err)}")
        
        return jsonify({'success': True, 'message': 'Account deleted successfully!'})
        
    except Exception as e:
        logger.error(f"Error in delete_account: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500