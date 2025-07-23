from flask import request,jsonify
from marshmallow import ValidationError
from .schemas import customer_schema,customers_schema,login_schema
from sqlalchemy import select,delete
from application.models import Customer,db
from . import customers_bp
from application.extensions import limiter,cache
from application.utils.util import encode_token,token_required

###================= Flask API with CRUD Endpoints ============================= ###

#=================  Create Login to Customer (POST)   ====================#
@customers_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']     
        password = credentials['password']

    except ValidationError as e:
        return jsonify({"error": e.messages,
                        'messages': 'Invalid payload, expecting username and password'}),400
    
    query = select(Customer).where(Customer.email == email)
    customer= db.session.execute(query).scalars().first() #Query customer table for a customer with this email

    if customer and customer.password == password: #if we have a customer associated with the customername, validate the password
        auth_token = encode_token(customer.id)

        response = {
            "status": "Success",
            "message": f"Successfully Logged In and the Customer name is: {customer.name} , customer id is: {customer.id}",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401


#=================  Create User (POST)   ====================#

@customers_bp.route('/', methods=['POST']) ## To make the Customer service high avabile limiting the number of input request implemented reat liming techique
@limiter.limit("40 per minute") # limit this request to 40 times per minute
def create_customer():

    try:	# Deserialize and validate input Customer
        customer_data= customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400

     		
    query = select(Customer).where(Customer.email == customer_data['email']) #Checking our db for a Customer with this email
    existing_customer = db.session.execute(query).scalars().all() 

    if existing_customer:
        return jsonify({"error" : "Email already associated with an account."}),400
      #use data to create an instance of Customer
    new_customer = Customer(**customer_data)
    #save new_user to the database
    db.session.add(new_customer)  
    db.session.commit()
    # Use schema to return the serialized data of the created Customer
    return jsonify({"Message": "New Customer details added successfully",
                    "customer": customer_schema.dump(new_customer)}), 201

#========== Retrieve Customers (GET) ===========================#
'''
@customers_bp.route("/", methods=['GET'])
# @limiter.limit("3 per hour") # A client can only attempt to make(limit this request to 3 times per hour) 3 users per hour other way to call ("3/hour")
@cache.cached(timeout=30) ## To impove the get customers API performances configure cacheing mechanisham implemted simple cacheing
def get_customers():
    
    query = select(Customer)
    print("db is executed")
    customer = db.session.execute(query).scalars().all()


    return customers_schema.jsonify(customer)
'''
#========== Retrieve Customers using pagination (GET) ===========================#

@customers_bp.route("/", methods=['GET'])
# @limiter.limit("3 per hour") # A client can only attempt to make(limit this request to 3 times per hour) 3 users per hour other way to call ("3/hour")
@cache.cached(timeout=30, query_string=True) ## To impove the get customers API performances configure cacheing mechanisham implemted simple cacheing
def get_customers():
    
    try:
        page = int(request.args.get("page"))  ## converting to interger
        per_page = int(request.args.get("per_page"))
        query = select(Customer)
        customers = db.paginate(query, page = page, per_page = per_page)  ## pagination used to page and per_page numbers based on retrieve the customers
        
        return customers_schema.jsonify(customers),200

    except:
        query = select(Customer)
        print("db is executed")
        customers = db.session.execute(query).scalars().all()

        return customers_schema.jsonify(customers),200

#=========== Retrieve Specific Customer (GET) ================== #

@customers_bp.route("/<int:customer_id>", methods=['GET'])
def get_customer(customer_id):

    customer = db.session.get(Customer, customer_id)
    if customer:
        return customer_schema.jsonify(customer), 200
    
    return jsonify({"error": "Customer not found."}), 404

#============ Update Specific Customer details (PUT) =============#

@customers_bp.route("/", methods=['PUT'])
# @limiter.limit("5 per hour") # limit this request to 5 times per hour
@token_required
def update_customer(customer_id):
    
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "customer not found."}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in customer_data.items():
        setattr(customer, key, value)

    db.session.commit()

    return jsonify({"Message": f'Successfully Updated Customer id: {customer_id}',
                    "customer": customer_schema.dump(customer)}), 200

#========== Delete Specific Customer details (DELETE)=================#


@customers_bp.route("/", methods=['DELETE'])
# @limiter.limit("5 per day") # limit this request to 5 times per day
@token_required
def delete_customer(customer_id):

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({"Message": f'customer id: {customer_id}, successfully deleted.'}), 200


