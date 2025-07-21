from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime, timedelta
import os

from models import db, User, Listing, ListingImage, Favorite, Message, PropertyFeature

app = Flask(__name__, instance_path='/tmp')
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///real_estate.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

db.init_app(app)
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global flag to track initialization
_initialized = False

def initialize_database():
    with app.app_context():
        db.create_all()
        
        # Create sample data if database is empty
        if not User.query.first():
            from sample_data import create_sample_data
            create_sample_data()

@app.before_request
def ensure_initialized():
    global _initialized
    if not _initialized:
        initialize_database()
        _initialized = True

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    user = User(
        name=data['name'],
        email=data['email'],
        password=data['password'],  # In production, hash the password
        phone=data.get('phone'),
        user_type=data.get('user_type', 'buyer')
    )
    
    db.session.add(user)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'token': access_token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'user_type': user.user_type
        }
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f"[LOGIN] Attempt: email={data.get('email')}")
    user = User.query.filter_by(email=data['email']).first()
    if user:
        print(f"[LOGIN] User found: {user.email}")
        if user.password == data['password']:
            print(f"[LOGIN] Password match for {user.email}")
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'token': access_token,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.phone,
                    'user_type': user.user_type
                }
            })
        else:
            print(f"[LOGIN] Password mismatch for {user.email}")
    else:
        print(f"[LOGIN] User not found for email: {data.get('email')}")
    return jsonify({'error': 'Invalid credentials'}), 401

# User profile routes
@app.route('/api/user/profile', methods=['GET'])
# @jwt_required()
def get_profile():
    # user_id = get_jwt_identity()
    # For demo: always return the first user
    user = User.query.first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'user_type': user.user_type
    })

@app.route('/api/user/profile', methods=['PUT'])
# @jwt_required()
def update_profile():
    # user_id = get_jwt_identity()
    user = User.query.first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()
    if 'name' in data:
        user.name = data['name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'user_type' in data:
        user.user_type = data['user_type']
    db.session.commit()
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'phone': user.phone,
        'user_type': user.user_type
    })

# Listing routes
@app.route('/api/listings', methods=['GET'])
def get_listings():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    property_type = request.args.get('property_type')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    bedrooms = request.args.get('bedrooms', type=int)
    city = request.args.get('city')
    status = request.args.get('status', 'active')
    
    query = Listing.query.filter_by(status=status)
    
    if property_type:
        query = query.filter_by(property_type=property_type)
    if min_price:
        query = query.filter(Listing.price >= min_price)
    if max_price:
        query = query.filter(Listing.price <= max_price)
    if bedrooms:
        query = query.filter(Listing.bedrooms >= bedrooms)
    if city:
        query = query.filter(Listing.city.ilike(f'%{city}%'))
    
    listings = query.order_by(Listing.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'listings': [{
            'id': listing.id,
            'title': listing.title,
            'description': listing.description,
            'price': listing.price,
            'property_type': listing.property_type,
            'bedrooms': listing.bedrooms,
            'bathrooms': listing.bathrooms,
            'square_feet': listing.square_feet,
            'address': listing.address,
            'city': listing.city,
            'state': listing.state,
            'zip_code': listing.zip_code,
            'latitude': listing.latitude,
            'longitude': listing.longitude,
            'status': listing.status,
            'created_at': listing.created_at.isoformat(),
            'owner': {
                'id': listing.owner.id,
                'name': listing.owner.name,
                'phone': listing.owner.phone
            },
            'primary_image': listing.images[0].image_url if listing.images else None,
            'image_count': len(listing.images)
        } for listing in listings.items],
        'total': listings.total,
        'pages': listings.pages,
        'current_page': page
    })

