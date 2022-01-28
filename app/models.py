from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import jsonify
import enum


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class NDS(enum.Enum):
    nds0 = 0
    nds10 = 10
    nds18 = 18
    nds20 = 20


class TypePost(enum.Enum):
    promotion = 'Акция'
    news = 'Новость'


class ItemCatalog:
    def __init__(self, id=0, name='', article='', producer='', nds=NDS.nds0, balance=0.0, price=0.0, quantity=0.0, sum=0.0):
        self.id = id
        self.name = name
        self.article = article
        self.producer = producer
        self.nds = nds
        self.balance = balance
        self.price = price
        self.quantity = quantity
        self.sum = sum


product_info_table = db.Table('product_info', db.metadata,
                              db.Column('id', db.Integer, primary_key=True),
                              db.Column('product_id', db.Integer, db.ForeignKey(
                                  'product.id', ondelete='CASCADE', onupdate='CASCADE')),
                              db.Column('description', db.String(1000)))


posts = db.Table('posts', db.metadata,
                 db.Column('id', db.Integer,
                           autoincrement=True, nullable=False),
                 db.Column('name', db.String(250)),
                 db.Column('description', db.String(1000)),
                 db.Column('author', db.String(150)),
                 db.Column('type_post', db.Enum(TypePost)),
                 db.Column('timestamp', db.DateTime, default=datetime.utcnow)
                 )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(25), unique=True)
    password_hash = db.Column(db.String(128))
    active = db.Column(db.Boolean, default=False)
    profile = db.relationship('Profile', backref='parent', lazy='dynamic')

    def __repr__(self):
        return 'User <%s>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Contract(UserMixin, db.Model):
    __tablename__ = "contracts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    ref_1c = db.Column(db.String(36))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete='CASCADE', onupdate='CASCADE'))
    consignees = db.relationship('Consignee', backref='parent', lazy='dynamic')
    price = db.relationship('Price', backref='parent', lazy='dynamic')
    cart = db.relationship('Cart', backref='parent', lazy='dynamic')
    orders = db.relationship('Order', backref='parent', lazy='dynamic')
    data = db.Column(db.JSON)

    @staticmethod
    def update(profile, new_value={}):
        Profile.query.filter_by(id=profile.id).update(new_value)
        db.session.commit()


class Price(db.Model):
    __tablename__ = 'prices'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    balance = db.Column(db.Float)
    price = db.Column(db.Float)
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profiles.id', ondelete='CASCADE', onupdate='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id', ondelete='CASCADE', onupdate='CASCADE'))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref_1c = db.Column(db.String(36))
    name = db.Column(db.String(250))
    nds = db.Column(db.Enum(NDS))
    article = db.Column(db.String(25))
    producer = db.Column(db.String(150))
    category = db.Column(db.String(150))
    contract = db.Column(db.Integer, db.ForeignKey(
        'contracts.id', ondelete='CASCADE', onupdate='CASCADE'))
    cart = db.relationship('Cart', backref='product', lazy='dynamic')

    def __repr__(self):
        return """id: %s\nname: %s\nnds: %d""" % (self.id, self.name, self.nds.value)

    def product_info(self):
        conn = db.engine.connect()
        info = conn.execute(db.select([product_info_table.c.description]).where(
            product_info_table.c.product_id == self.id)).first()
        conn.close()

        row = {}
        row['name'] = self.name
        if info:
            row['description'] = info[0]
        else:
            row['description'] = ""

        return jsonify(row)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    ref_1c = db.Column(db.String(36))
    date = db.Column(db.DateTime, default=datetime.utcnow)
    delivery_date = db.Column(db.Date)
    sum = db.Column(db.Float)
    status = db.Column(db.String(25))
    comment = db.Column(db.String(500))
    addr_id = db.Column(db.Integer, db.ForeignKey(
        'consignees.id', ondelete='CASCADE', onupdate='CASCADE'))
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profiles.id', ondelete='CASCADE', onupdate='CASCADE'))
    items = db.relationship('ItemsOrder', backref='order', lazy='dynamic')

    @staticmethod
    def update(order_id, new_value={}):
        Order.query.filter_by(id=order_id).update(new_value)
        db.session.commit()

    @staticmethod
    def add(profile, form_data):
        order = Order()
        order.delivery_date = form_data.get('delivery_date')
        order.addr_id = int(form_data.get('consignee'))
        order.comment = form_data.get('comment')
        order.profile_id = profile.id
        order.status = "Новый"

        cart = profile.cart.all()
        total = 0
        for item in cart:
            item_order = ItemsOrder(product_id=item.product_id, nds=item.nds, sum=round(item.count * item.price, 2),
                                    sum_nds=round((item.price * (item.nds.value / 100)) * item.count, 2), quantity=item.count, price=item.price, order=order)
            total += item_order.sum
            db.session.add(item_order)

        order.sum = total
        db.session.add(order)

    @staticmethod
    def rejected(order_id):
        curr_order = Order.query.get(order_id)
        db.session.delete(curr_order)
        db.session.commit()


class ItemsOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'orders.id', ondelete='CASCADE', onupdate='CASCADE'))
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id', ondelete='CASCADE', onupdate='CASCADE'))
    nds = db.Column(db.Enum(NDS))
    quantity = db.Column(db.Float)
    price = db.Column(db.Float)
    sum = db.Column(db.Float)
    sum_nds = db.Column(db.Float)


class Consignee(db.Model):
    __tablename__ = 'consignees'
    id = db.Column(db.Integer, primary_key=True)
    ref_1c = db.Column(db.String(36))
    name = db.Column(db.String(500))
    profile_id = db.Column(db.Integer, db.ForeignKey(
        'profiles.id', ondelete='CASCADE', onupdate='CASCADE'))
    orders = db.relationship('Order', backref='orders', lazy='dynamic')

    def __repr__(self):
        return '%s' % (self.name)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_name = db.Column(db.String(250))
    nds = db.Column(db.Enum(NDS))
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))
    count = db.Column(db.Float)
    price = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def add(product, profile, count, price):
        cart = Cart(profile_id=profile.id, product_id=product.id, product_name=product.name, nds=product.nds,
                    count=count, price=price)
        db.session.add(cart)
        db.session.commit()

    @staticmethod
    def remove(product, profile):
        Cart.query.filter_by(product_id=product.id,
                             profile_id=profile.id).delete()
        db.session.commit()

    @staticmethod
    def update(product, profile, count, price):
        Cart.query.filter_by(product_id=product.id, profile_id=profile.id).update(
            {'count': count, 'price': price})
        db.session.commit()

    @staticmethod
    def exist(product, profile):
        return Cart.query.filter_by(product_id=product.id, profile_id=profile.id).count() > 0

    @staticmethod
    def clear(profile):
        Cart.query.filter_by(parent=profile).delete()
        db.session.commit()

    def __repr__(self):
        return """Product ID: %s\nUser ID: %s'\nCount: %d""" % (self.product_id, self.profile_id, self.count)
