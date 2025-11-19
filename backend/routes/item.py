from flask import Blueprint
from controllers.item_controller import (
    create_item,
    read_items,
    update_item,
    delete_item
)
from middleware.auth import authenticate_token

# Create blueprint
item_bp = Blueprint('item', __name__)

# Define routes
@item_bp.route('/create', methods=['POST'])
@authenticate_token
def create_item_route():
    return create_item()

@item_bp.route('/read', methods=['GET'])
@authenticate_token
def read_items_route():
    return read_items()

@item_bp.route('/update', methods=['PUT'])
@authenticate_token
def update_item_route():
    return update_item()

@item_bp.route('/delete', methods=['DELETE'])
@authenticate_token
def delete_item_route():
    return delete_item()