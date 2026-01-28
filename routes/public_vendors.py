"""
Public Vendor Routes
Allow users/tools to fetch active vendors by category/service
"""
from flask import Blueprint, jsonify, request, g
from models import Vendor
from .decorators import auth_required

public_vendors_bp = Blueprint('public_vendors', __name__, url_prefix='/api/public/vendors')

@public_vendors_bp.route('', methods=['GET'])
def get_public_vendors():
    """
    Get active vendors filtered by params
    Query Params:
      - category (str)
      - service (str)
      - featured (bool)
      - limit (int)
    """
    try:
        category = request.args.get('category')
        service = request.args.get('service')
        featured = request.args.get('featured')
        limit = request.args.get('limit', 10, type=int)

        query = Vendor.query.filter_by(status='active')

        if category:
            query = query.filter(Vendor.category == category)
        
        if featured == 'true':
            query = query.filter(Vendor.is_featured == True)

        # Basic service filter (JSON contains check could be DB specific, doing simple check for now if robust JSON search needed we need func.json_contains)
        # For compatibility, we'll fetch and filter in python if service is requested, or use simple string match if possible.
        # Ideally: query = query.filter(func.json_contains(Vendor.services, f'"{service}"'))
        
        vendors = query.order_by(Vendor.is_featured.desc(), Vendor.rating.desc()).limit(limit).all()

        results = []
        for v in vendors:
            # Python-side filtering for service if needed
            if service and v.services:
                if service not in v.services:
                    continue

            v_dict = {
                'id': v.id,
                'name': v.name,
                'description': v.description,
                'category': v.category,
                'services': v.services,
                'rating': float(v.rating) if v.rating else 0.0,
                'reviewCount': v.review_count,
                'isFeatured': v.is_featured,
                'logoUrl': v.logo_url,
                'website': v.website,
                'metadata': v.metadata_json or {},
                'countryCode': v.country_code
            }
            results.append(v_dict)

        return jsonify({'vendors': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@public_vendors_bp.route('/<vendor_id>', methods=['GET'])
def get_vendor_details(vendor_id):
    """Get full vendor details"""
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        if vendor.status != 'active':
            return jsonify({'error': 'Vendor not found'}), 404

        data = {
            'id': vendor.id,
            'name': vendor.name,
            'description': vendor.description,
            'category': vendor.category,
            'services': vendor.services,
            'rating': float(vendor.rating) if vendor.rating else 0.0,
            'reviewCount': vendor.review_count,
            'isFeatured': vendor.is_featured,
            'logoUrl': vendor.logo_url,
            'website': vendor.website,
            'phone': vendor.phone,
            'email': vendor.email,
            'metadata': vendor.metadata_json or {},
            'countryCode': vendor.country_code,
            'createdAt': vendor.created_at.isoformat() if vendor.created_at else None
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_vendors_bp.route('/<vendor_id>/history', methods=['GET'])
def get_vendor_history(vendor_id):
    """Get historical data points for analysis"""
    try:
        from models import VendorHistory
        metric = request.args.get('metric')
        days = request.args.get('days', 365, type=int)
        
        query = VendorHistory.query.filter_by(vendor_id=vendor_id)
        if metric:
            query = query.filter_by(metric_type=metric)
            
        history = query.order_by(VendorHistory.recorded_at.asc()).all()
        
        results = [{
            'date': h.recorded_at.isoformat(),
            'value': float(h.value),
            'metric': h.metric_type
        } for h in history]
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_vendors_bp.route('/<vendor_id>/reviews', methods=['GET'])
def get_vendor_reviews(vendor_id):
    """Get vendor reviews"""
    try:
        from models import VendorReview
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        
        pagination = VendorReview.query.filter_by(vendor_id=vendor_id)\
            .order_by(VendorReview.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
            
        results = []
        for r in pagination.items:
            results.append({
                'id': r.id,
                'rating': r.rating,
                'comment': r.comment,
                'userName': r.user.name if r.user else 'Anonymous',
                'userAvatar': r.user.avatar_url if r.user else None,
                'isVerified': r.is_verified_customer,
                'date': r.created_at.isoformat()
            })
            
        return jsonify({
            'reviews': results,
            'total': pagination.total,
            'pages': pagination.pages,
            'current': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@public_vendors_bp.route('/<vendor_id>/reviews', methods=['POST'])
@auth_required
def create_vendor_review(vendor_id):
    """Create a review (Requires Auth)"""
    try:
        from models import VendorReview, db, Vendor
        import uuid
        from datetime import datetime, timezone
        
        data = request.get_json()
        user_id = g.user.id
        
        # Validation
        rating = data.get('rating')
        if not rating or not (1 <= float(rating) <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            
        comment = data.get('comment', '')
        
        # Check if vendor exists
        vendor = Vendor.query.get_or_404(vendor_id)
        
        # Check if already reviewed
        existing = VendorReview.query.filter_by(vendor_id=vendor_id, user_id=user_id).first()
        if existing:
            # Update existing
            existing.rating = rating
            existing.comment = comment
            existing.created_at = datetime.now(timezone.utc)
            db.session.commit()
            
            # Recalc rating
            update_vendor_rating(vendor_id)
            
            return jsonify({'ok': True, 'id': existing.id, 'message': 'Review updated'})

        review_id = str(uuid.uuid4())
        review = VendorReview(
            id=review_id,
            vendor_id=vendor_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
            created_at=datetime.now(timezone.utc),
            is_verified_customer=False # Placeholder
        )
        
        db.session.add(review)
        db.session.commit()
        
        # Recalc rating
        update_vendor_rating(vendor_id)
        
        return jsonify({'ok': True, 'id': review_id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def update_vendor_rating(vendor_id):
    from models import VendorReview, Vendor, db
    reviews = VendorReview.query.filter_by(vendor_id=vendor_id).all()
    if not reviews:
        return
        
    avg = sum(r.rating for r in reviews) / len(reviews)
    vendor = Vendor.query.get(vendor_id)
    if vendor:
        vendor.rating = avg
        vendor.review_count = len(reviews)
        db.session.commit()