@app.route('/api/listings/<int:listing_id>', methods=['GET'])
def get_listing(listing_id):
    listing = Listing.query.get(listing_id)
    
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404

    # Fetch features for this listing
    features = []
    from models import PropertyFeature
    for f in PropertyFeature.query.filter_by(listing_id=listing.id).all():
        features.append({'name': f.feature_name, 'value': f.feature_value})

    return jsonify({
        'id': listing.id,
        'title': listing.title,
        'description': listing.description,
        'price': listing.price,
        'property_type': listing.property_type,
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'square_feet': listing.square_feet,
        'address': listing.address,
        'city': listing.city,
        'state': listing.state,
        'zip_code': listing.zip_code,
        'latitude': listing.latitude,
        'longitude': listing.longitude,
        'status': listing.status,
        'created_at': listing.created_at.isoformat(),
        'owner': {
            'id': listing.owner.id,
            'name': listing.owner.name,
            'phone': listing.owner.phone,
            'email': listing.owner.email
        },
        'images': [{
            'id': img.id,
            'image_url': img.image_url,
            'is_primary': img.is_primary
        } for img in listing.images],
        'features': features
    })

@app.route('/api/listings', methods=['POST'])
@jwt_required()
def create_listing():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    listing = Listing(
        owner_id=user_id,
        title=data['title'],
        description=data.get('description', ''),
        price=data['price'],
        property_type=data.get('property_type'),
        bedrooms=data.get('bedrooms'),
        bathrooms=data.get('bathrooms'),
        square_feet=data.get('square_feet'),
        address=data.get('address'),
        city=data.get('city'),
        state=data.get('state'),
        zip_code=data.get('zip_code'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude')
    )
    
    db.session.add(listing)
    db.session.commit()
    
    # Add images if provided
    if 'images' in data:
        for i, image_url in enumerate(data['images']):
            image = ListingImage(
                listing_id=listing.id,
                image_url=image_url,
                is_primary=(i == 0)  # First image is primary
            )
            db.session.add(image)
    
    db.session.commit()
    
    return jsonify({
        'id': listing.id,
        'title': listing.title,
        'price': listing.price,
        'status': listing.status
    })

@app.route('/api/listings/<int:listing_id>', methods=['PUT'])
@jwt_required()
def update_listing(listing_id):
    user_id = get_jwt_identity()
    listing = Listing.query.get(listing_id)
    
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    if listing.owner_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        listing.title = data['title']
    if 'description' in data:
        listing.description = data['description']
    if 'price' in data:
        listing.price = data['price']
    if 'property_type' in data:
        listing.property_type = data['property_type']
    if 'bedrooms' in data:
        listing.bedrooms = data['bedrooms']
    if 'bathrooms' in data:
        listing.bathrooms = data['bathrooms']
    if 'square_feet' in data:
        listing.square_feet = data['square_feet']
    if 'address' in data:
        listing.address = data['address']
    if 'city' in data:
        listing.city = data['city']
    if 'state' in data:
        listing.state = data['state']
    if 'zip_code' in data:
        listing.zip_code = data['zip_code']
    if 'status' in data:
        listing.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'id': listing.id,
        'title': listing.title,
        'price': listing.price,
        'status': listing.status
    })

# Favorite routes
@app.route('/api/favorites', methods=['GET'])
# @jwt_required()
def get_favorites():
    # user_id = get_jwt_identity()
    user = User.query.first()
    favorites = Favorite.query.filter_by(user_id=user.id).all()
    
    return jsonify([{
        'id': fav.id,
        'listing': {
            'id': fav.listing.id,
            'title': fav.listing.title,
            'price': fav.listing.price,
            'property_type': fav.listing.property_type,
            'city': fav.listing.city,
            'primary_image': fav.listing.images[0].image_url if fav.listing.images else None
        },
        'created_at': fav.created_at.isoformat()
    } for fav in favorites])

@app.route('/api/favorites', methods=['POST'])
# @jwt_required()
def add_favorite():
    # user_id = get_jwt_identity()
    user = User.query.first()
    data = request.get_json()
    
    # Check if already favorited
    existing = Favorite.query.filter_by(
        user_id=user.id, 
        listing_id=data['listing_id']
    ).first()
    
    if existing:
        return jsonify({'error': 'Already favorited'}), 400
    
    favorite = Favorite(
        user_id=user.id,
        listing_id=data['listing_id']
    )
    
    db.session.add(favorite)
    db.session.commit()
    
    return jsonify({'message': 'Added to favorites'})

