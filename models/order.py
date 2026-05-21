from datetime import datetime
from extensions import db


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.String(20), nullable=False, default="LOW")


    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "product": self.product,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat(),
            "priority": self.priority
        }