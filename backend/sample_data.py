from models import db, User, Listing, ListingImage, Favorite, Message, PropertyFeature
from datetime import datetime, timedelta
import random

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
            price=890000.0,
            property_type='apartment',
            bedrooms=4,
            bathrooms=2,
            square_feet=140,
            address='Jungfernstieg 5',
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
            description='Modernes Penthouse mit Dachterrasse und Blick auf die Frankfurter Skyline.',
            price=1750000.0,
            property_type='apartment',
            bedrooms=5,
            bathrooms=3,
            square_feet=180,
            address='Zeil 100',
            city='Frankfurt',
            state='Hessen',
            zip_code='60313',
            latitude=50.1155,
            longitude=8.6842,
            status='active'
        ),
        Listing(
            owner_id=2,
            title='Familienhaus am Dom',
            description='Geräumiges Einfamilienhaus in bester Lage, fußläufig zum Kölner Dom.',
            price=950000.0,
            property_type='house',
            bedrooms=5,
            bathrooms=3,
            square_feet=200,
            address='Domkloster 2',
            city='Köln',
            state='NRW',
            zip_code='50667',
            latitude=50.9413,
            longitude=6.9583,
            status='active'
        ),
        Listing(
            owner_id=5,
            title='Stilvolle Wohnung an der Königsallee',
            description='Elegante 2-Zimmer-Wohnung mit Balkon und Blick auf die Königsallee.',
            price=720000.0,
            property_type='apartment',
            bedrooms=2,
            bathrooms=1,
            square_feet=90,
            address='Königsallee 45',
            city='Düsseldorf',
            state='NRW',
            zip_code='40212',
            latitude=51.2254,
            longitude=6.7763,
            status='active'
        ),
        Listing(
            owner_id=2,
            title='Reihenhaus am Schlossplatz',
            description='Modernes Reihenhaus mit Terrasse und Garten, zentral in Stuttgart gelegen.',
            price=830000.0,
            property_type='house',
            bedrooms=4,
            bathrooms=2,
            square_feet=130,
            address='Schlossplatz 8',
            city='Stuttgart',
            state='Baden-Württemberg',
            zip_code='70173',
            latitude=48.7784,
            longitude=9.1806,
            status='active'
        ),
        Listing(
            owner_id=5,
            title='Loftwohnung am Augustusplatz',
            description='Großzügige Loftwohnung mit moderner Ausstattung und Blick auf den Augustusplatz.',
            price=670000.0,
            property_type='apartment',
            bedrooms=3,
            bathrooms=2,
            square_feet=120,
            address='Augustusplatz 1',
            city='Leipzig',
            state='Sachsen',
            zip_code='04109',
            latitude=51.3397,
            longitude=12.3731,
            status='active'
        ),
        Listing(
            owner_id=2,
            title='Dachgeschosswohnung am Altmarkt',
            description='Helle Dachgeschosswohnung mit großer Dachterrasse im Herzen von Dresden.',
            price=610000.0,
            property_type='apartment',
            bedrooms=2,
            bathrooms=1,
            square_feet=85,
            address='Altmarkt 10',
            city='Dresden',
            state='Sachsen',
            zip_code='01067',
            latitude=51.0504,
            longitude=13.7373,
            status='active'
        ),
        Listing(
            owner_id=5,
            title='Stadthaus am Kröpcke',
            description='Stilvolles Stadthaus mit Garten und Garage, zentral in Hannover.',
            price=990000.0,
            property_type='house',
            bedrooms=5,
            bathrooms=3,
            square_feet=180,
            address='Kröpcke 3',
            city='Hannover',
            state='Niedersachsen',
            zip_code='30159',
            latitude=52.3759,
            longitude=9.7320,
            status='active'
        )
    ]
    for listing in listings:
        db.session.add(listing)
    db.session.commit()

    # Pool of real house images
    house_images = [
        'https://images.pexels.com/photos/106399/pexels-photo-106399.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/259588/pexels-photo-259588.jpeg?auto=compress&w=800',
        'https://images.pexels.com/photos/534151/pexels-photo-534151.jpeg?auto=compress&w=800',
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