from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    

    def __repr__(self):
        return f'<User {self.id} - {self.email}>' 

    def serialize(self):
        # do not serialize the password, its a security breach
        return {"id": self.id,
                "email": self.email,
                'is_active': self.is_active}


# Modelo de 'Planets'

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    
    def __repr__(self):
        return f'<Planet: {self.id} - {self.name}'

    def serialize(self):
        return {"id": self.id,
                "name": self.name}


# Modelo de 'Characters' 

class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    
    def __repr__(self):
        return f'<Character: {self.id} - {self.name}'

    def serialize(self):
        return {"id": self.id,
                "name": self.name}

# Modelo de 'Character_Favorites'
# Many to Many - Modelo Puente 

class CharacterFavorites(db.Model):
    __tablename__ = 'character_favorites'
    id = db.Column(db.Integer, primary_key=True)
    # Columns FK
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'))
    # Relationship 
    users = db.relationship('Users', foreign_keys=[user_id])
    character = db.relationship('Characters', foreign_keys=[character_id])

    def __repr__(self):
        return f'<Character: {self.id} - {self.user_id} - {self.name}'

    def serialize(self):
        return {"id": self.id,
                "user_id": self.user_id,
                "character_id": self.character_id,
                "character_name": self.character.name}

class PlanetFavorites(db.Model):
    __tablename__ = 'planet_favorites'
    id = db.Column(db.Integer, primary_key=True)
    # Columns FK
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    # Relationship
    user = db.relationship('Users', foreign_keys=[user_id])
    planet = db.relationship('Planets', foreign_keys=[planet_id])

    def __repr__(self):
        return f'<Planet: {self.id} - {self.user_id} - {self.planet_id}>'

    def serialize(self):
        return {"id": self.id,
                "user_id": self.user_id,
                "planet_id": self.planet_id,
                "planet_name": self.planet.name}