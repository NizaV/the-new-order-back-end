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
from models import db, Vendor
from flask_jwt_simple import JWTManager, create_jwt, get_jwt_identity, jwt_required
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# jwt_simple config
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET")  # Change this!
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
    if search_name is None:

        for vendor in vendors:
            payload.append(vendor.serialize())
        return jsonify(payload), 200
    else:
        filter_vendors=list(filter(lambda vendor: search_name in vendor.vendor_name.lower(), vendors))
        for vendor in filter_vendors:
            payload.append(vendor.serialize())
        return jsonify(payload), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
