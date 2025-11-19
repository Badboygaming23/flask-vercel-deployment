from flask import Blueprint
from controllers.user_controller import (
    get_user_info,
    update_user_info,
    upload_profile_picture,
    get_profile_picture,
    verify_current_password,
    change_password
)
from middleware.auth import authenticate_token

# Create blueprint
user_bp = Blueprint('user', __name__)

# Define routes
@user_bp.route('/user-info', methods=['GET'])
@authenticate_token
def user_info_route():
    return get_user_info()

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@authenticate_token
def update_user_info_route(user_id):
    return update_user_info(user_id)

@user_bp.route('/upload-profile-picture', methods=['POST'])
@authenticate_token
def upload_profile_picture_route():
    return upload_profile_picture()

@user_bp.route('/profile-picture', methods=['GET'])
@authenticate_token
def profile_picture_route():
    return get_profile_picture()

@user_bp.route('/verify-current-password', methods=['POST'])
@authenticate_token
def verify_current_password_route():
    return verify_current_password()

@user_bp.route('/change-password', methods=['POST'])
@authenticate_token
def change_password_route():
    return change_password()