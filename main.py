from app import app, db
from app.models import User, Product, Cart, Consignee, Order, ItemsOrder, Profile, Contract


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Product': Product, 'Cart': Cart,
            'Consignee': Consignee, 'Order': Order, 'ItemsOrder': ItemsOrder, 'Profile': Profile, 'Contract': Contract}
