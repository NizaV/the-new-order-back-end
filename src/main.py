"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Vendor, Product, Order, OrderItem
from flask_jwt_simple import JWTManager, create_jwt, get_jwt_identity, jwt_required
#from models import Person
app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# jwt_simple config
app.config['JWT_SECRET_KEY'] = "soienfkf"  # Change this!
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code
# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)
@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200
@app.route('/signup', methods=['POST'])
def handle_signup():
    input_data = request.json
    if 'vendor_name' in input_data and 'email' in input_data and 'password' in input_data and 'phone' in input_data:
        new_vendor = Vendor(
            input_data['vendor_name'],
            input_data['email'],
            input_data['password'],
            input_data['phone']
        )
        db.session.add(new_vendor)
        try:
            db.session.commit()
            return jsonify(new_vendor.serialize()), 201
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "msg": error.args
            }), 500
    else:
        return jsonify({
            "msg": "check your keys..."
        }), 400
# Provide a method to create access tokens. The create_jwt()
# function is used to actually generate the token
@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    params = request.get_json()
    email = params.get('email', None)
    password = params.get('password', None)
    if not email:
        return jsonify({"msg": "Missing email parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400
    # vendor = Vendor.query.filter_by(email= email).one_or_none()
    # if vendor is None:
    #     return jsonify({"msg": "Email not found"}), 404
    # else:
    #     if password == vendor.password:
    #         return jsonify({
    #             token: create_jwt(identity=vendor.id),
    #             vendor: vendor.serialize()
    #         }), 200
    #     else: 
    #         return jsonify({"msg": "Bad email or password"}), 
    specific_vendor = Vendor.query.filter_by(
        email=email
    ).one_or_none()
    if isinstance(specific_vendor, Vendor):
        if specific_vendor.password == password:
            # oh, this person is who it claims to be!
            # Identity can be any data that is json serializable
            response = {'jwt': create_jwt(identity=specific_vendor.id), "vendor": specific_vendor.serialize()}
            return jsonify(response), 200
        else:
            return jsonify({
            "msg": "bad credentials"
        }), 400
    else:
        return jsonify({
            "msg": "bad credentials"
        }), 400
    # if username != 'test' or password != 'test':
    #     return jsonify({"msg": "Bad username or password"}), 401
@app.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    specific_vendor_id = get_jwt_identity()
    specific_vendor = Vendor.query.filter_by(
        id=specific_vendor_id
    ).one_or_none()
    # specific_user = User.query.get(specific_user_id)
    if specific_vendor is None:
        return jsonify({
            "msg": "user not found"
        }), 404
    else:
        return jsonify({
            "msg": "Yay! You sent your token correctly so I know who you are!",
            "vendor_data": specific_vendor.serialize()
        }), 200
    
@app.route('/vendors', methods=['GET'])
def handle_vendors():
    vendors=Vendor.query.filter_by(is_active=True).all()
    payload=[]
    search_name=request.args.get("name")
    print(search_name)
    if search_name is None:
        for vendor in vendors:
            payload.append(vendor.serialize())
        return jsonify(payload), 200
    else:
        filter_vendors=list(filter(lambda vendor: search_name in vendor.vendor_name.lower(), vendors))
        for vendor in filter_vendors:
            payload.append(vendor.serialize())
        return jsonify(payload), 200
# Item Add Edit Page
@app.route('/menu-items', methods=['GET', 'POST'])
@app.route('/menu-items/<item_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required
def menuItems(item_id=None):
    # Get All Menu Items
    specific_vendor_id = get_jwt_identity()
    if request.method=='GET':
        if item_id is None: 
            vendor_items = Product.query.filter_by(
                vendor_id=specific_vendor_id
            ).all()
            serialized_items=[]
            for item in vendor_items:
                serialized_items.append(item.serialize())
            return jsonify(serialized_items), 200
        else: 
            specific_item = Product.query.filter_by(id=item_id).one_or_none()
            return jsonify(specific_item.serialize()), 200
    elif request.method=='POST':
        body = request.get_json()
        item = Product(name=body['name'],category=body['category'], vendor_id=specific_vendor_id, price=body['price'], description=body['description'])
        db.session.add(item)
        db.session.commit()
        print(item)
        return jsonify(item.serialize()), 201
    elif request.method=='PUT':
        body = request.get_json()
        item = Product.query.get(item_id)
        if item is None:
            raise APIException('Menu item not found', status_code=404)
        if 'name' in body:
            item.name=body['name']
        if 'price' in body:
            item.price=body['price']
        if 'description' in body:
            item.description=body['description']
        if 'category' in body:
            item.category=body['category']
        db.session.commit()
        return jsonify(item.serialize()), 200
        
    elif request.method=='DELETE':
        item = Product.query.get(item_id)
        if item is None:
            raise APIException('Item not found', status_code=404)
        db.session.delete(item)
        db.session.commit()
        return jsonify({}), 204
@app.route('/vendor/<int:vendor_id>', methods=['PUT', 'GET', 'DELETE'])
def get_single_vendor(vendor_id):
    """
    Single vendor
    """
    
            
    # GET request
    if request.method == 'GET':
        user1 = Vendor.query.filter_by(
                id=vendor_id
            ).first()
        print("****", user1)    
        if user1 is None:
            raise APIException('Vendor not found', status_code=404)
        return jsonify(user1.serialize()), 200
    return "Invalid Method", 404
#Admin Main Menu Page
@app.route('/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.all() #way to get all the orders
    seri_orders= []
    for order in orders:
        seri_orders.append(order.serialize())
    print(orders)
    return jsonify(seri_orders), 200
    # this only runs if `$ python src/main.py` is executed


#User Main Menu and Send Order
@app.route('/vendor-public-menu/<int:vendor_id>', methods=['GET'])
def get_public_menu(vendor_id):
    products = Product.query.filter_by(vendor_id = vendor_id).all()
    seri_products = []
    for product in products:
        seri_products.append(product.serialize())
    print(seri_products)
    return jsonify(seri_products), 200

@app.route('/create-order', methods=['POST'])
def create_order():
    input_data = request.json
   
    if 'name' in input_data and 'email' in input_data and 'phone' in input_data:
        new_order = Order(
            name = input_data['name'],
            email = input_data['email'],
            phone = input_data['phone'],
            sub_total_price = input_data['sub_total_price'],
            total_price = input_data['total_price'],
            expected_pickup = input_data['expected_pickup'],
            vendor_id = input_data['vendor_id'],
            started_at = None,
            cancel_order = None,
            closed_at = None,
            created_at = None
        )
        db.session.add(new_order)
        try:
            db.session.commit()
            return jsonify(new_order.serialize()), 201
        except Exception as error:
            db.session.rollback()
            return jsonify({
                "msg": error.args
            }), 500
    else:
        return jsonify({
            "msg": "order not processed"
        }), 400

@app.route('/order-item', methods=['POST', 'GET'])
def handle_order_item():
    # POST request
    if request.method == 'POST':
        body = request.get_json()
       
        user1 = OrderItem(order_id=body['order_id'], product_id=body['product_id'], quantity=body['quantity'], unit_price=body['unit_price'], special_instructions=body['special_instructions'])
        db.session.add(user1)
        db.session.commit()
        return "ok", 200
    # GET request
    if request.method == 'GET':
        all_people = OrderItem.query.all()
        all_people = list(map(lambda x: x.serialize(), all_people))
        return jsonify(all_people), 200
    return "Invalid Method", 404

# @app.route('/payment', methods=['POST'])
# def create_order(name, email, phone, sub_total_price, total_price, order_items):


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)