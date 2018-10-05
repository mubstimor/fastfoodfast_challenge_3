""" manages routes to the app. """
import datetime
from functools import wraps
from flask import request, jsonify
from environs import Env
from pprint import pprint
from flasgger import Swagger
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required,
                                get_jwt_identity, JWTManager,
                                verify_jwt_in_request)
from api import app
from api.order import Order
from api.user import User
from api.fooditem import FoodItem

app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "FastFoodFast API Documentation",
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE"),
        ('Access-Control-Allow-Credentials', "true"),
    ]
}
SWAGGER = Swagger(app)
ENV = Env()
ENV.read_env()
app.config['SECRET_KEY'] = ENV.str("JWT_SECRET_KEY")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
JWT = JWTManager(app)

ORDER = Order()
USER = User()
FOODITEM = FoodItem()

@app.route('/', methods=['GET'])
def index():
    """ route to index of the API. """
    return jsonify({'Home': 'Index of the API', "Docs":"/apidocs"})

@JWT.unauthorized_loader
def unauthorized_response(callback):
    """ responds to missing authorisation header. """
    return jsonify({
        'ok': False,
        'message': 'Missing Authorization Header'
    }), 401

def admin_token_required(_f):
    """ create token to protect admin only routes. """
    @wraps(_f)
    def decorated(*args, **kwargs):
        """ check role = admin in user token. """
        verify_jwt_in_request()
        claims = get_jwt_identity()
        if claims['role'] != 'Admin':
            return jsonify({"msg": "Admins only!"}), 403
        else:
            return _f(*args, **kwargs)
    return decorated

@app.route('/api/v1/users/orders', methods=['POST'])
@jwt_required
def create_order():
    """
        Create a new order
        Allows a customer post an order
        ---
        tags:
          - ORDER
        parameters:
          - in: body
            item: body
            quantity: body
            schema:
              id: Order
              required:
                - item
                - quantity
              properties:
                item:
                  type: string
                  description: ordered item
                  default: Chips
                quantity:
                  type: integer
                  description: number of items requested
                  default: 1
        responses:
          201:
            description: New order created
        """
    if not request.json or not 'item' in request.json:
        return jsonify({'error': 'Missing Item parameter in request'}), 400
    try:
        request.json['quantity'] = int(request.json['quantity'])
        # request.json['user_id'] = int(request.json['user_id'])
    except ValueError:
        return jsonify({'error': 'Bad request'}), 400

    current_user = get_jwt_identity()
    logged_in_user = current_user['id']
    # if current_user['id'] != request.json['user_id']:
    #     return jsonify({'error': True, "message":"Forbidden request"}), 403

    order = ORDER.check_if_order_exists(logged_in_user , \
                                        request.json['item'], request.json['quantity'])
    if order:
        return jsonify({'error': 'Order already exists'}), 409
    else:
        create_user_order = ORDER.create_order(logged_in_user, request.json)
        if create_user_order:
            return jsonify({"message":"Order successfully created",
                            'id': create_user_order}), 201
        else:
            return jsonify({'error': True, "message":"Unable to support request"}), 400


@app.route('/api/v1/orders', methods=['GET'])
@admin_token_required
def get_all_orders():
    """
    Endpoint for returning list of orders
    ---
    tags:
      - ORDER

    responses:
      200:
        description: All available orders
    """
    orders = ORDER.fetch_all_orders()
    if orders:
        return jsonify({'orders': orders})
    else:
        return jsonify({'orders': "No orders available"})
  
@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
@admin_token_required
def get_order(order_id):
    """
    Get single order
    ---
    tags:
      - ORDER
    produces:
      - application/json
    parameters:
      - in: path
        name: order_id
        type: int
        description: order_id to be retrieved
        required: false
    responses:
      200:
        description: The requested order
    """
    order = ORDER.get_order(order_id)
    if order:
        return jsonify({'order': order})
    else:
        return jsonify({'order': 'Order not found'}), 404
  
@app.route('/api/v1/orders/<int:order_id>', methods=['PUT'])
@admin_token_required
def update_order(order_id):
    """
        Update a single order's status
        ---
        tags:
          - ORDER
        parameters:
          - in: body
            status: body
            schema:
              id: Order
          - in: path
            name: order_id
            required: false
            description: The ID of the order, try 1!
            type: string
        responses:
          200:
            description: The order has been updated
            # schema:
            #   id: Order
        """
    status = ("processing", "cancelled", "complete")
    if request.json['status'] not in status:
        return jsonify({'error': 'Missing status parameter in request'}), 400
    return jsonify({'order': ORDER.update_order(order_id, request.json)})

@app.route('/api/v1/orders/<int:order_id>', methods=['DELETE'])
@admin_token_required
def delete_order(order_id):
    """ delete requested resource from list. """
    return jsonify({'result': ORDER.delete_order(order_id)})

@app.route('/api/v1/auth/signup', methods=['POST'])
def create_user():
    """
        Register a new user
        ---
        tags:
          - User
        parameters:
          - in: body
            name: body
            email: body
            password: body
            gender: body
            user_type: body
            schema:
              id: User
              required:
                - name
                - email
                - password
                - gender
              properties:
                name:
                    type: string
                    description: user identifer
                email:
                    type: string
                    description: email address of user
                password:
                    type: string
                    description: secret key known to user
                gender:
                    type: string
                    description: either male or female
                user_type:
                    type: string
                    description: class of the user
                    default: Customer
        responses:
          201:
            description: New user created
    """
    gender = ('male', 'female')
    if not request.json or not 'email' in request.json:
        return jsonify({'error': True, "message": "Add 'email' parameter to reuest"}), 400
    if request.json['gender'] not in gender:
        return jsonify({'error': True, "message": "Add 'gender' parameter to reuest"}), 400

    user = USER.check_if_user_exists(request.json['email'])
    if user:
        return jsonify({'error': 'user already exists'}), 409
    else:
        try:
            post_user = USER.create_user(request.json)
        except KeyError:
            return jsonify({'error': True, "message": "Missing/Invalid parameters in request"}), 400
        return jsonify({'user': post_user, "message": "User successfully created."}), 201

