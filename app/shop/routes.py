from flask import render_template, redirect
from app.shop import bp

from app.models.shop_item import ShopItem

@bp.route('/')
def index():
    items = ShopItem.query.all()
    return render_template('shop/index.html', items=items)

@bp.route('/item/<idx>')
def item(idx):
    item: ShopItem = ShopItem.query.filter_by(id=idx).first()
    if item.href:
        return redirect(item.href)
    return render_template('shop/item.html', item=item)

@bp.route('/shopitem1')
def shopitem1():
    item = ShopItem.query.filter_by(id=1).first()
    return render_template('shop/item.html', item=item)

@bp.route('/shopitem3')
def shopitem3():
    item = ShopItem.query.filter_by(id=3).first()
    return render_template('shop/item.html', item=item)