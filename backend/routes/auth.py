from flask import Blueprint, request, jsonify
from controllers.auth_controller import (
    request_otp, 
    request_password_reset_otp, 
    verify_otp_and_register, 
    verify_password_reset_otp, 
    reset_password, 
    login, 
    logout
)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Define routes
@auth_bp.route('/request-otp', methods=['POST'])
def request_otp_route():
    return request_otp()

@auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_password_reset_otp_route():
    return request_password_reset_otp()

@auth_bp.route('/verify-otp-and-register', methods=['POST'])
def verify_otp_and_register_route():
    return verify_otp_and_register()

@auth_bp.route('/forgot-password/verify-otp', methods=['POST'])
def verify_password_reset_otp_route():
    return verify_password_reset_otp()

@auth_bp.route('/forgot-password/reset', methods=['POST'])
def reset_password_route():
    return reset_password()

@auth_bp.route('/login', methods=['POST'])
def login_route():
    return login()

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    return logout()