@app.route('/api/v1/users', methods=['GET'])
def get_all_users():
    """ A route to return all of the available users. """
    return jsonify({'users': USER.fetch_all_users()})

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """ Get a specific user with given id."""
    user = USER.get_user(user_id)
    return jsonify({'user': user})

@app.route('/api/v1/auth/login', methods=['POST'])
def auth_user():
    """
        Authenticate user
        ---
        tags:
          - User
        parameters:
          - in: body
            name: body
            required: true
            type: string
            description: sign in a registered user
            
            schema:
              id: Auth
              properties:
                email:
                    type: string
                    description: email address of user
                password:
                    type: string
                    description: secret key known to user
        responses:
          200:
            description: Login successful
    """
    pprint(request.json)
    if not request.json or not 'password' in request.json:
        return jsonify({'error': 'Missing password parameter in request'}), 400
    access_token = ""
    data = USER.authenticate(request.json)
    if data:
        access_token = create_access_token(identity=data)
        user = {}
        user['token'] = access_token
        return jsonify({'ok': True, 'data': user}), 200
    else:
        return jsonify({'ok': False, 'message': 'invalid username or password'}), 401

@app.route('/api/v1/users/orders/<int:order_id>', methods=['PUT'])
def update_user_order(order_id):
    """ update order details with put request. """
    return jsonify({'order': ORDER.update_user_order(order_id, request.json)})

@app.route('/api/v1/users/orders', methods=['GET'])
@jwt_required
def get_user_orders():
    """
    Get orders for a specific user.
    ---
    tags:
      - ORDER
    produces:
      - application/json
    responses:
      200:
        description: Displays a users order history
    security:
        -JWT:
            descript: send token
            type: apiKey
            scheme: bearer
            name: access-token
            in: header
            bearerFormat: JWT
    """
    current_user = get_jwt_identity()
    get_orders = ORDER.fetch_user_orders(current_user['id'])
    if get_user_orders:
        return jsonify({'myorders': get_orders})
    else:
        return jsonify({"message":"no orders available for current user"})

@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def elevate_user_to_admin(user_id):
    """ update user to admin. """
    status = USER.assign_admin_privileges(user_id)
    return jsonify(status)

@app.route('/api/v1/users/admin/<string:email>', methods=['GET'])
def get_user_data(email):
    """ Get orders for a specific user."""
    data = USER.get_user_data_from(email)
    return jsonify(data)

@app.route('/api/v1/menu', methods=['POST'])
@admin_token_required
def create_fooditem():
    """
        Create a new menu item
        Allows an admin to post a food item
        ---
        tags:
          - MENU
        securityDefinitions:
            bearerAuth:
                type: bearer
        parameters:
          - in: body
            name: body
            category: body
            price: body
            schema:
              id: Menu
              required:
                - name
                - category
                - price
              properties:
                name:
                    type: string
                    description: description of food item
                    default: 1
                category:
                    type: string
                    description: class to which the item belongs
                    default: Foods
                price:
                    type: integer
                    description: monetary worth of item
                    default: 3000
        responses:
          201:
            description: New order created
        # openapi: 3.0.0
        components:
            securitySchemes:
                bearerAuth:
                    type: apiKey
                    scheme: bearer
                    in: header
                    bearerFormat: JWT
        security:
            - bearerAuth: []            
    """
    try:
        request.json['price'] = int(request.json['price'])
    except ValueError:
        return jsonify({'error': 'Invalid price value'}), 400

    item = FOODITEM.check_if_item_exists(request.json['name'])
    if item:
        return jsonify({'error': 'Menu Item already exists'}), 409
    else:
        return jsonify({'fooditem': FOODITEM.create_item(request.json)}), 201

@app.route('/api/v1/menu', methods=['GET'])
def get_all_fooditems():
    """
    Get available menu
    ---
    tags:
      - MENU
    produces:
      - application/json
    responses:
      200:
        description: Displays a list of available menu item
    """
    return jsonify({'menu': FOODITEM.fetch_all_fooditems()})

@app.route('/api/v1/menu/<int:item_id>', methods=['GET'])
def get_fooditem(item_id):
    """
    Get single menu item
    ---
    tags:
      - MENU
    produces:
      - application/json
    parameters:
      - in: path
        name: item_id
        type: int
        description: item_id to be retrieved
        required: false
    responses:
      200:
        description: The requested menu item
    """
    item = FOODITEM.get_item(item_id)
    return jsonify({'fooditem': item})

@app.route('/api/v1/menu/<int:item_id>', methods=['PUT'])
@admin_token_required
def update_fooditem(item_id):
    """ update food item with put request. """
    return jsonify({'fooditem': FOODITEM.update_item(item_id, request.json)})

@app.route('/api/v1/menu/<int:item_id>', methods=['DELETE'])
def delete_fooditem(item_id):
    """ delete requested resource from list. """
    return jsonify({'result': FOODITEM.delete_item(item_id)})

@app.route('/api/v1/protected', methods=['GET'])
@jwt_required
def protected():
    """"access identity of current user """
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200
