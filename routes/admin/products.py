"""
Admin Products Routes
CRUD for Products
"""
import uuid
import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from models import db, Product, AuditEvent
from ..decorators import admin_required

products_bp = Blueprint('admin_products', __name__, url_prefix='/products')


def log_audit(action, entity, entity_id, meta=None):
    try:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            actor='admin',
            action=action,
            entity=entity,
            entityId=entity_id,
            meta=json.dumps(meta) if meta else None
        )
        db.session.add(audit)
    except Exception as e:
        print(f"Audit log failed: {e}")


@products_bp.route('', methods=['GET'])
@admin_required
def get_products():
    """List all products with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category')
        status = request.args.get('status')

        query = Product.query

        if search:
            query = query.filter(
                (Product.name.ilike(f'%{search}%')) |
                (Product.description.ilike(f'%{search}%'))
            )
        if category:
            query = query.filter_by(category=category)
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)

        products = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'products': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': float(p.price) if p.price else 0,
                'category': p.category,
                'imageUrl': p.image_url,
                'isActive': p.is_active,
                'createdAt': p.created_at.isoformat() if p.created_at else None,
            } for p in products.items],
            'total': products.total,
            'pages': products.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<product_id>', methods=['GET'])
@admin_required
def get_product(product_id):
    """Get single product details"""
    try:
        p = Product.query.get_or_404(product_id)
        return jsonify({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': float(p.price) if p.price else 0,
            'category': p.category,
            'imageUrl': p.image_url,
            'isActive': p.is_active,
            'createdAt': p.created_at.isoformat() if p.created_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@products_bp.route('', methods=['POST'])
@admin_required
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': 'Product name is required'}), 400

        product_id = str(uuid.uuid4())

        product = Product(
            id=product_id,
            name=data['name'],
            description=data.get('description'),
            price=data.get('price', 0),
            category=data.get('category'),
            image_url=data.get('imageUrl'),
            is_active=data.get('isActive', True),
            created_at=datetime.utcnow()
        )

        db.session.add(product)
        db.session.commit()

        log_audit('PRODUCT_CREATE', 'product', product_id, {'name': data['name']})

        return jsonify({'ok': True, 'id': product_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    """Update a product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()

        if 'name' in data:
            product.name = data['name']
        if 'description' in data:
            product.description = data['description']
        if 'price' in data:
            product.price = data['price']
        if 'category' in data:
            product.category = data['category']
        if 'imageUrl' in data:
            product.image_url = data['imageUrl']
        if 'isActive' in data:
            product.is_active = data['isActive']

        db.session.commit()
        log_audit('PRODUCT_UPDATE', 'product', product_id, data)

        return jsonify({'ok': True, 'message': 'Product updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@products_bp.route('/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)

        db.session.delete(product)
        db.session.commit()

        log_audit('PRODUCT_DELETE', 'product', product_id)

        return jsonify({'ok': True, 'message': 'Product deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
