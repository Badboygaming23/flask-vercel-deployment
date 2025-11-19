import logging
from flask import request, jsonify
from supabase_client import supabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_item():
    """
    Create a new item.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        
        if not name or not description:
            return jsonify({'success': False, 'message': 'Name and description are required.'}), 400
        
        response = supabase.table('items').insert({
            'name': name,
            'description': description,
            'user_id': user_id
        }).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error creating item.'}), 500
        
        return jsonify({
            'success': True, 
            'message': 'Item created successfully!', 
            'itemId': response.data[0]['id']
        })
        
    except Exception as e:
        logger.error(f"Error in create_item: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def read_items():
    """
    Read all items for the user.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        response = supabase.table('items').select('*').eq('user_id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error reading items.'}), 500
        
        return jsonify({
            'success': True, 
            'message': 'Items retrieved successfully!', 
            'items': response.data
        })
        
    except Exception as e:
        logger.error(f"Error in read_items: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def update_item():
    """
    Update an item.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        data = request.get_json()
        item_id = data.get('id')
        name = data.get('name')
        description = data.get('description')
        
        if not item_id or not name or not description:
            return jsonify({'success': False, 'message': 'Item ID, name, and description are required.'}), 400
        
        response = supabase.table('items').update({
            'name': name,
            'description': description
        }).eq('id', item_id).eq('user_id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error updating item.'}), 500
        
        if len(response.data) == 0:
            return jsonify({'success': False, 'message': 'Item not found or you do not have permission to update it.'}), 404
        
        return jsonify({'success': True, 'message': 'Item updated successfully!'})
        
    except Exception as e:
        logger.error(f"Error in update_item: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500

def delete_item():
    """
    Delete an item.
    """
    try:
        # Get user from request context (set by auth middleware)
        user = getattr(request, 'user', None)
        
        if not user:
            return jsonify({'success': False, 'message': 'User not authenticated.'}), 401
        
        user_id = user['id']
        
        data = request.get_json()
        item_id = data.get('id')
        
        if not item_id:
            return jsonify({'success': False, 'message': 'Item ID is required.'}), 400
        
        response = supabase.table('items').delete().eq('id', item_id).eq('user_id', user_id).execute()
        
        if response.error:
            logger.error(response.error)
            return jsonify({'success': False, 'message': 'Error deleting item.'}), 500
        
        if len(response.data) == 0:
            return jsonify({'success': False, 'message': 'Item not found or you do not have permission to delete it.'}), 404
        
        return jsonify({'success': True, 'message': 'Item deleted successfully!'})
        
    except Exception as e:
        logger.error(f"Error in delete_item: {str(e)}")
        return jsonify({'success': False, 'message': 'An unexpected error occurred.'}), 500