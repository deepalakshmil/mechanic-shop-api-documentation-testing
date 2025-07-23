from flask import request,jsonify
from marshmallow import ValidationError
from .schemas import service_ticket_schema,service_tickets_schema,return_service_schema,edit_service_schema,service_ticket_create_schema
from sqlalchemy import select
from application.models import Customer,Service_tickets,Mechanics,db,ServiceInventory,Inventory
from . import serviceTickets_bp
from application.extensions import limiter
from application.utils.util import token_required

###================= Flask API with CRUD Endpoints ============================= ###

#=================  Create Service Ticket with mechanics (POST)   ====================#

@serviceTickets_bp.route('/with-mechanics', methods=['POST'])
def create_service_ticket_mechanics():

    try: #load & validate via the create‐only schema
        service_data= service_ticket_create_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    #pull mechanic_ids out so you don't pass them into the model ctor
    mechanic_ids = service_data.pop('mechanic_ids', [])

    # Retrieve the customer by its id.
    customer = db.session.get(Customer, service_data['customer_id'])
   
    # Check if the customer exists
    if customer:
        # Always add the service to the session BEFORE appending relationships
        new_service= Service_tickets(**service_data)
        db.session.add(new_service)  # add to session before appending mechanics

        for mechanic_id in mechanic_ids:
            query = select(Mechanics).where(Mechanics.id == mechanic_id)
            mechanic=db.session.execute(query).scalar()

            if mechanic:
                new_service.mechanics.append(mechanic)
            else:
                return jsonify({"message": f"Invalid mechanic id: {mechanic_id}"})

        db.session.commit()
    
        return jsonify({"Message": "New service ticket details added successfully",
                    "Service": return_service_schema.dump(new_service)}), 201
                          # return full nested result
    else:  
        return jsonify({"error" : "Customer id not in an account."}),400
    
#=================  Create Service Ticket without mechanics (POST)   ====================#
## API not using anymore Created for learning purpose:
@serviceTickets_bp.route('/', methods=['POST'])
def create_service_ticket():

    try:
        service_data= service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    # Retrieve the customer by its id.
    customer = db.session.get(Customer, service_data['customer_id'])

    # Check if the customer exists
    if customer:
        
        new_service= Service_tickets(**service_data)
 
        db.session.add(new_service)  
        db.session.commit()
    
        return jsonify({"Message": "New service ticket details added successfully",
                    "Service": service_ticket_schema.dump(new_service)}), 201
    else:
        return jsonify({"error" : "Customer id not in an account."}),400

#========== Retrieves all service tickets (GET) ===========================#

@serviceTickets_bp.route("/", methods=['GET'])
def get_service_tickets():

    query = select(Service_tickets)
    service = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service), 200


#========== Retrieves all service tickets from single customer (GET) ===========================#

## Create a route that requires a token, that returns the service_tickets related to that customer.

@serviceTickets_bp.route("/my-tickets", methods=['GET'])
@token_required
def get_customer_service_tickets(customer_id):

    query = select(Service_tickets).filter_by(customer_id = customer_id)
    service = db.session.execute(query).scalars().all()

    return service_tickets_schema.jsonify(service), 200

##=========== Retrieve Specific Service tickets (GET) ================== #

@serviceTickets_bp.route("/<int:service_id>", methods=['GET'])
def get_service_ticket(service_id):

    service = db.session.get(Service_tickets, service_id)
    if service:
        return service_ticket_schema.jsonify(service), 200
    
    return jsonify({"error": "Service id is not found."}), 404

# #============Edit Service Tickets to add and remove from mechanics details (PUT) ==============#

