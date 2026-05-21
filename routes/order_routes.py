from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.order import Order
import heapq

order_bp = Blueprint("order_bp", __name__)


def admin_required():

    claims = get_jwt()

    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    return None


# -------------------------
# CREATE ORDER
# -------------------------
@order_bp.route("/orders", methods=["POST"])
@jwt_required()
def create_order():
    """
    Create a new order
    ---
    security:
      - Bearer: []

    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            customer_name:
              type: string
            product:
              type: string
            quantity:
              type: integer
            priority:
              type: string
              enum:
                - HIGH
                - MEDIUM
                - LOW
    responses:
      201:
        description: Order created
    """

    admin_check = admin_required()

    if admin_check:
        return admin_check

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body cannot be empty"
        }), 400

    errors = []

    customer_name = data.get("customer_name")
    product = data.get("product")
    quantity = data.get("quantity")

    priority = data.get(
        "priority",
        "LOW"
    ).upper()

    valid_priorities = [
        "HIGH",
        "MEDIUM",
        "LOW"
    ]

    if not customer_name:
        errors.append(
            "Customer name is required"
        )

    if not product:
        errors.append(
            "Product name is required"
        )

    if (
        quantity is None
        or not isinstance(quantity, int)
        or quantity <= 0
    ):
        errors.append(
            "Quantity must be a positive integer"
        )

    if priority not in valid_priorities:
        errors.append(
            "Priority must be HIGH, MEDIUM or LOW"
        )

    if errors:
        return jsonify({
            "success": False,
            "message": "Validation failed",
            "errors": errors
        }), 400

    new_order = Order(
        customer_name=customer_name,
        product=product,
        quantity=quantity,
        priority=priority
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Order created successfully",
        "order": new_order.to_dict()
    }), 201


# -------------------------
# GET ALL ORDERS
# -------------------------
@order_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    """
    Get all orders
    ---
    security:
      - Bearer: []
    parameters:
      - name: customer_name
        in: query
        type: string

      - name: product
        in: query
        type: string

      - name: sort
        in: query
        type: string
        enum:
          - asc
          - desc

      - name: page
        in: query
        type: integer

      - name: limit
        in: query
        type: integer
    responses:
      200:
        description: List of orders
    """

    customer_name = request.args.get(
        "customer_name"
    )

    product = request.args.get(
        "product"
    )

    sort = request.args.get(
        "sort",
        "desc"
    )

    page = request.args.get(
        "page",
        1,
        type=int
    )

    limit = request.args.get(
        "limit",
        5,
        type=int
    )

    query = Order.query

    if customer_name:
        query = query.filter(
            Order.customer_name.ilike(
                f"%{customer_name}%"
            )
        )

    if product:
        query = query.filter(
            Order.product.ilike(
                f"%{product}%"
            )
        )

    if sort == "asc":
        query = query.order_by(
            Order.created_at.asc()
        )
    else:
        query = query.order_by(
            Order.created_at.desc()
        )

    paginated_orders = query.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )

    return jsonify({
        "success": True,
        "page": page,
        "limit": limit,
        "total_orders": paginated_orders.total,
        "total_pages": paginated_orders.pages,
        "orders": [
            order.to_dict()
            for order in paginated_orders.items
        ]
    }), 200

# -------------------------
# PROCESS ORDERS BY PRIORITY
# -------------------------
@order_bp.route(
    "/orders/process",
    methods=["GET"]
)
@jwt_required()
def process_orders():
    """
    Process orders by priority
    ---
    security:
      - Bearer: []
    responses:
      200:
        description: Orders processed successfully
    """

    orders = Order.query.all()

    priority_map = {
        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3
    }

    heap = []

    for order in orders:

        heapq.heappush(
            heap,
            (
                priority_map.get(
                    order.priority,
                    3
                ),
                order.created_at,
                order
            )
        )

    processed_orders = []

    while heap:

        _, _, order = heapq.heappop(heap)

        
        processed_orders.append({
            "id": order.id,
            "customer_name":
            order.customer_name,
            "product":
            order.product,
            "quantity":
            order.quantity,
            "priority":
            order.priority,
            "scheduled_by":
            "priority_queue"
        })

    return jsonify({
        "success": True,
        "total_processed":
        len(processed_orders),
        "processing_order":
        processed_orders
    }), 200

# -------------------------
# GET ORDER BY ID
# -------------------------
@order_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order_by_id(order_id):
    """
    Get order by ID
    ---
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        required: true
        type: integer

    responses:
      200:
        description: Order found

      404:
        description: Order not found
    """

    order = db.session.get(
        Order,
        order_id
    )

    if not order:
        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    return jsonify({
        "success": True,
        "order": order.to_dict()
    }), 200


# -------------------------
# UPDATE ORDER
# -------------------------
@order_bp.route("/orders/<int:order_id>", methods=["PUT"])
@jwt_required()
def update_order(order_id):
    """
    Update an order
    ---
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Order updated

      404:
        description: Order not found
    """

    admin_check = admin_required()

    if admin_check:
        return admin_check

    order = db.session.get(
        Order,
        order_id
    )

    if not order:
        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body cannot be empty"
        }), 400

    priority = data.get(
        "priority",
        order.priority
    ).upper()

    valid_priorities = [
        "HIGH",
        "MEDIUM",
        "LOW"
    ]

    if priority not in valid_priorities:
        return jsonify({
            "success": False,
            "message":
            "Priority must be HIGH, MEDIUM or LOW"
        }), 400

    order.customer_name = data.get(
        "customer_name",
        order.customer_name
    )

    order.product = data.get(
        "product",
        order.product
    )

    order.quantity = data.get(
        "quantity",
        order.quantity
    )

    order.priority = priority

    db.session.commit()

    return jsonify({
        "success": True,
        "message":
        "Order updated successfully",
        "order": order.to_dict()
    }), 200


# -------------------------
# DELETE ORDER
# -------------------------
@order_bp.route(
    "/orders/<int:order_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_order(order_id):
    """
    Delete an order
    ---
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        required: true
        type: integer

    responses:
      200:
        description: Order deleted

      404:
        description: Order not found
    """

    admin_check = admin_required()

    if admin_check:
        return admin_check

    order = db.session.get(
        Order,
        order_id
    )

    if not order:
        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    db.session.delete(order)
    db.session.commit()

    return jsonify({
        "success": True,
        "message":
        "Order deleted successfully"
    }), 200