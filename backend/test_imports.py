"""
Test script to verify that all modules can be imported without errors.
This helps catch syntax errors and import issues early.
"""

def test_imports():
    try:
        print("Testing imports...")
        
        # Test config import
        from config import Config
        print("✓ config imported successfully")
        
        # Test supabase client import
        from supabase_client import get_supabase_client
        print("✓ supabase_client imported successfully")
        
        # Test middleware import
        from middleware.auth import authenticate_token
        print("✓ middleware.auth imported successfully")
        
        # Test utils imports
        from utils.mailer import send_otp_email, send_password_reset_email
        print("✓ utils.mailer imported successfully")
        
        from utils.supabase_storage import upload_file_to_supabase, delete_file_from_supabase
        print("✓ utils.supabase_storage imported successfully")
        
        # Test controllers imports
        from controllers.auth_controller import request_otp
        print("✓ controllers.auth_controller imported successfully")
        
        from controllers.user_controller import get_user_info
        print("✓ controllers.user_controller imported successfully")
        
        from controllers.account_controller import create_account
        print("✓ controllers.account_controller imported successfully")
        
        from controllers.item_controller import create_item
        print("✓ controllers.item_controller imported successfully")
        
        # Test routes imports
        from routes.auth import auth_bp
        print("✓ routes.auth imported successfully")
        
        from routes.user import user_bp
        print("✓ routes.user imported successfully")
        
        from routes.account import account_bp
        print("✓ routes.account imported successfully")
        
        from routes.item import item_bp
        print("✓ routes.item imported successfully")
        
        print("\nAll imports successful! The Flask application should run without import errors.")
        return True
        
    except Exception as e:
        print(f"Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports()