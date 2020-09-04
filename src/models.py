from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    orders = db.relationship('Order', backref='vendor', lazy=True)
    location= db.relationship('Location', backref='vendor', uselist=False)
    products= db.relationship('Product', backref='vendor', lazy=True)
    
    def __init__(self, vendor_name, email, password, phone):
        self.vendor_name = vendor_name
        self.email = email
        self.password = password
        self.phone = phone
        self.is_active = True
    
    # products=[] #ask ernesto

    def __repr__(self):
        return '<Vendor %r>' % self.vendor

    def serialize(self):
        return {
            "id": self.id,
            "vendor_name": self.vendor_name,
            "email": self.email,
            "phone": self.phone,
            "orders": self.orders,
            "products": list(map(lambda x:x.serialize(), self.products))
            # do not serialize the password, its a security breach
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id=db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id=db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    unit_price=db.Column(db.Float(asdecimal=True), nullable=False)
    special_instructions=db.Column(db.String(1000), nullable=True)

    def __init__(self, order_id, Product_id, quantity, unit_price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
    
    def __ref__(self):
         return '<OrderItem %r>'%self.order_item

    def serialize(self):
        return{
            "id":self.id,
            "order_id":self.order_id,
            "product_id":self.produce_id,
            "quantity":self.quantity,
            "unit_price":self.unit_price,
        }

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    category=db.Column(db.String(1000), nullable=False)
    price=db.Column(db.Float(asdecimal=True), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    order_items=db.relationship('OrderItem', backref='product', lazy=True)
    description=db.Column(db.String(1000), nullable=False)
    def __init__(self, name, category, price, description, vendor_id):
        self.name = name
        self.category = category
        self.price=price
        self.vendor_id= vendor_id
        self.description= description
    # vendor= Product('Burger', 'Main', 5.99, 1) #ask ernesto
    
    def __ref__(self):
         return '<OrderItems %r>'%self.product

    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "category":self.category,
            "price": "{:.2}".format(self.price),
            "description":self.description,
            "vendor_id":self.vendor_id,
        }


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id=db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    total_price=db.Column(db.Float(asdecimal=True), nullable=False)
    payment_date=db.Column(db.DateTime(timezone=True), nullable=False)
    payment_type=db.Column(db.String(20), nullable=False)

    def __init__(self, order_id, total_price, payment_date, payment_type):
        self.order_id = order_id
        self.total_price = total_price
        self.payment_date=payment_date
        self.payment_type=payment_type
    
    def __ref__(self):
         return '<Payment %r>'%self.payment

    def serialize(self):
        return{
            "id":self.id,
            "order_id":self.order_id,
            "total_price":self.total_price,
            "payment_date":self.payment_date,
            "payment_type":self.payment_type,
        }

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    longitude=db.Column(db.String(16), nullable=False)
    latitude=db.Column(db.String(16), nullable=False)
    vendor_id=db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    is_open=db.Column(db.Boolean(), nullable=False)

    def __init__(self, longitude, latitude, vendor_id, is_open):
        self.longitude = longitude
        self.latitude = latitude
        self.vendor_id=vendor_id
        self.is_open=is_open
    
    def __ref__(self):
         return '<Location %r>'%self.location

    def serialize(self):
        return{
            "id":self.id,
            "longitude":self.longitude,
            "latitude":self.latitude,
            "vendor_id":self.vendor_id,
            "is_open":self.is_open,
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    cancel_order = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    expected_pickup = db.Column(db.DateTime, nullable=False)
    sub_total_price = db.Column(db.Float(asdecimal=True), nullable=False)
    total_price = db.Column(db.Float(asdecimal=True), nullable=False)
    payment = db.relationship('Payment', backref='order', uselist=False) 
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

    def __init__(self, name, email, phone, created_at, started_at, cancel_order, close_at, expected_pickup, vendor_id, sub_total_price, total_price):
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = created_at
        self.started_at = started_at
        #sub_total_price = None ???

    def __ref__(self):
         return '<Order %r>'%self.order #What goes here? is .order right?

    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "email":self.email,
            "phone":self.phone,
            "created_at":self.created_at,
            "started_at":self.started_at,
            "cancel_order":self.cancel_order,
            "closed_at":self.closed_at,
            "expected_pickup":self.expected_pickup,
            "vendor_id":self.vendor_id,
            "sub_total_price":self.sub_total_price,
            "total_price":self.total_price,
            "order_items":list(map(lambda x:x.serialize(),self.order_items))
            
        }