@app.route('/api/favorites/<int:listing_id>', methods=['DELETE'])
# @jwt_required()
def remove_favorite(listing_id):
    # user_id = get_jwt_identity()
    user = User.query.first()
    favorite = Favorite.query.filter_by(
        user_id=user.id, 
        listing_id=listing_id
    ).first()
    
    if not favorite:
        return jsonify({'error': 'Favorite not found'}), 404
    
    db.session.delete(favorite)
    db.session.commit()
    
    return jsonify({'message': 'Removed from favorites'})

# Message routes
@app.route('/api/messages', methods=['GET'])
@jwt_required()
def get_messages():
    user_id = get_jwt_identity()
    messages = Message.query.filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).order_by(Message.created_at.desc()).all()
    
    return jsonify([{
        'id': msg.id,
        'subject': msg.subject,
        'content': msg.content,
        'is_read': msg.is_read,
        'created_at': msg.created_at.isoformat(),
        'sender': {
            'id': msg.sender.id,
            'name': msg.sender.name
        },
        'receiver': {
            'id': msg.receiver.id,
            'name': msg.receiver.name
        },
        'listing': {
            'id': msg.listing.id,
            'title': msg.listing.title
        } if msg.listing else None
    } for msg in messages])

@app.route('/api/messages', methods=['POST'])
@jwt_required()
def send_message():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    message = Message(
        sender_id=user_id,
        receiver_id=data['receiver_id'],
        listing_id=data.get('listing_id'),
        subject=data.get('subject', ''),
        content=data['content']
    )
    
    db.session.add(message)
    db.session.commit()
    
    # Emit real-time notification
    socketio.emit('new_message', {
        'message': {
            'id': message.id,
            'subject': message.subject,
            'content': message.content,
            'sender': {
                'id': message.sender.id,
                'name': message.sender.name
            }
        }
    }, room=f"user_{data['receiver_id']}")
    
    return jsonify({
        'id': message.id,
        'subject': message.subject,
        'content': message.content
    })

# Search routes
@app.route('/api/search', methods=['GET'])
def search_listings():
    query = request.args.get('q', '')
    property_type = request.args.get('property_type')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    bedrooms = request.args.get('bedrooms', type=int)
    city = request.args.get('city')
    
    listings_query = Listing.query.filter_by(status='active')
    
    if query:
        listings_query = listings_query.filter(
            db.or_(
                Listing.title.ilike(f'%{query}%'),
                Listing.description.ilike(f'%{query}%'),
                Listing.address.ilike(f'%{query}%'),
                Listing.city.ilike(f'%{query}%')
            )
        )
    
    if property_type:
        listings_query = listings_query.filter_by(property_type=property_type)
    if min_price:
        listings_query = listings_query.filter(Listing.price >= min_price)
    if max_price:
        listings_query = listings_query.filter(Listing.price <= max_price)
    if bedrooms:
        listings_query = listings_query.filter(Listing.bedrooms >= bedrooms)
    if city:
        listings_query = listings_query.filter(Listing.city.ilike(f'%{city}%'))
    
    listings = listings_query.order_by(Listing.created_at.desc()).limit(20).all()
    
    return jsonify([{
        'id': listing.id,
        'title': listing.title,
        'price': listing.price,
        'property_type': listing.property_type,
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'city': listing.city,
        'state': listing.state,
        'primary_image': listing.images[0].image_url if listing.images else None
    } for listing in listings])

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_user_room')
def handle_join_user_room(data):
    room = f"user_{data['user_id']}"
    join_room(room)
    print(f'Client joined room: {room}')

if __name__ == '__main__':
    initialize_database()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True) 