from flask import request,jsonify
from marshmallow import ValidationError
from .schemas import mechanic_schema,mechanics_schema
from sqlalchemy import select
from application.models import Mechanics,db
from . import mechanics_bp
from application.extensions import cache

###================= Flask API with CRUD Endpoints ============================= ###

#=================  Create User (POST)   ====================#

@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():

    try:
        mechanic_data= mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    query = select(Mechanics).where(Mechanics.email == mechanic_data['email']) #Checking our db for a Mechanic with this email
    existing_mechanic = db.session.execute(query).scalars().all() 

    if existing_mechanic:
        return jsonify({"error" : "Email already associated with an account."}),400

    new_mechanic= Mechanics(**mechanic_data)
 
    db.session.add(new_mechanic)  
    db.session.commit()
    
    return jsonify({"Message": "New Mechanic details added successfully",
                    "Mechanic": mechanic_schema.dump(new_mechanic)}), 201

#========== Retrieve Mechanics (GET) ===========================#

@mechanics_bp.route("/", methods=['GET'])
@cache.cached(timeout=30)
def get_mechanics():

    query = select(Mechanics)
    mechanic = db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanic)

#=========== Retrieve Specific Mechanic (GET) ================== #

@mechanics_bp.route("/<int:mechanic_id>", methods=['GET'])
def get_mechanic(mechanic_id):

    mechanic = db.session.get(Mechanics, mechanic_id)
    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    
    return jsonify({"error": "Mechanic id is not found."}), 404

#============ Update Specific Mechanic details (PUT) =============#

@mechanics_bp.route("/<int:mechanic_id>", methods=['PUT'])
def update_mechanic(mechanic_id):
    
    mechanic = db.session.get(Mechanics, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic id is not found."}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()

    return jsonify({"Message": f'Successfully Updated Mechanic id: {mechanic_id}',
                    "mechanic": mechanic_schema.dump(mechanic)}), 200

#========== Delete Specific Mechanics details (DELETE)=================#

@mechanics_bp.route("/<int:mechanic_id>", methods=['DELETE'])
def delete_mechanic(mechanic_id):

    mechanic = db.session.get(Mechanics, mechanic_id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found."}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    
    return jsonify({"message": f'mechanic id: {mechanic_id}, successfully deleted.'}), 200

#================== Retrieve a list of popular mechanics (GET)  ===============#

# A display a list of mechanics in order of who has worked on the most tickets using sort() and lambda function

@mechanics_bp.route("/popular-mechanic", methods=['GET'])
def popular_mechanics():
    query = select(Mechanics)
    mechanics = db.session.execute(query).scalars().all()

    mechanics.sort(key = lambda mechanic :len(mechanic.services),reverse=True)

    # for mechanic in mechanics:
    #     print(mechanic.name , len(mechanic.services))

    return jsonify({"Message" : "Successfully Retrieve a list mechanics in order of who has worked on the most tikets",
                                     "Most popular Mechanics List Order by:" : mechanics_schema.dump(mechanics)}),200

#================== Retrieve a list of mechanic name(use search passing parameter with  name) (GET)  ===============#


@mechanics_bp.route("/search", methods=['GET'])
def serch_mechanics():
    
    name = request.args.get("name")
    print(name)
    # query = select(Mechanics).where(Mechanics.name.like(name))
    query = select(Mechanics).where(Mechanics.name.like(f'%{name}%')) # retrieve list of name based on passing parameter name
    mechanics=db.session.execute(query).scalars().all()

    return mechanics_schema.jsonify(mechanics)
