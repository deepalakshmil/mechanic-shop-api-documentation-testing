
from application import create_app, db
from application.models import Mechanics, Service_tickets, Customer
from datetime import date
import unittest   ## Imports Python’s unittest framework for setting up and running tests.

class TestMechanic(unittest.TestCase):
        ##   Unit tests for the Mechanic routes, including auth and CRUD operations  ###
    def setUp(self):
        self.app = create_app('TestingConfig') ## Creates a test app instance using TestingConfig
        self.client = self.app.test_client()  ##  Sets up a test client to send requests.
        with self.app.app_context(): ##  Initializes a test database context:
            db.create_all()

            mechanic1 = Mechanics(name="test_user2", email="test2@email.com", address="3st test street", phone="989-4645-3234")
            mechanic2 = Mechanics(name="test_user3", email="test3@email.com", address="4st test street", phone="432-4635-2222")
            mechanic3 = Mechanics(name="test_user4", email="test4@email.com", address="5st test street", phone="123-4643-2209")
            db.session.add_all([mechanic1,mechanic2,mechanic3])
            db.session.commit()
            self.mechanic1_id = mechanic1.id
            self.mechanic2_id = mechanic2.id
            self.mechanic3_id = mechanic3.id        

        self.mechanic_payload = {
            "name": "Rosye",
            "address": "1001, North street",
            "email": "rosy@gmail.com",            
            "phone": "897-7876-2689"
        }

    ##================================= Create Mechanic Testcase ================================##

    def test_create_mechanic_success(self):
            ### Test creating a new mechanic successfully ###

        response = self.client.post('/mechanics/', json=self.mechanic_payload)

        self.assertEqual(response.status_code, 201)
        print("response", response.json)
        self.assertIn('Mechanic',response.json)
        self.assertEqual(response.json['Mechanic']['name'], "Rosye")
        self.assertEqual(response.json['Mechanic']['email'], "rosy@gmail.com")
        self.assertEqual(response.json['Message'], "New Mechanic details added successfully")

            ### Negative Test: Invalid Customer Creation ###
    def test_create_mechanic_validation_error(self):
            # Test creating a mechanic with missing required field #
        invalid_payload = self.mechanic_payload.copy()
        invalid_payload.pop('address')
        invalid_payload.pop('phone')

        response = self.client.post('/mechanics/', json=invalid_payload)

        print("Validation Error Response Error:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.json, dict)
        # The exact validation message depends on your schema; adjust as needed
        self.assertIn('address', response.json)
        self.assertIn('phone', response.json)
        self.assertEqual(response.json['address'][0], "Missing data for required field.")
        self.assertIn("Missing data for required field.", response.json['phone'])

            ## Negative Test: Test creating a mechanic with an email that already exists ##
    def test_create_mechanic_duplicate_email(self):
            #Test creating a mechanic with an email that already exists #
            # First insert   
        response = self.client.post('/mechanics/', json=self.mechanic_payload)
            # Second insert with same email

        response = self.client.post('/mechanics/', json=self.mechanic_payload)

        print("Duplicate Response JSON:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'],"Email already associated with an account.")

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()      ## To ensure clean DB reset after each test 
            db.drop_all()

    ##============================= Retrieve all Mechanics Testcase =============================##

    def test_get_all_mechanics_success(self):
            # Test retrieving all mechanics 
        response = self.client.get('/mechanics/')

        print("All mechanics Response JSON:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 3)   # 3 added in setUp
        self.assertIn('name',response.json[0])
        print('name',response.json[0])
            # check that emails are from test_user2 and test_user3
        emails = [mechanic['email'] for mechanic in response.json]
        self.assertIn('test2@email.com', emails)
        self.assertIn('test3@email.com', emails)
        self.assertIn('test4@email.com', emails)

    ##============================ Retrieve Specific Mechanic Testcase ==========================##

    def test_get_mechanic_by_id_success(self):
        # Test retrieving a mechanic by valid ID  #
        mechanic_id = self.mechanic1_id
        print("Mechanic_id",mechanic_id)

        response = self.client.get(f'/mechanics/{mechanic_id}')

        print("Get by ID response Json",response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['email'],"test2@email.com")
        self.assertEqual(response.json['name'], 'test_user2')

        # Negative Test: Retrieve Mechanic by Invalid ID (404 Case) #
    def test_get_mechanic_by_id_not_found(self):
        not_existent_id = 100

        response = self.client.get(f'/mechanics/{not_existent_id}')

        print("Invalid ID Response JSON:", response.json)
        self.assertEqual(response.status_code, 404)
        self.assertIsInstance(response.json, dict)
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], "Mechanic id is not found.")
    
    ##========================== Update Specific Mechanic details Testcase=======================##

    def test_update_mechanic_success(self):
        update_mechanic_payload={
            "name": "New_test_user3",
            "address": "15/3, test street",
            "email": "testnew@gmail.com",            
            "phone": "111-1111-2211"
        }

        response = self.client.put(f'/mechanics/{self.mechanic2_id}',json = update_mechanic_payload)

        print("Update Success Response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Message",response.json)
        self.assertEqual(response.json['mechanic']['name'],'New_test_user3')
        self.assertEqual(response.json['Message'],f'Successfully Updated Mechanic id: {self.mechanic2_id}')

            ## Negative Test: Update Mechanic — Invalid Input ##
    def test_update_mechanic_validation_error(self):
        invalid_payload = {
            "name": "No Email",
            "address": "Somewhere Street"
            # Missing email and phone
                        }

        response = self.client.put(f'/mechanics/{self.mechanic1_id}', json=invalid_payload)

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.json)
        self.assertIn('phone', response.json)
        print("Update Validation Error Response:", response.json)
    
            ## Negative Test: Update Non-existent Mechanic (404)
    def test_update_mechanic_not_found(self):
        payload = {
            "name": "nofound",
            "email": "nofound@email.com",
            "address": "Nowhere",
            "phone": "000-000-0000"
                }

        response = self.client.put('/mechanics/99', json=payload)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Mechanic id is not found.")
        print("Update Not Found Response:", response.json)

    ##============================= Delete Specific Mechanic details Testcase ========================##

    def test_delete_mechanic_success(self):

        response = self.client.delete(f'/mechanics/{self.mechanic1_id}')

        print("Delete Success Response",response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message',response.json)
        self.assertEqual(response.json['message'],f'mechanic id: {self.mechanic1_id}, successfully deleted.')
    
            ## Negative Test: Delete Mechanic Not Found (404) ##
    def test_delete_mechanic_not_found(self):
        response = self.client.delete('/mechanics/111')
    
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Mechanic not found.")
        print("Delete Not Found Response:", response.json)

    ##======= Retrieve a list of mechanic name(use search passing parameter with  name) Testcase ========##

    def test_get_popular_mechanics_success(self):
        with self.app.app_context():
            # Ensure a customer with id=1 exists (to avoid IntegrityError)
            customer = db.session.get(Customer, 1)

            if not customer:
                customer = Customer(
                name="Test Customer",
                email="customer1@email.com",
                password="test",
                address="123 Test St",
                phone="123-456-7890",
                salary=50000.0
            )

            db.session.add(customer)
            db.session.commit()

            # Fetch test mechanics
            mechanic1 = db.session.get(Mechanics, self.mechanic1_id)
            mechanic2 = db.session.query(Mechanics).filter_by(email="test3@email.com").first()
            mechanic3 = db.session.get(Mechanics, self.mechanic3_id)

            # create 3 service tickets
            service1 = Service_tickets(VIN="TTT2676234634320", customer_issue="Brake Repair", customer_id=customer.id, service_date= date(2025,7,20))
            service2 = Service_tickets(VIN="EEE1676234634326", customer_issue="Oil Change", customer_id=customer.id, service_date= date(2025,12,10))
            service3 = Service_tickets(VIN="RRR2676234634323", customer_issue="Tire Rotation", customer_id=customer.id, service_date=date(2026,5,23))

            # Assign tickets: mechanic3 gets most, then mechanic1, then mechanic2
            mechanic3.services.extend([service1, service2,service3]) ## 3 services    ## The .extend() method is used to add multiple items to a list at once -- by extending the list with another iterable (like another list or a set of items).
            mechanic1.services.extend([service1,service2])  ## 2 services
            mechanic2.services.append(service2) ## 1 services

            db.session.add_all([service1,service2,service3])
            db.session.commit()

            # Now call the popular-mechanic endpoint
            response = self.client.get('/mechanics/popular-mechanic')

            print("response popular", response.json)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Most popular Mechanics List Order by:", response.json)

            mechanic_list = response.json["Most popular Mechanics List Order by:"]
            print("mechanic_list",mechanic_list)
            self.assertGreater(len(mechanic_list),2)  ## Ensures that at least 3 mechanics were returned in the response.

                # Check sorting correctness: popular mechanics first
            ids = [mechanic["id"] for mechanic in mechanic_list] ## mechanic IDs into a list.
            services_counts = [len(db.session.get(Mechanics, mid).services) for mid in ids] ## counts how many service tickets each mechanic has.

                # Ensure the list is sorted by number of services in descending order
            self.assertEqual(services_counts, sorted(services_counts, reverse=True))
            print("service_count",services_counts) ##[3,2,1]

                # ensures the mechanics are listed from most to least popular by number of services.
            self.assertTrue(all(services_counts[i] >= services_counts[i+1] for i in range(len(services_counts)-1)))
            print("Popular mechanics order response:", response.json)

    ##========== Retrieve a list of mechanic name(use search passing parameter with  name) Testcase  ============##
        
    def test_search_mechanic_by_name_success(self):
        response = self.client.get('/mechanics/search?name=test_user')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)  # Should return at least one match
        print("Number of results:",len(response.json))
        for mechanic in response.json:
            self.assertIn('test_user', mechanic['name'])   # Ensure it matches the query
            self.assertNotIn("peter", mechanic['name'])    # Should not contain unrelated names
            self.assertNotEqual(mechanic['name'], 'user')  # Reject exact unrelated name
    
        ## Negative Test:  Add search edge case tests (no results or empty name) ##
    def test_search_mechanic_no_match(self):
        response = self.client.get('/mechanics/search?name=xyz_no_match')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_search_mechanic_empty_param(self):
        response = self.client.get('/mechanics/search?name=')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)        
    
    if __name__ == '__main__':
        unittest.main()