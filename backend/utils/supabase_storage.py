import logging
from supabase_client import supabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_file_to_supabase(file_buffer, file_name, bucket_name='images'):
    """
    Upload a file to Supabase Storage.
    
    Args:
        file_buffer: The file buffer or file object
        file_name: The name to save the file as
        bucket_name: The storage bucket name (default: 'images')
    
    Returns:
        dict: {'public_url': str, 'error': str or None}
    """
    try:
        logger.info(f"Uploading file to Supabase Storage: {file_name} in bucket: {bucket_name}")
        
        # Upload the file to Supabase Storage
        response = supabase.storage.from_(bucket_name).upload(
            file=file_buffer,
            path=file_name,
            file_options={"content-type": "image/*"}
        )
        
        if response.status_code != 200:
            error_msg = f"Error uploading file to Supabase Storage: {response.json()}"
            logger.error(error_msg)
            return {'public_url': None, 'error': error_msg}
        
        logger.info("File uploaded successfully")
        
        # Get the public URL for the uploaded file
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        logger.info(f"Public URL generated: {public_url}")
        
        return {'public_url': public_url, 'error': None}
        
    except Exception as err:
        error_msg = f"Unexpected error uploading file to Supabase Storage: {str(err)}"
        logger.error(error_msg)
        return {'public_url': None, 'error': error_msg}

def delete_file_from_supabase(file_name, bucket_name='images'):
    """
    Delete a file from Supabase Storage.
    
    Args:
        file_name: The name of the file to delete
        bucket_name: The storage bucket name (default: 'images')
    
    Returns:
        dict: {'error': str or None}
    """
    try:
        logger.info(f"Deleting file from Supabase Storage: {file_name} in bucket: {bucket_name}")
        
        # Delete the file from Supabase Storage
        response = supabase.storage.from_(bucket_name).remove([file_name])
        
        if response.status_code != 200:
            error_msg = f"Error deleting file from Supabase Storage: {response.json()}"
            logger.error(error_msg)
            return {'error': error_msg}
        
        logger.info("File deleted successfully")
        return {'error': None}
        
    except Exception as err:
        error_msg = f"Unexpected error deleting file from Supabase Storage: {str(err)}"
        logger.error(error_msg)
        return {'error': error_msg}

def get_public_url_from_supabase(file_name, bucket_name='images'):
    """
    Get the public URL for a file in Supabase Storage.
    
    Args:
        file_name: The name of the file
        bucket_name: The storage bucket name (default: 'images')
    
    Returns:
        str: The public URL of the file
    """
    try:
        logger.info(f"Getting public URL for file: {file_name} in bucket: {bucket_name}")
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_name)
        logger.info(f"Public URL retrieved: {public_url}")
        return public_url
    except Exception as err:
        logger.error(f"Error getting public URL from Supabase Storage: {str(err)}")
        return None