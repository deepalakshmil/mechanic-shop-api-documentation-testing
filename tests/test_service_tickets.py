from application import create_app, db
from application.models import Customer, Service_tickets, Mechanics, Inventory ,ServiceInventory
from datetime import date
from application.utils.util import encode_token
import unittest 


class TestServiceTicket(unittest.TestCase):
        ###   Unit tests for the ServiceTicket routes, including auth and CRUD operations  ###
    def setUp(self):
        # Create app and push context
        self.app = create_app('TestingConfig') ## Creates a test app instance using TestingConfig
        # self.app.app_context(): ##  Initializes a test database context:
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create test client
        self.client = self.app.test_client()  ##  Sets up a test client to send requests.

        # Clean DB to avoid UNIQUE constraint errors
        db.drop_all()
        db.create_all()

        # Create customers test data
        customer1 = Customer(name="Saba", email="test@email.com", password="test",
                                address="Street 123", phone="123-456-7890", salary=55000.00)
        customer2 = Customer(name="test_user1", email="test1@email.com", password="test1",
                                address="2st test street", phone="123-4645-2222", salary=60000.0)            
        db.session.add_all([customer1,customer2])
        db.session.commit()
        # Save IDs
        self.customer1_id = customer1.id
        self.customer2_id = customer2.id
            
        # Create mechanics
        mechanic1 = Mechanics(name="test_user2", email="test2@email.com", address="3st test street", phone="989-4645-3234")
        mechanic2 = Mechanics(name="test_user3", email="test3@email.com", address="4st test street", phone="432-4635-2222")
        mechanic3 = Mechanics(name="test_user4", email="test4@email.com", address="5st test street", phone="123-4643-2209")
        db.session.add_all([mechanic1,mechanic2,mechanic3])
        db.session.commit()
        # Save IDs
        self.mechanic1_id = mechanic1.id
        self.mechanic2_id = mechanic2.id
        self.mechanic3_id = mechanic3.id

        # Create service_ticket
        service1 = Service_tickets(VIN="TTT2676234634320", customer_issue="Brake Repair", customer_id=self.customer1_id, service_date= date(2025,7,20))
        service2 = Service_tickets(VIN="EEE1676234634326", customer_issue="Oil Change", customer_id=self.customer1_id, service_date= date(2025,12,10))
        service3 = Service_tickets(VIN="RRR2676234634323", customer_issue="Tire Rotation", customer_id=self.customer1_id, service_date=date(2026,5,23))
        db.session.add_all([service1,service2,service3])
        db.session.commit()

        # Save IDs
        self.service1_id = service1.id
        self.service2_id = service2.id
        self.service3_id = service3.id

        # self.token = encode_token(3)
        self.auth_token = self.get_auth_token()
        self.assertIsNotNone(self.auth_token)  ## Check the token value is None , the test will fail at this point 
                                                # Fail if token is None
        # Prepare payloads for testing                                        
        self.serviceticket_mechanic_payload = {
                    "VIN": "RRR567623463213",
                    "service_date":"2025-07-20",
                    "customer_issue":"Alternator failure",
                    "customer_id": self.customer1_id,
                    "mechanic_ids": [self.mechanic1_id, self.mechanic2_id]
        }

        self.serviceticket_payload = {
            "VIN": "RRR567623463213",
            "service_date": "2025-07-20",
            "customer_issue": "Alternator failure",
            "customer_id": self.customer2_id
        }

    ##===================================== Create ServiceTicket Testcase ====================================##

    def test_create_serviceticket_with_mechanic_success(self):
            ### Test creating a new ServiceTicket with mechanic successfully ###
        response = self.client.post('/service-tickets/with-mechanics', json= self.serviceticket_mechanic_payload)

        self.assertEqual(response.status_code, 201)
        print("response", response.json)
        self.assertIn("New service ticket details added successfully",response.json['Message'])
        self.assertEqual(response.json['Service']['customer_issue'], "Alternator failure")
        # Check customer details
        customer_id = response.json['Service']['customer']['id']
        self.assertEqual(customer_id, self.customer1_id)
        # self.assertEqual(len(response.json['Service']['mechanic_ids']), 2)
        mechanics = response.json['Service'].get('mechanics')
        self.assertIsInstance(mechanics, list)
        self.assertEqual(len(mechanics), 2)

    ##================================= Create ServiceTicket without mechanic Testcase =====================##

    def test_create_serviceticket_without_mechanics_success(self):
        
        response = self.client.post('/service-tickets/', json=self.serviceticket_payload)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn("New service ticket details added successfully", response.json['Message'])

        service_data = response.json['Service']
        self.assertEqual(service_data['customer_issue'], "Alternator failure")
        self.assertEqual(service_data['VIN'], "RRR567623463213")
        self.assertEqual(service_data['customer_id'], self.customer2_id)
        self.assertEqual(service_data['service_date'], "2025-07-20")

            ### Negative Test: Invalid ServiceTicket Creation ###
    def test_create_service_ticket_validation_error(self):
            # Test creating a ServiceTicket with missing required field #
        invalid_payload = self.serviceticket_mechanic_payload.copy()
        invalid_payload.pop('customer_id')
        invalid_payload.pop('VIN')

        response = self.client.post('/service-tickets/with-mechanics', json=invalid_payload)

        print("Validation Error Response Error:", response.json)
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.json, dict)
        # The exact validation message depends on your schema; adjust as needed
        self.assertIn('customer_id', response.json)
        self.assertIn('VIN', response.json)
        self.assertIn('Missing data for required field.',response.json['VIN'])

    def tearDown(self):
        # with self.app.app_context():
        db.session.remove()   ## To ensure clean DB reset after each test 
        db.drop_all()
        self.app_context.pop()
    
    ##=============== Retrieves all service tickets from single customer Testcase =============================##
    ## Test for Create a route that requires a token, that returns the service_tickets related to that customer.
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

    def test_get_service_tickets_for_customer_success(self):        
        headers = {'Authorization': f"Bearer {self.auth_token}"}

        response = self.client.get('/service-tickets/my-tickets', headers=headers)

        print("My Tickets Response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)

        for ticket in response.json:
            self.assertEqual(ticket['customer_id'], self.customer1_id)
            self.assertIn('VIN', ticket)
            self.assertIn('customer_issue', ticket) 

    ##=============================== Retrieves all service tickets Testcase ================================ ##

    def test_get_service_tickets_success(self):
            #Test retrieving all service tickets 
        response = self.client.get('/service-tickets/')

        print("All Service Tickets Response JSON:", response.json)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)   # at least the two inserted service tickets

            # Optional: check specific fields in the first ticket
        self.assertIn('VIN', data[0])
        self.assertIn('customer_issue', data[0])

    ##=========================== Retrieve Specific Service tickets Testcase ==============================##

    def test_get_service_ticket_by_id_success(self):
        # Make GET request to the endpoint with service_id
        response = self.client.get(f'/service-tickets/{self.service1_id}')

        print("Specific Service Tickets Response JSON:", response.json)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], self.service1_id)
        self.assertEqual(data['VIN'], "TTT2676234634320")
        self.assertEqual(data['customer_issue'], "Brake Repair")

        # Negative Test: Retrieve customer by Invalid ID (404 Case) #
    def test_get_service_ticket_by_id_not_found(self):
        # Use an ID that does not exist, e.g., 777
        response = self.client.get('/service-tickets/777')

        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)
        self.assertEqual(data['error'], "Service id is not found.")

    ##=============== Edit Service Tickets to add and remove from mechanics details Testcase ===============##

    def test_edit_service_ticket_add_remove_mechanics_success(self):
        # # Prepare edit payload to add and remove the mechanic (should add, then try to remove)
        payload = {
        "add_mechanic_ids": [self.mechanic1_id,self.mechanic2_id],
        "remove_mechanic_ids": []
                }
        
        response = self.client.put(f'/service-tickets/{self.service2_id}', json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn("Messages", data)
        self.assertIn("Successfully added item to the mechanic id", str(data["Mechanics"]))
        self.assertEqual(data["Service"]["id"], self.service2_id)

        # Now test removing the same mechanics
        payload = {
        "add_mechanic_ids": [],
        "remove_mechanic_ids": [self.mechanic1_id,self.mechanic2_id]
                }
        
        response = self.client.put(f'/service-tickets/{self.service2_id}', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        print("data",data)
        self.assertIn("Succefully removed mechanic id", str(data["Mechanics"]))
        mechanic_ids = [mech["id"] for mech in data["Service"]["mechanics"]]
        self.assertNotIn(self.mechanic1_id, mechanic_ids)
        self.assertNotIn(self.mechanic2_id, mechanic_ids)
        

            ## Negative Test: Validation Test: Invalid Mechanic
    def test_edit_service_ticket_with_invalid_mechanic(self):
        invalid_mechanic_id = 666  # non-existent ID
        payload = {
            "add_mechanic_ids": [invalid_mechanic_id],
            "remove_mechanic_ids": []
                }

        response = self.client.put(f'/service-tickets/{self.service2_id}', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertIn(f"Mechanic id: {invalid_mechanic_id} does not exist.", str(data["Mechanics"]))

    ##==================== Update Specific Service_ticket to assign Mechanic details Testcase ==================##

    def test_assign_mechanic_to_service_ticket_success(self):
        # Assign mechanic1 to service2
        response = self.client.put(f'/service-tickets/{self.service2_id}/assign-mechanic/{self.mechanic1_id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Successfully added", response.get_json()["Message"])

        # Try assigning again - should get 400
        response = self.client.put(f'/service-tickets/{self.service2_id}/assign-mechanic/{self.mechanic1_id}')
    
        self.assertEqual(response.status_code, 400)
        self.assertIn("Details is already included in this service_tickets.", response.json["Message"])

    ##=================== Remove Specific Service_ticket and Mechanic details Testcase ========================##

    def test_remove_mechanic_from_service_ticket_success(self):
            # First assign mechanic to ensure it’s attached
        self.client.put(f'/service-tickets/{self.service2_id}/assign-mechanic/{self.mechanic1_id}')

            # Now remove the mechanic
        response = self.client.put(f'/service-tickets/{self.service2_id}/remove-mechanic/{self.mechanic1_id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Succefully removed", response.get_json()["Message"])

            # Try removing again — should fail
        response = self.client.put(f'/service-tickets/{self.service2_id}/remove-mechanic/{self.mechanic1_id}')
    
        self.assertEqual(response.status_code, 400)
        self.assertIn("Mechanic is not assigned to this service ticket.", response.json["error"])
        #  Check in DB that mechanic is removed from service
        service = db.session.get(Service_tickets, self.service2_id)
        mechanic_ids = [m.id for m in service.mechanics]
        self.assertNotIn(self.mechanic1_id, mechanic_ids)
    
    ##========================== DELETE SPECIFIC Service Ticket Testcase ====================================##

    def test_delete_service_ticket_success(self):
        service_id=self.service3_id

        # Perform DELETE request
        response = self.client.delete(f'/service-tickets/{service_id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json)
        self.assertEqual(response.json['message'],f"service id: {service_id}, successfully deleted.")

        # Confirm it's actually deleted
        deleted_service = db.session.get(Service_tickets, service_id)
        self.assertIsNone(deleted_service)

        ## Negative Test: Delete Non-Existent Service Ticket
    def test_delete_service_ticket_not_found(self):
        response = self.client.delete('/service-tickets/99')  # assuming this ID doesn't exist
        self.assertEqual(response.status_code, 400)
        self.assertIn("service not found", response.get_json()["error"])

        ## Edge Case: Deleting Twice
    def test_delete_service_ticket_twice(self):
        service_id=self.service2_id

        # First delete
        response1 = self.client.delete(f'/service-tickets/{service_id}')
        self.assertEqual(response1.status_code, 200)

        # Second delete should return 400
        response2 = self.client.delete(f'/service-tickets/{service_id}')
        self.assertEqual(response2.status_code, 400)
        self.assertIn("service not found", response2.get_json()["error"])

    ##============ Create Specific Service_ticket to add on Inventory details Testcase =================##
    
    def test_add_inventory_to_service_ticket_success(self):
            #create required inventory
        inventory1 = Inventory(name="Brake Pad", price=100.0)
        inventory2 = Inventory(name="Tire", price=500.0)

        db.session.add_all([inventory1,inventory2])
        db.session.commit()

            # Step 1: Prepare payload to add an inventory part
        inventory_payload = {
                        "inventory_id": inventory1.id,
                        "quantity": 3
                            }

            # Step 2: Call the POST endpoint to add part
        response = self.client.post(f"/service-tickets/{self.service2_id}/add_part", json=inventory_payload)

            # Step 3: Validate response
        print("Response add inventory", response.json)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Message", data)
        self.assertEqual(data["Message"], "Part added to service ticket successfully.")
        self.assertEqual(data["service_ticket_id"], self.service2_id)
        self.assertEqual(data["inventory_id"], inventory1.id)
        self.assertEqual(data["quantity"], 3)

        # Step 4: Add same part again to test quantity update
        inventory_payload["quantity"] = 2
        second_response = self.client.post(f"/service-tickets/{self.service2_id}/add_part", json=inventory_payload)
        print("Second Response add inventory", second_response.json)
        self.assertEqual(second_response.status_code, 200)
        second_data = second_response.get_json()
        self.assertEqual(second_data["quantity"], 3+2)  # total quantity should now be 5
        link = db.session.query(ServiceInventory).filter_by(service_ticket_id=self.service2_id,
                                                            inventory_id=inventory1.id).first()
        self.assertEqual(link.quantity, 5)

    if __name__ == '__main__':
        unittest.main()