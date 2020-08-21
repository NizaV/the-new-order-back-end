from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    orders = db.Column(db.String(1000))
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    orders = db.relationship('Order', backref='vendor', lazy=True)

    def __init__(self, vendor_name, email, password, phone, orders):
        self.vendor_name = vendor_name
        self.email = email
        self.password = password
        self.phone = phone
        self.orders = orders
        self.is_active = True

    def __repr__(self):
        return '<Vendor %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "vendor_name": self.vendor_name,
            "email": self.email,
            "phone": self.phone,
            "orders": self.phone
            # do not serialize the password, its a security breach
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=False)
    cancel_order = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=False)
    expected_pickup = db.Column(db.DateTime, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    sub_total_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    def __init__(self, name, email, phone, created_at, started_at, cancel_order, close_at, expected_pickup, vendor_id, sub_total_price, total_price):
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = created_at
        self.started_at = started_at
        #sub_total_price = None ???

class VendorLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    
    def __repr__(self):
        return '<VendorLogin %r>' % self.username 

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            
        }
    
class MenuItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item=db.Column(db.String(100), nullable=False)
    price=db.Column(db.Float(25), nullable=False)
    description=db.Column(db.String(50), unique=True, nullable=False)
    photo=db.Column(db.String(20), unique=True, nullable=False)
    
    def __ref__(self):
         return '<MenuItems %r>'%self.menu

    def serialize(self):
        return{
            "id":self.id,
            "menu":self.id,
            "price":self.id,
            "description":self.id,
            "photo":self.id,
        }
