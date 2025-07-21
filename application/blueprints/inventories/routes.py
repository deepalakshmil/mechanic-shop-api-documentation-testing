from flask import request,jsonify
from marshmallow import ValidationError
from .schemas import inventory_schema, inventories_schema
from sqlalchemy import select
from application.models import Inventory,db
from . import inventories_bp
from application.extensions import cache

###================= Flask API with CRUD Endpoints ============================= ###

#=================  Create Inventory (POST)   ====================#

@inventories_bp.route('/', methods=['POST'])
def create_inventory():

    try:
        inventory_data= inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify({"error" : e.messages}),400
    
    new_inventory= Inventory(**inventory_data)
 
    db.session.add(new_inventory)  
    db.session.commit()
    
    return jsonify({"Message": f"The {new_inventory.name} New Inventory details added successfully",
                    "Inventory": inventory_schema.dump(new_inventory)}), 201

#========== Retrieve all Inventories (GET) ===========================#

@inventories_bp.route("/", methods=['GET'])
@cache.cached(timeout=30) # Database data is refreshed in the cache based on a set timeout interval.
def get_inventories():

    query = select(Inventory)
    inventory = db.session.execute(query).scalars().all()

    return inventories_schema.jsonify(inventory)

#=========== Retrieve Specific Inventory (GET) ================== #

@inventories_bp.route("/<int:inventory_id>", methods=['GET'])
def get_inventory(inventory_id):

    inventory = db.session.get(Inventory, inventory_id)
    if inventory:
        return inventory_schema.jsonify(inventory), 200
    
    return jsonify({"error": "Inventory id is not found."}), 404

#============ Update Specific Inventory details (PUT) =============#

@inventories_bp.route("/<int:inventory_id>", methods=['PUT'])
def update_inventory(inventory_id):
    
    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({"error": "Inventory id is not found."}), 404
    
    try:
        inventory_data = inventory_schema.load(request.json)
    
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in inventory_data.items():
        setattr(inventory, key, value)

    db.session.commit()

    return jsonify({"Message": f'Successfully Updated Inventory id: {inventory_id}',
                    "Inventory": inventory_schema.dump(inventory)}), 200

#========== Delete Specific Inventory details (DELETE)=================#

@inventories_bp.route("/<int:inventory_id>", methods=['DELETE'])
def delete_inventory(inventory_id):

    inventory = db.session.get(Inventory, inventory_id)

    if not inventory:
        return jsonify({"error": "Inventory not found."}), 404
    
    db.session.delete(inventory)
    db.session.commit()
    
    return jsonify({"message": f'Inventory id: {inventory_id}, successfully deleted.'}), 200