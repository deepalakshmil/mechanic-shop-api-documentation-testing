
from application import create_app, db
from application.models import Customer
from application.utils.util import encode_token
import unittest   ## Imports Python’s unittest framework for setting up and running tests.

class TestCustomer(unittest.TestCase):
        ###   Unit tests for the Customer routes, including auth and CRUD operations  ###
    def setUp(self):
        self.app = create_app('TestingConfig') ## Creates a test app instance using TestingConfig
        with self.app.app_context(): ##  Initializes a test database context:
            db.create_all()

            customer1 = Customer(name="test_user", email="test@email.com", password="test",
                                address="1st test street", phone="123-4645-3234", salary=50000.0)
            customer2 = Customer(name="test_user1", email="test1@email.com", password="test1",
                                address="2st test street", phone="123-4645-2222", salary=60000.0)
            db.session.add_all([customer1,customer2])
            db.session.commit()
            self.customer1_id = customer1.id
            self.customer2_id = customer2.id
        self.client = self.app.test_client()  ##  Sets up a test client to send requests.
        # self.token = encode_token(3)
        self.auth_token = self.get_auth_token()
        self.assertIsNotNone(self.auth_token)  ## Check the token value is None , the test will fail at this point 
                                                # Fail if token is None
        self.customer_payload = {
            "name": "Saba",
            "email": "saba@gmail.com",
            "password": "saba",
            "address": "1st west street",
            "phone": "574-212-2675",
            "salary": 11000.0
        }

    def test_customer_query_access(self):
        with self.app.app_context():
            count = db.session.query(Customer).count()
            print("count", count)
            self.assertIsInstance(count, int)
            
    ##=============================== Create Customer Testcase =============================##

    def test_create_customer_success(self):
            ### Should successfully create a customer with valid data ###

        response = self.client.post('/customers/', json=self.customer_payload)

        self.assertEqual(response.status_code, 201)
        print("response", response.json)
        self.assertIn('customer',response.json)
        self.assertEqual(response.json['customer']['name'], "Saba")
        self.assertEqual(response.json['customer']['email'], "saba@gmail.com")
        self.assertEqual(response.json['Message'], "New Customer details added successfully")

            ### Negative Test: Invalid Customer Creation ###
    def test_create_customer_validation_error(self):
            # Test creating a customer with missing required field (like email) #
        invalid_payload = self.customer_payload.copy()
        invalid_payload.pop('password')

        response = self.client.post('/customers/', json=invalid_payload)

        print("Validation Error Response Error:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.json, dict)
        # The exact validation message depends on your schema; adjust as needed
        self.assertIn('password', response.json)

            ### Negative Test:Test creating a customer with an email that already exists ###
    def test_create_customer_duplicate_email(self):
            #Test creating a customer with an email that already exists #
            # First insert   
        response = self.client.post('/customers/', json=self.customer_payload)
            # Second insert with same email

        response = self.client.post('/customers/', json=self.customer_payload)

        print("Duplicate Response JSON:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'],"Email already associated with an account.")
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()    ## To ensure clean DB reset after each test 
            db.drop_all()

    ##================================ Create Login Customer Testcase ===========================##

    def test_login_customer_success(self):
        credentials  = {
            "email": "test@email.com",
            "password": "test"
        }

        response = self.client.post('/customers/login', json= credentials)

        self.assertEqual(response.status_code , 200)
        self.assertEqual(response.json['status'], 'Success')
        self.assertIsInstance(response.json['auth_token'], str)
        self.assertGreater(len(response.json['auth_token']), 20) # optional: check length > 20
    
    def get_auth_token(self):
            ###  Login with test user and return valid auth token for protected routes ###
        response = self.client.post('/customers/login', json = { "email": "test@email.com"  , "password": "test"})

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("auth_token", data)
        self.assertIsInstance(data["auth_token"], str)
        self.assertGreater(len(data["auth_token"]), 20)
        print("Autho_token",data)

        return data['auth_token']

            ## Negative Test: Invalid Login Test ##
    def test_invalid_login(self):
        credentials = {
            "email": "bad_email@email.com",
            "password": "bad_pw"
        }

        response = self.client.post('/customers/login', json=credentials)

        print("response.status_code", response.status_code)
        self.assertEqual(response.status_code , 401)
        self.assertEqual(response.json['messages'], 'Invalid email or password')

    ##=========================== Retrieve all Customers using pagination Testcase ===========================##

    def test_get_customers_with_pagination_success(self):
        # Test retrieving customers with pagination #

        response = self.client.get('/customers/?page=1&per_page=2')

        print("paginated Response Json",response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)   # because customers_schema.jsonify(customers) returns list
        self.assertEqual(len(response.json), 2)      # should return 2 items on first page
            # check the first customer's email matches one of the inserted
        self.assertIn(response.json[0]['email'], ['test@email.com', 'test1@email.com'])
        emails = [customer['email'] for customer in response.json]
        for email in ['test@email.com', 'test1@email.com']:
            with self.subTest(email=email):
                self.assertIn(email, emails)

    def test_get_customers_without_pagination_success(self):
            #Test retrieving all customers without pagination params
        response = self.client.get('/customers/')
        print("All customers Response JSON:", response.json)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 2)   # at least the two inserted customers
            # check that emails are from test_user and test_user1
        emails = [customer['email'] for customer in response.json]
        self.assertIn('test@email.com', emails)
        self.assertIn('test1@email.com', emails)

    ##============================== Retrieve Specific Customer  Testcase ==============================##

    def test_get_customer_by_id_success(self):
        customer_id = self.customer1_id
        print("customer_id",customer_id)

        response = self.client.get(f'/customers/{customer_id}')

        print("Get by ID response Json",response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'],"test@email.com")
        self.assertEqual(response.json['name'], 'test_user')

        # Negative Test: Retrieve customer by Invalid ID (404 Case) #
    def test_get_customer_by_invalid_id(self):
        not_existent_id = 50

        response = self.client.get(f'/customers/{not_existent_id}')

        print("Invalid ID Response JSON:", response.json)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], "Customer not found.")
    
                            ##==== Token Authenticated Route Test ====##
    ##====================== Update Specific Customer details(token authenticated) Testcase =================##

    def test_update_customer_success(self):
        # token= self.get_auth_token()

        updated_customer_payload = {
            "name": "sabaresh",
            "email": "",
            "address": "100th, bigroundhill",
            "phone": "123-2342-3211",
            "salary":0 ,
            "password":""
        }

        response = self.client.put('/customers/', json = updated_customer_payload, 
                                                        headers = {"Authorization": f"Bearer {self.auth_token}"})

        print("Update Success:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Message", response.json)
        self.assertEqual(response.json["customer"]["name"], "sabaresh")
        self.assertEqual(response.json["customer"]["phone"], "123-2342-3211")

            #==== Negative TEST: Update with non-existent customer =====#
    def test_update_customer_not_found(self):
        # Create token with fake customer_id (e.g.,999)
        fake_token = encode_token(999)

        updated_data = {
            "name": "Should Not Work",
            "email": "fake@email.com",
            "password": "test",
            "address": "Nowhere",
            "phone": "000-000-0000",
            "salary": 12345.67
        }

        response = self.client.put('/customers/',json=updated_data,
                                                headers={"Authorization": f"Bearer {fake_token}"})

        print("Non-existent user update:", response.json)
        self.assertEqual(response.status_code, 401)  # Unauthorized
        print("response_code", response.status_code)
        self.assertIn("message", response.json)

        self.assertEqual(response.json["message"], "Invalid token — customer does not exist.")    

    ##===================== Delete Specific Customer details(token authenticated) Testcase ====================##

    def test_delete_customer_success_then_cannot_get_customer(self):
            # Step 1: Delete the customer
        response = self.client.delete('/customers/', headers={"Authorization": f"Bearer {self.auth_token}"})
    
        print("Delete response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Message", response.json)
        self.assertEqual(response.json["Message"], f"customer id: {self.customer1_id}, successfully deleted.")

            # Step 2: Try to retrieve the deleted customer
        get_response = self.client.get(f"/customers/{self.customer1_id}")
        print("Get after delete:", get_response.json)
        self.assertEqual(get_response.status_code, 404)
        self.assertIn("error", get_response.json)
        self.assertEqual(get_response.json["error"], "Customer not found.")

    if __name__ == '__main__':
        unittest.main()