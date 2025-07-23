from application import create_app, db
from application.models import  Inventory
import unittest 

class TestInventory(unittest.TestCase):
        ###   Unit tests for the Inventory routes, including auth and CRUD operations  ###
    def setUp(self):
        # Create app and push context
        self.app = create_app('TestingConfig') 
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create test client
        self.client = self.app.test_client()  ##  Sets up a test client to send requests.

        # # Clean DB to avoid UNIQUE constraint errors
        # db.drop_all()
        db.create_all()

        # Create Inventories test data
        inventory1 = Inventory(name="Radiator", price=50.00)
        inventory2 = Inventory(name="Grille", price=65.00)
        inventory3 = Inventory(name="Bumper", price=200.00)               
        
        
        db.session.add_all([inventory1,inventory2,inventory3])
        db.session.commit()

        # Save IDs
        self.inventory1_id = inventory1.id
        self.inventory2_id = inventory2.id
        self.inventory3_id = inventory3.id

        self.inventory_payload =  {
                    "name" :"Fenders",
                    "price": 4500.0
                            }
        
    ##===============================  Create Inventory Testcase  ===============================##

    def test_create_inventory_success(self):
            ### Should successfully create a inventory with valid data ###

        response = self.client.post('/inventories/', json=self.inventory_payload)

        self.assertEqual(response.status_code, 201)
        print("response", response.json)
        self.assertIn('Inventory',response.json)
        self.assertEqual(response.json['Inventory']['name'], "Fenders")
        self.assertEqual(response.json['Inventory']['price'], 4500.00)
        self.assertEqual(response.json['Message'], f"The {self.inventory_payload['name']} New Inventory details added successfully")
    
            ## Negative Test: Invalid inventory Creation ##
    def test_create_inventory_missing_fields(self):
        # Missing 'price'
        payload = {
            "name": "Spark Plug"
        }

        response = self.client.post('/inventories/', json=payload)

        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        self.assertIn("price", data["error"])  # from Marshmallow validation

        ## Negative Test: Invalid inventory Creation ##
    def test_create_inventory_invalid_price(self):
        # Invalid price type
        payload = {
            "name": "Brake Pad",
            "price": "free"
        }

        response = self.client.post('/inventories/', json=payload)

        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", data)
        self.assertIn("price", data["error"])
    
    def tearDown(self):
        db.session.remove()   ## To ensure clean DB reset after each test 
        db.drop_all()
        self.app_context.pop()
    
    ##======================== Retrieve all Inventories Testcase ==============================##

    def test_get_all_inventories_success(self):
            #Test retrieving all inventories
        response = self.client.get('/inventories/')

        print("All Inventories Response JSON:", response.json)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)   # at least the two inserted inventories

            # Optional: check specific fields in the inventories list
        self.assertIn('name', data[0])
        self.assertIn('price', data[0])
        self.assertEqual(data[0]['name'], "Radiator")
        self.assertEqual(data[1]['name'], "Grille")
        self.assertEqual(data[1]['price'], 65.0)
    
    ##====================== Retrieve Specific Inventory Testcase =======================##

    def test_get_specific_inventory_by_id_success(self):
        # Make GET request to the endpoint with inventory1_id
        response = self.client.get(f'/inventories/{self.inventory1_id}')

        print("Specific Inventory Response JSON:", response.json)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], self.inventory1_id)
        self.assertEqual(data['name'], "Radiator")
        self.assertEqual(data['price'], 50.0)

        # Negative Test: Retrieve inventory by Invalid ID (404 Case) #
    def test_get_specific_inventory_by_id_not_found(self):
        # Use an ID that does not exist, e.g., 333
        response = self.client.get('/inventories/333')

        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)
        self.assertEqual(data['error'], "Inventory id is not found.")
    
    ##======================= Update Specific Inventory details Testcase===================##

    def test_update_inventory_success(self):
        inventory_id=self.inventory1_id
        update_inventory_payload={
            "name": "Fenders front side",
            "price": 6000.0,
        }

        response = self.client.put(f'/inventories/{inventory_id}',json = update_inventory_payload)

        print("Update Success Response:", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Message",response.json)
        self.assertEqual(response.json['Inventory']['name'],'Fenders front side')
        self.assertEqual(response.json['Message'],f'Successfully Updated Inventory id: {inventory_id}')
        self.assertEqual(response.json['Inventory']['price'],update_inventory_payload['price'])

        ## Negative Test: Update inventory by Invalid ID (404 Case) ##
    def test_update_inventory_not_found(self):
        updated_data = {"name": "Part", "price": 999.0}

        response = self.client.put('/inventories/22', json=updated_data)

        data = response.get_json()
        print("DEBUG: response data:", data)

        self.assertEqual(response.status_code, 404)
        self.assertIsNotNone(data)
        self.assertIn("error", data)
        self.assertEqual(data['error'], "Inventory id is not found.")

    ##======================= Delete Specific Inventory details Testcase =====================##
    def test_delete_inventory_success(self):
        inventory_id=self.inventory2_id
        
        response = self.client.delete(f'/inventories/{inventory_id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("successfully deleted", response.json['message'])
        self.assertEqual(response.json['message'], f'Inventory id: {inventory_id}, successfully deleted.')

            ## Check if it's really deleted ##
        get_response = self.client.get(f'/inventories/{inventory_id}')
        self.assertEqual(get_response.status_code, 404)

            ## Negative Test: Delete inventory by Invalid ID (404 Case) ##
    def test_delete_inventory_not_found(self):
            
        response = self.client.delete('/inventories/999')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], "Inventory not found.")


    if __name__ == '__main__':
        unittest.main()
