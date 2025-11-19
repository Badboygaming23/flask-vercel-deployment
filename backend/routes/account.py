from flask import Blueprint
from controllers.account_controller import (
    create_account,
    get_accounts,
    update_account,
    delete_account
)
from middleware.auth import authenticate_token

# Create blueprint
account_bp = Blueprint('account', __name__)

# Define routes
@account_bp.route('/accounts', methods=['POST'])
@authenticate_token
def create_account_route():
    return create_account()

@account_bp.route('/accounts', methods=['GET'])
@authenticate_token
def get_accounts_route():
    return get_accounts()

@account_bp.route('/accounts/<int:account_id>', methods=['PUT'])
@authenticate_token
def update_account_route(account_id):
    return update_account(account_id)

@account_bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@authenticate_token
def delete_account_route(account_id):
    return delete_account(account_id)