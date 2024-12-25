from flask import render_template, request, session, jsonify
from app.cart import bp

from app.models.shop_item import ShopItem

@bp.route('/')
def index():
    # items: ShopItem = ShopItem.query.filter_by(id=idx).first()

    # type('Obj', (object,), {k: v for k, v in dict_example.items()})()
    # obj = json.loads(json.dumps(dict_example), object_hook=lambda d: SimpleNamespace(**d))

    cart = list()

    # convert json cart to object
    for item in session["cart"].values():
        cart.append(type('Obj', (object,), {k: v for k, v in item.items()})())

    return render_template('cart/index.html', cart=cart)

@bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    try:
        product_id = request.get_json(force=True)["id"]
        print(product_id)

        # Initialize cart in session if it doesn't exist
        if 'cart' not in session:
            session['cart'] = {}

        cart = session['cart']

        # Add or update product in cart
        if product_id in cart:
            cart[product_id]["quantity"] += 1
        else:
            item: ShopItem = ShopItem.query.filter_by(id=product_id).first()
            cart[product_id] = {**item.to_cart(), "quantity": 1}

        session['cart'] = cart
        print(session['cart'])
        return jsonify({"message": "ok"})
    except:
        return jsonify({"error": "Incorrect request format"}), 401