@serviceTickets_bp.route("/<int:service_id>", methods=['PUT'])
def edit_serviceTicket(service_id):
    try:
        service_edits = edit_service_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query= select(Service_tickets).where(Service_tickets.id == service_id)
    service = db.session.execute(query).scalars().first()

    if not service:
        return jsonify({"Message": "Service ticket not found."}), 404

    messages = []

    # Add mechanics
    for mechanic_id in service_edits.get('add_mechanic_ids',[]):
        query = select(Mechanics).where(Mechanics.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic:
            if mechanic not in service.mechanics:
                service.mechanics.append(mechanic)
                messages.append(f"Successfully added item to the mechanic id: {mechanic_id}")                    
            else:
                 messages.append(f"Details is {mechanic_id} already included in this service_tickets.")
        else:
             messages.append(f"Mechanic id: {mechanic_id} does not exist.")

    # Remove mechanics
    for mechanic_id in service_edits.get('remove_mechanic_ids',[]):
        query = select(Mechanics).where(Mechanics.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()

        if mechanic:
            if mechanic in service.mechanics:
                service.mechanics.remove(mechanic)    
                messages.append(f"Succefully removed mechanic id: {mechanic_id}")
            else:
                messages.append(f"Invalid {mechanic_id} is not attached to this service ticket.")
        else:
            messages.append(f"{mechanic_id} does not exist.")
    db.session.commit()

    return jsonify({
        "Messages": "New service ticket details added successfully and Remove successfully",
        "Mechanics" : messages,
        "Service": return_service_schema.dump(service)
    }), 200

#============EDIT SPECIFIC service===========
'''
@serviceTickets_bp.route("/<int:service_id>", methods=['PUT'])
def edit_service(service_id):
    try:
        service_edits= edit_service_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    
    query= select(Service_tickets).where(Service_tickets.id==service_id)
    service=db.session.execute(query).scalars().first()
    
    for mechanic_id in service_edits['add_mechanic_ids']:
        query= select(Mechanics).where(Mechanics.id == mechanic_id)
        mechanic=db.session.execute(query).scalars().first()
        
        if mechanic and mechanic not in service.mechanics:
            service.mechanics.append(mechanic)
            
    for mechanic_id in service_edits['remove_mechanic_ids']:
        query= select(Mechanics).where(Mechanics.id == mechanic_id)
        mechanic=db.session.execute(query).scalars().first()
        
        if mechanic and mechanic in service.mechanics:
            service.mechanics.remove(mechanic)
    
    db.session.commit()
    return return_service_schema.jsonify(service)
         
'''
# #============DELETE SPECIFIC Service Ticket  (DELETE) ==============#

@serviceTickets_bp.route("/<int:id>", methods=['DELETE'])
@limiter.limit("5 per hour") # limit this request to 5 times per hour
def delete_service(id):
    service = db.session.get(Service_tickets, id)

    if not service:
        return jsonify({"error": "service not found."}), 400
    
    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": f'service id: {id}, successfully deleted.'}), 200
    
##============ Update Specific Service_ticket and Mechanic details Using (PUT) =============#

## Adds a relationship between a service ticket and the mechanics
@serviceTickets_bp.route("/<int:service_id>/assign-mechanic/<int:mechanic_id>", methods=['PUT'])
def add_mechanic(service_id,mechanic_id):
     
     service = db.session.get(Service_tickets, service_id)
     mechanic= db.session.get(Mechanics,mechanic_id)
    
     if service and mechanic:
         if mechanic not in service.mechanics:
             service.mechanics.append(mechanic)
             db.session.commit()
             return jsonify({"Message": f"Successfully added item to the mechanic id is: {mechanic_id}  form service ticket id is: {service_id}."}), 200
         else:
            return jsonify({"Message" : "Details is already included in this service_tickets."}),400
         
     else:
         return jsonify({"Message" : "Invalid service_id or mechanic_id"}),400
      
         
##========= Remove Specific Service_ticket and Mechanic Using (PUT) =============#

## Removes the relationship from the service ticket and the mechanic using the PUT
@serviceTickets_bp.route("/<int:service_id>/remove-mechanic/<int:mechanic_id>", methods=['PUT'])
def remove_mechanic(service_id,mechanic_id):
     
     service = db.session.get(Service_tickets, service_id)
     mechanic= db.session.get(Mechanics,mechanic_id)

     if service and mechanic:
         if mechanic not in service.mechanics:
             return jsonify({"error" : "Mechanic is not assigned to this service ticket."}),400
         else:
             service.mechanics.remove(mechanic)
             db.session.commit()
             return jsonify({"Message" : f"Succefully removed the mechanic id is: {mechanic_id}  form service ticket id is: {service_id}."}),200
     else:
         return jsonify({"Message": "Invalid service_id or mechanic_id"}), 400
 

##========== Delete Specific Mechanic from an Service ticket Using (DELETE)=================#

@serviceTickets_bp.route("/<int:service_id>/delete-mechanic/<int:mechanic_id>", methods=['DELETE'])
def delete_mechanic(service_id,mechanic_id):

     service = db.session.get(Service_tickets, service_id)
     mechanic= db.session.get(Mechanics,mechanic_id)
          
     if service and mechanic:
          if mechanic not in service.mechanics:
             return jsonify({"error" : "Mechanic is not assigned to this service ticket."}),400
          else:
            db.session.delete(mechanic)
            db.session.commit()
            return jsonify({"message": f"succefully deleted the mechanic: {mechanic_id} and the product id is :{service_id}"}), 200
     else:

        return jsonify({"Message": "Invalid service_id or mechanic_id"}), 400


##============ Create Specific Service_ticket to add on Inventory details Using (POST) =============#

## To add a single part(inventory) to an existing Service Ticket.
## Adds a relationship between a service ticket and the inventory

@serviceTickets_bp.route('/<int:service_id>/add_part', methods=['POST'])  
def add_inventory(service_id):

    data = request.get_json()
    inventory_id = data.get('inventory_id')
    quantity = data.get('quantity')

    if not inventory_id or not quantity:
        return jsonify({"Message": "Both inventory_id and quantity are required."}), 400
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"Message": "Quantity must be an integer."}), 400

    if not inventory_id or quantity <= 0:
        return jsonify({"Message": "Both inventory_id and a positive quantity are required."}), 400
    
    service = db.session.get(Service_tickets, service_id)
    inventory = db.session.get(Inventory, inventory_id)

    # Check the service ticket exists and inventory part exists
    if not service or not inventory:
        return jsonify({"Message": "Invalid service id or inventory id."}), 400

    # Check if this inventory already linked to this service ticket
    query = select(ServiceInventory).filter_by(
        service_ticket_id=service_id,
        inventory_id=inventory_id )
    existing = db.session.execute(query).scalars().first()

    if existing:
        existing.quantity += quantity  # If already exists, just update quantity
        db.session.commit()
        updated_quantity = existing.quantity   #  updated quantity
    else:
            # Create new association
        new_link = ServiceInventory(
            service_ticket_id=service_id,
            inventory_id=inventory_id,
            quantity=quantity
        )
        db.session.add(new_link)
        db.session.commit()
        updated_quantity = quantity    # starting quantity
    return jsonify({"Message": "Part added to service ticket successfully.",
                    "service_ticket_id": service_id,
            "inventory_id": inventory_id,
            "quantity": updated_quantity  }), 200  # return total quantity