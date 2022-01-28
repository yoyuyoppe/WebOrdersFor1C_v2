# -*- coding: utf-8 -*-
from app import app, db
from sqlalchemy import or_, func, and_, join, outerjoin
from app.forms import LoginForm, RegistrationForm, FormOrder, FormProfile
from app.models import User, Product, Cart, ItemCatalog, NDS, Consignee, Order, ItemsOrder, Price, Profile, Contract
from flask import render_template, flash, redirect, url_for, flash, request, jsonify, json, make_response
from flask_login import current_user, login_user, logout_user, login_required


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = current_user.profile.filter_by(user_id=current_user.id).first()
    if profile:
        user = User.query.get(profile.user_id)
        consignees = profile.consignees.all()
        contracts = Contract.query.all()
        form = FormProfile()
        row = 0
        for consignee in consignees:
            row += 1
            form.consignee.choices.append((row, consignee.name))
        row = 0
        for contract in contracts:
            row += 1
            form.contracts.choices.append((row, contract.name))   

        if request.method == 'GET':
            form.name.data = profile.name
            form.email.data = profile.data.get('email', user.email)
            form.phone.data = profile.data.get('phone', user.phone)
            form.inn.data = profile.data.get('inn', '')
            form.kpp.data = profile.data.get('kpp', '')
            form.catalog_exp.data = profile.data.get('catalog_exp', '')

            file_type_exp = profile.data.get('file_type_exp', '')

            if file_type_exp == '':
                form.file_type_exp.choices = app.config.get(
                    'FILE_TYPE_EXP', [])
            else:
                if app.config.get('FILE_TYPE_EXP') and file_type_exp and len(app.config['FILE_TYPE_EXP']) >= int(file_type_exp):
                    form.file_type_exp.choices.append(
                        app.config['FILE_TYPE_EXP'][int(file_type_exp) - 1])
                row = 1
                for file_type in app.config.get('FILE_TYPE_EXP'):
                    if file_type not in form.file_type_exp.choices:
                        form.file_type_exp.choices.append(file_type)

        else:
            profile.data['email'] = form.email.data
            profile.data['phone'] = form.phone.data
            profile.data['inn'] = form.inn.data
            profile.data['kpp'] = form.kpp.data
            profile.data['catalog_exp'] = form.catalog_exp.data
            profile.data['file_type_exp'] = form.file_type_exp.data

            Profile.update(profile, {'data': profile.data})

        return render_template('profile.html', form=form, title='Профиль')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Не верный пользователь или пароль', 'danger')
            return redirect(url_for('index'))
        if user.active:
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        else:
            flash('Пользователь не подтвержден', 'danger')
    return render_template('index.html', title='Главная', form=form)


@app.route('/catalog')
@login_required
def catalog():
    catalog = []
    profile = current_user.profile.filter_by(user_id=current_user.id).first()
    q = request.args.get('q')
    if profile:
        query = db.session.query(Product.id, Product.name, func.ifnull(Product.article, ''), func.ifnull(Product.producer, ''),
                                 Product.nds, Price.price, func.ifnull(Cart.count, ''), Price.balance).\
            join(Price, Product.id == Price.product_id).outerjoin(Cart, and_(Product.id == Cart.product_id, Cart.profile_id ==
                                                                             profile.id)).filter(Price.profile_id == profile.id)

        if q:
            query = query.filter(Product.name.contains(
                q) | Product.article.contains(q) | Product.producer.contains(q))

        res = query.all()

        catalog = [{'id': id, 'name': name, 'article': article,
                    'producer': producer, 'nds': nds.value, 'price': price,
                    'quantity': qty, 'balance': balance} for id, name, article, producer, nds, price, qty, balance in res]

    return render_template('catalog.html', title='Каталог', products=catalog, profile=profile)


@app.route('/catalog/curr_product/info')
@login_required
def product_description():
    product_id = request.args.get('product_id')
    product = Product.query.get(int(product_id))
    if product:
        return product.product_info()


@app.route('/orders/order/new', methods=['GET', 'POST'])
@login_required
def new_order():
    form = FormOrder()
    profile = current_user.profile.filter_by(user_id=current_user.id).first()
    title = 'Новый заказ'
    total = 0
    if profile:
        consignees = profile.consignees.all()
        if request.args.get('cart'):
            cart = json.loads(request.args.get('cart'))
        elif request.form.get('submit_order'):
            cart = json.loads(request.form.get('submit_order'))
        else:
            cart = []

        for item in cart:
            product = Product.query.get(int(item['id']))
            if Cart.exist(product, profile):
                Cart.update(product, profile, item['qty'], item['price'])
            else:
                Cart.add(product, profile, item['qty'], item['price'])

        products = profile.cart.all()

        for item in products:
            total += round(item.count * item.price, 2)

        if len(products) == 0:
            return redirect(url_for('catalog'))

        row = 0
        for consignee in consignees:
            row += 1
            form.consignee.choices.append((row, consignee.name))

        if request.method == 'POST':
            Order.add(profile, form.data)
            Cart.clear(profile)
            return redirect(url_for('orders'))

        return render_template('new_order.html', title=title, form=form, products=products, profile=profile, total=total)


@app.route('/orders/order/<int:id_order>', methods=['GET', 'POST'])
@login_required
def order(id_order):
    form = FormOrder()
    profile = current_user.profile.filter_by(user_id=current_user.id).first()
    title = 'Заказ %s' % id_order
    if request.args.get('rejected'):
        Order.update(id_order, {'status': "Отклонен"})
        return redirect(url_for('orders'))
    if profile:
        curr_order = Order.query.get(id_order)

        if curr_order is None:
            flash('Заказ №%s не найден!!!' % id_order)
            return redirect(url_for('orders'))

        consignee = profile.consignees.filter_by(id=curr_order.addr_id).first()
        items_order = db.session.query(ItemsOrder.product_id, Product.name,
                                       ItemsOrder.nds, ItemsOrder.price, ItemsOrder.quantity, ItemsOrder.sum).\
            join(Product, ItemsOrder.product_id == Product.id).filter(
            ItemsOrder.order_id == curr_order.id).all()

        products = [{'id': id, 'name': name, 'nds': nds.value, 'price': price,
                     'quantity': qty, 'sum': sum} for id, name, nds, price, qty, sum in items_order]

        form.consignee.choices.append((1, consignee.name))
        form.delivery_date.data = curr_order.delivery_date
        form.comment.data = curr_order.comment
    return render_template('order.html', title=title, form=form, products=products, profile=profile, id_order=id_order, total=curr_order.sum)


@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    profile = current_user.profile.filter_by(user_id=current_user.id).first()
    query = profile.orders.join(Consignee, Order.addr_id == Consignee.id)
    q = request.args.get('q')
    if q:
        query = query.filter(Order.id.contains(
            q) | Order.status.contains(q) | Consignee.name.contains(q))
    return render_template('orders.html', title='Заказы', orders=query.all(), Consignee=Consignee)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, регистрация прошла успешно', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
