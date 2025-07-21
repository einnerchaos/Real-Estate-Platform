from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime, timedelta
import os
import random

# Models
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    user_type = db.Column(db.String(20))  # buyer, seller, agent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    listings = db.relationship('Listing', backref='owner', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    property_type = db.Column(db.String(50))  # house, apartment, condo, land
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    square_feet = db.Column(db.Float)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')  # active, sold, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    images = db.relationship('ListingImage', backref='listing', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='listing', lazy=True)

class ListingImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=True)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PropertyFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    feature_name = db.Column(db.String(100), nullable=False)
    feature_value = db.Column(db.String(200))

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

def create_sample_data():
    # Create users
    users = [
        User(
            name='Max Mustermann',
            email='max@example.com',
            password='password123',
            phone='+49-30-123456',
            user_type='buyer'
        ),
        User(
            name='Sabine Müller',
            email='sabine@example.com',
            password='password123',
            phone='+49-89-654321',
            user_type='seller'
        ),
        User(
            name='Thomas Schmidt',
            email='thomas@example.com',
            password='password123',
            phone='+49-40-987654',
            user_type='agent'
        ),
        User(
            name='Julia Becker',
            email='julia@example.com',
            password='password123',
            phone='+49-69-112233',
            user_type='buyer'
        ),
        User(
            name='David Wagner',
            email='david@example.com',
            password='password123',
            phone='+49-221-445566',
            user_type='seller'
        )
    ]
    for user in users:
        db.session.add(user)
    db.session.commit()

    # German cities and coordinates
    german_cities = [
        ('Berlin', 'Brandenburger Tor', '10117', 52.5163, 13.3777),
        ('München', 'Marienplatz', '80331', 48.1371, 11.5754),
        ('Hamburg', 'Jungfernstieg', '20095', 53.5535, 9.9937),
        ('Frankfurt', 'Zeil', '60313', 50.1155, 8.6842),
        ('Köln', 'Domkloster', '50667', 50.9413, 6.9583),
        ('Düsseldorf', 'Königsallee', '40212', 51.2254, 6.7763),
        ('Stuttgart', 'Schlossplatz', '70173', 48.7784, 9.1806),
        ('Leipzig', 'Augustusplatz', '04109', 51.3397, 12.3731),
        ('Dresden', 'Altmarkt', '01067', 51.0504, 13.7373),
        ('Hannover', 'Kröpcke', '30159', 52.3759, 9.7320)
    ]
    
    # Sample listings in German cities
    listings = [
        Listing(
            owner_id=2,
            title='Moderne Wohnung am Brandenburger Tor',
            description='Helle, moderne 3-Zimmer-Wohnung mit Balkon im Herzen von Berlin. Perfekt für Familien oder Paare.',
            price=650000.0,
            property_type='apartment',
            bedrooms=3,
            bathrooms=2,
            square_feet=110,
            address='Brandenburger Tor 1',
            city='Berlin',
            state='Berlin',
            zip_code='10117',
            latitude=52.5163,
            longitude=13.3777,
            status='active'
        ),
        Listing(
            owner_id=5,
            title='Luxusvilla mit Isarblick',
            description='Exklusive Villa mit großem Garten und Blick auf die Isar. Hochwertige Ausstattung, ruhige Lage.',
            price=2200000.0,
            property_type='house',
            bedrooms=6,
            bathrooms=4,
            square_feet=350,
            address='Isarstraße 12',
            city='München',
            state='Bayern',
            zip_code='80331',
            latitude=48.1371,
            longitude=11.5754,
            status='active'
        ),
        Listing(
            owner_id=2,
            title='Altbauwohnung an der Alster',
            description='Charmante Altbauwohnung mit hohen Decken und Stuck, direkt an der Außenalster.',
            price=850000.0,
            property_type='apartment',
            bedrooms=4,
            bathrooms=2,
            square_feet=140,
            address='Alsterufer 8',
            city='Hamburg',
            state='Hamburg',
            zip_code='20095',
            latitude=53.5535,
            longitude=9.9937,
            status='active'
        ),
        Listing(
            owner_id=5,
            title='Penthouse mit Skyline-Blick',
            description='Luxuriöses Penthouse mit Panoramablick über die Frankfurter Skyline. Moderne Ausstattung.',
            price=1800000.0,
            property_type='apartment',
            bedrooms=3,
            bathrooms=3,
            square_feet=180,
            address='Zeil 123',
            city='Frankfurt',
            state='Hessen',
            zip_code='60313',
            latitude=50.1155,
            longitude=8.6842,
            status='active'
        ),
        Listing(
            owner_id=2,
            title='Stadtvilla im Rheinviertel',
            description='Elegante Stadtvilla im exklusiven Rheinviertel. Großer Garten, Garage, hochwertige Ausstattung.',
            price=1200000.0,
            property_type='house',
            bedrooms=5,
            bathrooms=3,
            square_feet=280,
            address='Rheinallee 45',
            city='Köln',
            state='Nordrhein-Westfalen',
            zip_code='50667',
            latitude=50.9413,
            longitude=6.9583,
            status='active'
        ),
        Listing(
            owner_id=5,
            title='Stadthaus am Kröpcke',
            description='Moderne Stadthaus in bester Lage. Offener Grundriss, Terrasse, Tiefgarage.',
            price=950000.0,
            property_type='house',
            bedrooms=4,
            bathrooms=2,
            square_feet=200,
            address='Kröpcke 7',
            city='Hannover',
            state='Niedersachsen',
            zip_code='30159',
            latitude=52.3759,
            longitude=9.7320,
            status='active'
        ),
        Listing(
            owner_id=2,
            title='Loftwohnung am Augustusplatz',
            description='Industrielles Loft in einem umgebauten Fabrikgebäude. Hohe Decken, große Fenster.',
            price=750000.0,
            property_type='apartment',
            bedrooms=2,
            bathrooms=2,
            square_feet=160,
            address='Augustusplatz 15',
            city='Leipzig',
            state='Sachsen',
            zip_code='04109',
            latitude=51.3397,
            longitude=12.3731,
            status='active'
        ),
        Listing(
            owner_id=5,
            title='Barockwohnung am Altmarkt',
            description='Historische Wohnung in einem Barockgebäude. Stuckdecken, Parkett, antike Details.',
            price=680000.0,
            property_type='apartment',
            bedrooms=3,
            bathrooms=1,
            square_feet=120,
            address='Altmarkt 22',
            city='Dresden',
            state='Sachsen',
            zip_code='01067',
            latitude=51.0504,
            longitude=13.7373,
            status='active'
        )
    ]
    
    for listing in listings:
        db.session.add(listing)
    db.session.commit()

    # Add images to listings
    house_images = [
        'https://images.pexels.com/photos/106399/pexels-photo-106399.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/1396122/pexels-photo-1396122.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/210617/pexels-photo-210617.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/323780/pexels-photo-323780.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259962/pexels-photo-259962.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259600/pexels-photo-259600.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259701/pexels-photo-259701.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259624/pexels-photo-259624.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259580/pexels-photo-259580.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259597/pexels-photo-259597.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259618/pexels-photo-259618.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259588/pexels-photo-259588.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259600/pexels-photo-259600.jpeg?auto=compress&w=800',
    ]
    
    # Add multiple images per listing
    listing_objs = Listing.query.all()
    for i, listing in enumerate(listing_objs):
        used_imgs = random.sample(house_images, 3)
        for j, img_url in enumerate(used_imgs):
            db.session.add(ListingImage(listing_id=listing.id, image_url=img_url, is_primary=(j==0)))
    db.session.commit()

    # Add property features per listing
    feature_pool = [
        ('Balkon', ['Ja', 'Nein']),
        ('Garten', ['Ja', 'Nein']),
        ('Keller', ['Ja', 'Nein']),
        ('Baujahr', ['1990', '2005', '2015', '2020', '1975']),
        ('Heizung', ['Gas', 'Fernwärme', 'Öl', 'Wärmepumpe', 'Elektro']),
        ('Energieausweis', ['Vorhanden', 'Nicht vorhanden']),
        ('Stellplatz', ['Garage', 'Tiefgarage', 'Außenstellplatz', 'Kein Stellplatz']),
        ('Aufzug', ['Ja', 'Nein']),
        ('Barrierefrei', ['Ja', 'Nein']),
        ('Einbauküche', ['Ja', 'Nein']),
        ('Internet', ['Glasfaser', 'DSL', 'Kabel', 'Kein Internet']),
        ('Bodenbelag', ['Parkett', 'Fliesen', 'Teppich', 'Laminat']),
        ('Möbliert', ['Ja', 'Nein']),
        ('Haustiere erlaubt', ['Ja', 'Nein'])
    ]
    for listing in listing_objs:
        chosen = random.sample(feature_pool, 6)
        for fname, fvals in chosen:
            db.session.add(PropertyFeature(listing_id=listing.id, feature_name=fname, feature_value=random.choice(fvals)))
    db.session.commit()
    
    # Create favorites
    favorites = [
        Favorite(user_id=1, listing_id=1),  # Max likes Moderne Wohnung am Brandenburger Tor
        Favorite(user_id=1, listing_id=3),  # Max likes Altbauwohnung an der Alster
        Favorite(user_id=4, listing_id=2),  # Julia likes Luxusvilla mit Isarblick
        Favorite(user_id=4, listing_id=4),  # Julia likes Penthouse mit Skyline-Blick
        Favorite(user_id=3, listing_id=6),  # Thomas likes Stadthaus am Kröpcke
        Favorite(user_id=3, listing_id=8),  # Thomas likes Loftwohnung am Augustusplatz
    ]
    
    for favorite in favorites:
        db.session.add(favorite)
    db.session.commit()
    
    # Create messages
    messages = [
        Message(
            sender_id=1,  # Max
            receiver_id=2,  # Sabine
            listing_id=1,
            subject='Interesse an Wohnung am Brandenburger Tor',
            content='Hallo Sabine, ich bin sehr interessiert an Ihrer Wohnung am Brandenburger Tor. Ist sie noch verfügbar?',
            is_read=False
        ),
        Message(
            sender_id=2,  # Sabine
            receiver_id=1,  # Max
            listing_id=1,
            subject='Re: Interesse an Wohnung am Brandenburger Tor',
            content='Hallo Max, ja sie ist noch verfügbar! Ich kann Ihnen heute Abend einen Besichtigungstermin anbieten. Wann passt es Ihnen?',
            is_read=True
        ),
        Message(
            sender_id=4,  # Julia
            receiver_id=5,  # David
            listing_id=2,
            subject='Luxusvilla Anfrage',
            content='Hallo David, ich bin sehr interessiert an Ihrer Luxusvilla. Können Sie mir mehr über die Ausstattung und den Garten erzählen?',
            is_read=False
        ),
        Message(
            sender_id=3,  # Thomas
            receiver_id=5,  # David
            listing_id=6,
            subject='Stadthaus Fragen',
            content='Hallo David, ich bin ein Agent für einen Kunden, der an Ihrem Stadthaus interessiert ist. Ist die Garage inbegriffen?',
            is_read=False
        )
    ]
    
    for message in messages:
        db.session.add(message)
    db.session.commit()
    
    print("Sample data created successfully!")

if __name__ == '__main__':
    initialize_database()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True) 