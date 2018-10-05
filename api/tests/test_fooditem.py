""" Test class for FoodItem"""
import unittest
from pprint import pprint
from api import app
from api.database import DatabaseConnection

class FoodItemViewTest(unittest.TestCase):
    """ class defines test methods."""

    def _set_up_admin_token(self):
        """ test admin token """
        request = self.app.post('/api/v1/auth/signup', \
        json={"name": "James Adkins", "email": "james@example.com", "password": "1234", "gender":"male", "user_type":"Admin"})
        request = self.app.post('/api/v1/auth/login', \
        json={"email": "james@example.com", "password": "1234"})
        admin_token = "Bearer " + str(request.json['data']['token'])
        return admin_token

    def setUp(self):
        """ set default values for class. """
        self.app = app.test_client()
        self.db = DatabaseConnection()
        self.db.create_all_tables()
        self.app.testing = True
        self.fooditem = {"name": "Millet", "category": "Foods", "price":7000}
        self.bearer_token = self._set_up_admin_token()

    def test_create_fooditem(self):
        """ test create food item """
        request = self.app.post('/api/v1/menu', json=self.fooditem, headers={"Authorization": self.bearer_token})
        self.assertEqual(request.status_code, 201)  
        self.assertEqual(request.headers['Content-Type'], 'application/json')
        self.assertEqual(7000, request.json['fooditem']['price'])
        self.assertEqual("Foods", request.json['fooditem']['category'])

    def test_create_duplicate_menuitem(self):
        """ test duplicate menu item """
        request = self.app.post('/api/v1/menu', json=self.fooditem, headers={"Authorization": self.bearer_token})
        request = self.app.post('/api/v1/menu', json=self.fooditem, headers={"Authorization": self.bearer_token})
        self.assertEqual(request.status_code, 409)
        self.assertEqual(request.headers['Content-Type'], 'application/json')
        self.assertEqual("Menu Item already exists", request.json['error'])

    def test_create_menuitem_with_invalid_price(self):
        """ test post method by including an invalid price value."""
        self.fooditem['price'] = "xada"
        request = self.app.post('/api/v1/menu', json=self.fooditem, headers={"Authorization": self.bearer_token})
        self.assertEqual(request.status_code, 400)

    def test_retrieve_menuitem(self):
        """ test fetch method """
        request = self.app.post('/api/v1/menu', \
        json={"name": "Chips", "category": "Foods", "price":6000}, headers={"Authorization": self.bearer_token})
        pprint(request.json)
        created_item_id = int(request.json['fooditem']['id'])
        request = self.app.get('/api/v1/menu/' + str(created_item_id))
        pprint(request.json)
        self.assertEqual(request.status_code, 200)
        self.assertEqual("Chips", request.json['fooditem']['name'])

    def test_retrieve_unavailablemenuitem(self):
        """ test fetch method by passing an index that's not available """
        request = self.app.get('/api/v1/menu/11')
        self.assertEqual("not found", request.json['fooditem'])

    def test_get_all_menuitems(self):
        """ test get all menuitems method """
        request = self.app.post('/api/v1/menu', \
        json={"name": "Chicken Wings", "category": "Foods", "price":18000}, headers={"Authorization": self.bearer_token})
        request = self.app.get('/api/v1/menu')
        self.assertEqual(request.status_code, 200)
        self.assertGreater(len(request.json['menu']), 0)

    def test_update_menuitem(self):
        """ test update food item """
        request = self.app.post('/api/v1/menu', \
        json={"name": "Liver", "category": "Foods", "price":8000}, headers={"Authorization": self.bearer_token})
        created_item_id = int(request.json['fooditem']['id'])
        item_url = "/api/v1/menu/" + str(created_item_id)
        request = self.app.put(item_url,
                               json={"name": "Fish Fillet",
                                     "category": "Foods", "price":9000}, 
                                headers={"Authorization": self.bearer_token})
        self.assertEqual(request.status_code, 200)
        self.assertEqual(9000, request.json['fooditem']['price'])

    def test_update_unavailablemenuitem(self):
        """ test update unavailable item """
        request = self.app.post('/api/v1/menu',
                                json={"name": "Chicken Nuggets",
                                      "category": "Foods", "price":12000},
                                headers={"Authorization": self.bearer_token})
        created_item_id = int(request.json['fooditem']['id']) + 3
        item_url = "/api/v1/menu/" + str(created_item_id)
        request = self.app.put(item_url,
                    json={"name": "Fish Fillet", "category": "Foods", "price":9000},
                    headers={"Authorization": self.bearer_token})
        self.assertEqual(request.status_code, 200)
        self.assertEqual("unable to update item", request.json['fooditem'])

    def test_delete_menuitem(self):
        """ test delete method """
        request = self.app.post('/api/v1/menu', \
        json={"name": "Hot Chocolate", "category": "Beverages", "price":8000}, headers={"Authorization": self.bearer_token})
        created_item_id = int(request.json['fooditem']['id'])
        item_url = "/api/v1/menu/" + str(created_item_id)
        request = self.app.delete(item_url, headers={"Authorization": self.bearer_token})
        self.assertEqual(request.status_code, 200)
        self.assertNotEqual("", request.json['result'])

    def test_delete_unavailable_menuitem(self):
        """ test delete method for an unavailable resource """
        request = self.app.delete('/api/v1/menu/14', headers={"Authorization": self.bearer_token})
        self.assertEqual("unable to delete item", request.json['result'])

    def tearDown(self):
        """ undo effects of tests. """
        self.db.drop_all_tables()
        self.db.close_connection()

if __name__ == "__main__":
    unittest.main()
