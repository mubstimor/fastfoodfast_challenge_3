""" TESTS FOR USER ROUTES"""
import unittest
from api import app
from api.database import DatabaseConnection

class UserViewTest(unittest.TestCase):
    """ class defines test methods."""

    def setUp(self):
        """ set default values for class. """
        self.app = app.test_client()
        self.db = DatabaseConnection()
        self.db.create_all_tables()
        self.app.testing = True
        self.user = {"name": "John Doe", "email": "john@example.com", "password": "1234", "gender":"male", "user_type":""}

    def test_create_user(self):
        """ test create user method """
        request = self.app.post('/api/v1/auth/signup', json=self.user)
        self.assertEqual(request.status_code, 201)
        self.assertEqual("john@example.com", request.json['user']['email'])

    def test_create_duplicate_user(self):
        """ test create duplicate user """
        request = self.app.post('/api/v1/auth/signup', json=self.user)
        request = self.app.post('/api/v1/auth/signup', json=self.user)
        self.assertEqual(request.status_code, 409)
        self.assertEqual("user already exists", request.json['error'])

    def test_create_user_without_email(self):
        """ test post method by not including email in request """
        del self.user['email']
        request = self.app.post('/api/v1/auth/signup', json=self.user)
        self.assertEqual(request.status_code, 400)

    def test_create_user_invalid_gender(self):
        """ test create user method by including a wrong value for gender """
        self.user['gender'] = "mammal"
        request = self.app.post('/api/v1/auth/signup', json=self.user)
        self.assertEqual(request.status_code, 400)

    def test_user_login(self):
        """ test user login method """
        request = self.app.post('/api/v1/auth/signup',
                                json={"name": "Jack Jones", "email": "jack@example.com",
                                      "password": "1234", "gender":"male", "user_type":""})
        request = self.app.post('/api/v1/auth/login', \
        json={"email": "jack@example.com", "password": "1234"})
        self.assertEqual(True, request.json['ok'])

    def test_invalid_user_password(self):
        """ test invalid user login password"""
        request = self.app.post('/api/v1/auth/signup',
                                json=self.user)
        request = self.app.post('/api/v1/auth/login',
                                json={"email": "john@example.com", "password": "12345"})
        self.assertEqual(False, request.json['ok'])

    def test_invalid_user_login_email(self):
        """ test invalid user login email"""
        request = self.app.post('/api/v1/auth/signup',
                                json=self.user)
        request = self.app.post('/api/v1/auth/login', \
        json={"email": "john@example.com", "password": "12345"})
        self.assertEqual(False, request.json['ok'])

    def test_user_login_no_password(self):
        """ test login method by not including password in request """
        request = self.app.post('/api/v1/auth/login',
                                json={"email": "mubstimor@gmail.com"})
        self.assertEqual(request.status_code, 400)

    def test_get_user(self):
        """ test get user method """
        request = self.app.post('/api/v1/auth/signup',
                                json=self.user)
        created_user_id = int(request.json['user']['id'])
        user_url = "/api/v1/users/" + str(created_user_id)
        request = self.app.get(user_url)
        self.assertEqual(request.status_code, 200)

    def test_retrieve_unavailableuser(self):
        """ test fetch user method by passing an index that's not available """
        request = self.app.get('/api/v1/users/13')
        self.assertEqual("not found", request.json['user'])

    def test_get_all_users(self):
        """ test get user method """
        request = self.app.post('/api/v1/auth/signup',
                                json=self.user)
        request = self.app.get('/api/v1/users')
        self.assertEqual(request.status_code, 200)
        self.assertGreater(len(request.json['users']), 0)

    def tearDown(self):
        """ undo effects of tests. """
        self.db.drop_all_tables()
        self.db.close_connection()

if __name__ == "__main__":
    unittest.main()
