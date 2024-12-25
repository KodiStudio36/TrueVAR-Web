from app.extensions import db

class ShopItem(db.Model):
    __tablename__ = 'shop_item'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    href = db.Column(db.Text)

    def __init__(self, name: str, cost: float, href: str=None):
        self.name = name
        self.cost = cost
        self.href = href

    def to_cart(self):
        return {"id": self.id, "name": self.name, "cost": self.cost}