"""
Script to verify that all Express.js components have been converted to Flask.
"""

import os

def check_express_files_converted():
    """Check that all Express.js files have Flask equivalents."""
    print("Verifying Express.js to Flask conversion...")
    
    # List of original Express.js files and their Flask equivalents
    conversion_map = {
        'app.js': 'flask_app.py',
        'config/config.js': 'config.py',
        'config/supabase.js': 'config.py',
        'controllers/authController.js': 'controllers/auth_controller.py',
        'controllers/userController.js': 'controllers/user_controller.py',
        'controllers/accountController.js': 'controllers/account_controller.py',
        'controllers/itemController.js': 'controllers/item_controller.py',
        'middleware/auth.js': 'middleware/auth.py',
        'routes/authRoutes.js': 'routes/auth.py',
        'routes/userRoutes.js': 'routes/user.py',
        'routes/accountRoutes.js': 'routes/account.py',
        'routes/itemRoutes.js': 'routes/item.py',
        'utils/mailer.js': 'utils/mailer.py',
        'utils/supabaseStorage.js': 'utils/supabase_storage.py',
        'supabaseClient.js': 'supabase_client.py',
        'db.js': 'supabase_client.py'
    }
    
    base_path = '.'
    missing_conversions = []
    
    for express_file, flask_file in conversion_map.items():
        express_path = os.path.join(base_path, express_file)
        flask_path = os.path.join(base_path, flask_file)
        
        # Check if Express.js file exists
        if os.path.exists(express_path):
            # Check if Flask equivalent exists
            if not os.path.exists(flask_path):
                missing_conversions.append((express_file, flask_file))
                print(f"❌ Missing Flask equivalent for {express_file} -> {flask_file}")
            else:
                print(f"✓ Converted {express_file} -> {flask_file}")
        else:
            print(f"ℹ️  Express.js file {express_file} not found (may have been already converted)")
    
    if missing_conversions:
        print(f"\n⚠️  {len(missing_conversions)} conversions missing:")
        for express_file, flask_file in missing_conversions:
            print(f"  - {express_file} -> {flask_file}")
        return False
    else:
        print("\n✅ All Express.js components have been converted to Flask!")
        return True

def check_required_flask_files():
    """Check that all required Flask files exist."""
    print("\nChecking required Flask files...")
    
    required_files = [
        'flask_app.py',
        'config.py',
        'supabase_client.py',
        'requirements.txt',
        'controllers/auth_controller.py',
        'controllers/user_controller.py',
        'controllers/account_controller.py',
        'controllers/item_controller.py',
        'routes/auth.py',
        'routes/user.py',
        'routes/account.py',
        'routes/item.py',
        'middleware/auth.py',
        'utils/mailer.py',
        'utils/supabase_storage.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
            print(f"❌ Missing required file: {file_path}")
        else:
            print(f"✓ Found required file: {file_path}")
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} required files missing:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    else:
        print("\n✅ All required Flask files are present!")
        return True

if __name__ == "__main__":
    print("Flask Conversion Verification")
    print("=" * 30)
    
    conversion_ok = check_express_files_converted()
    files_ok = check_required_flask_files()
    
    print("\n" + "=" * 30)
    if conversion_ok and files_ok:
        print("🎉 CONVERSION COMPLETE: All Express.js components have been successfully converted to Flask!")
        print("\nTo run the Flask application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment variables in .env")
        print("3. Run: python flask_app.py")
    else:
        print("❌ CONVERSION INCOMPLETE: Some components are missing.")