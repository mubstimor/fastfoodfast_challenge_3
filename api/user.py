""" Class to manage CRUD operations on user objects"""
from werkzeug.security import generate_password_hash, check_password_hash
from api.database import DatabaseConnection

class User(object):
    """ docstring for User. """
    def __init__(self):
        """ define connections to food items table. """
        self.db = DatabaseConnection()
        self.db.create_all_tables()

    def create_user(self, user_data):
        """ add user to users table"""
        user = user_data
        user['name'] = str(user_data['name'])
        user['email'] = str(user_data['email'])
        user['gender'] = str(user_data['gender'])
        user['password'] = generate_password_hash(str(user_data['password']))
        user['user_type'] = str(user_data['user_type'])
        if not user['user_type']:
            user['user_type'] = 'Customer'
        self.db.cursor.execute("INSERT INTO users(name, email, password, gender, user_type) \
                                VALUES('"+ user['name'] + "','"+ user['email'] +"', '"+user['password']+"', '"+ \
                                user['gender']+"','"+user['user_type']+"') RETURNING id")
        user_id = self.db.cursor.fetchone()[0]
        del user['password']
        user['user_type'] = 'Customer'
        user['id'] = user_id
        return user

    def check_if_user_exists(self, email):
        """ retrieve item with similar email"""
        self.db.cursor.execute("SELECT * FROM users where email='"+email+"'")
        rows_found = self.db.cursor.rowcount
        if rows_found > 0:
            return True
        
    def get_user_data_from(self, email):
        """ retrieve user data with similar email"""
        self.db.cursor.execute("SELECT * FROM users where email='"+email+"'")
        useritem = self.db.cursor.fetchone()
        user = {"id": useritem['id'], "email": useritem['email'], "role": useritem['user_type']}
        return user

    def fetch_all_users(self):
        """ retrieve all users from db """
        self.db.cursor.execute("SELECT * FROM users")
        useritems = self.db.cursor.fetchall()
        users = []
        for item in useritems:
            user = {"id": item['id'], "email": item['email']}
            users.append(user)
        return users

    def get_user(self, user_id):
        """ retrieve user with given id"""
        self.db.cursor.execute("SELECT * FROM users where id='"+str(user_id)+"'")
        user_item = self.db.cursor.fetchone()
        rows_found = self.db.cursor.rowcount
        if rows_found > 0:
            user = {"id": user_item['id'], "email": user_item['email'], "role": user_item['user_type']}
            return user
        else:
            return "not found"

    def login(self, user_data):
        """ check user login """
        user = user_data
        user['email'] = str(user_data['email'])
        user['password'] = str(user_data['password'])
        self.db.cursor.execute("SELECT * FROM users where email='"+user['email']+"'")
        rows_found = self.db.cursor.rowcount
        if rows_found > 0:
            userdata = self.db.cursor.fetchone()
            login_status = check_password_hash(userdata['password'], user['password'])
            if login_status:
                return True
            else:
                return False
        else:
            return False

    def authenticate(self, user_data):
        """ check user login """
        user = user_data
        user['email'] = str(user_data['email'])
        user['password'] = str(user_data['password'])
        self.db.cursor.execute("SELECT * FROM users where email='"+user['email']+"'")
        rows_found = self.db.cursor.rowcount
        if rows_found > 0:
            userdata = self.db.cursor.fetchone()
            login_status = check_password_hash(userdata['password'], user['password'])
            if login_status:
                user = {"id": userdata['id'], "email": userdata['email'], "role": userdata['user_type']}
                return user
            
    def assign_admin_privileges(self, user_id):
        """ elevate user to admin """
        self.db.cursor.execute("UPDATE users set user_type='Admin' WHERE id='"+str(user_id)+"'")
        rows_updated = self.db.cursor.rowcount
        if rows_updated > 0:
            return {"error": False, "message":"user updated to admin"}
        else:
            return {"error": True, "message":"unable to elevate user to admin"}
        
