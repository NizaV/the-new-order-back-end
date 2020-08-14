from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

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

class VendorInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    business_name =db.Column(db.String(100), nullable=False)
    vendor_full_name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(50), unique=True, nullable=False)
    phone=db.Column(db.String(20), unique=True, nullable=False)
    orders=db.Column(db.String(1000))

    def__ref__(self):
        return '<VendorInfo %r>'%self.info

    def serialize(self):
        return{
            "id":self.id,
            "business_name":self.id,
            "vendor_full_name":self.id,
            "email":self.id,
            "phone":self.id,
            "orders":self.id,
        }
    
class MenuItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    menu_item=db.Column(db.String(100), nullable=False)
    price=db.Column(db.decimal(25), nullable=False)
    description=db.Column(db.String(50), unique=True, nullable=False)
    photo=db.Column(db.String(20), unique=True, nullable=False)
    
def__ref__(self):
        return '<MenuItems %r>'%self.menu

    def serialize(self):
        return{
            "id":self.id,
            "menu":self.id,
            "price":self.id,
            "description":self.id,
            "photo":self.id,
        }
