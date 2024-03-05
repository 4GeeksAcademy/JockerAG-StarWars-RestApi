"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Users, Planets, Characters, PlanetFavorites, CharacterFavorites
#from models import Person


# Instancias de flask
app = Flask(__name__)
app.url_map.strict_slashes = False
# Configuracion de DB
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {"msg": "Hello, this is your GET /user response "}
    return jsonify(response_body), 200

@app.route('/users', methods=['GET', 'POST'])
def handle_users():
    response_body = results = {}
    if request.method == 'GET':
        users = db.session.execute(db.select(Users)).scalars()
        # .scalars() -> una lista de registros, pero como un objeto SQLAlchemy
        # .scalar() -> un registro, pero como un objeto SQLAlchemy
        """ results['users'] = [row.serialize() for row in users] """
        response_body['results'] = results['users'] = [row.serialize() for row in users]
        response_body['message'] = 'Metodo GET de users'
        return response_body, 200

    if request.method == 'POST':
        # Debor recibir el body desde el front
        data = request.json
        print(data)
        print(data["email"])

        # Creando una instancia de la clase Users
        user = Users(email =data ['email'],
                     password =data['password'],
                     role = data['role'],
                     is_active =True)
        db.session.add(user)
        db.session.commit()
        response_body['results'] = user.serialize()
        response_body['message'] = 'Metodo POST de users'
        return response_body, 200


@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(id):
    response_body = {}
    print(id)
    if request.method == 'GET':
        response_body['message'] = 'metodo GET del users/<id>'
    if request.method == 'PUT':
        response_body['message'] = 'metodo PUT del users/<id>'
    if request.method == 'DELETE':
        response_body['message'] = 'metodo DELETE del users/<id>'
    return response_body, 200

# Endpoint de People [GET]
# Request (get) de los datos de la API y grabarlos en nuestro modelo
@app.route('/characters', methods=['GET'])
def handle_characters():
    response_body = {}
    characters = db.session.execute(db.select(Characters)).scalars()
    response_body["message"] = "Character List"
    response_body["results"] = [row.serialize() for row in characters]
    return response_body, 200

# Endpoint de Users/Favorites [GET]
# Request (get) de los datos de la API y grabarlos en nuestro modelo
@app.route('/characters/<int:id>', methods=['GET'])
def handle_character(id):
    response_body = {}
    character = db.session.execute(db.select(Characters).where(Characters.id == id )).scalar()
    response_body['results'] = character.serialize()
    response_body['message'] = 'Successful!'
    return response_body, 200
    
# Endpoint de Planets ['GET']
@app.route('/planets', methods=['GET'])
def handle_planets():
    response_body = {}
    planets = db.session.execute(db.select(Planets)).scalars()
    response_body["results"] = [row.serialize() for row in planets]
    response_body["message"] = "Planets List"
    return response_body, 200  
    

# Endpoint de Users/Favorites [GET]
# Request (get) de los datos de la API y grabarlos en nuestro modelo
@app.route('/planets/<int:id>', methods=['GET'])
def handle_planet_id(id):
    response_body = {}
    results = {}
    planet = db.session.execute(db.select(Planets).where(Planets.id == id)).scalar()
    response_body['results'] = planet.serialize()
    response_body['message'] = 'Successful!'
    return response_body, 200

# Endpoint de Favorites/Characters/<id> [POST, DELETE]
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def handle_user_favorites(user_id):
    response_body = {}
    # Obtengo los planetas Favoritos del usuario y utilizamos serialize para convertir el objeto a texto
    planet_favorites = PlanetFavorites.query.filter_by(user_id = user_id).all()
    serialized_planet_favorites = [favorite.serialize() for favorite in planet_favorites]
    # Obtengo los personajes Favoritos del usuario y utilizamos serialize para convertir el objeto
    character_favorites = CharacterFavorites.query.filter_by(user_id = user_id).all()
    serialized_character_favorites = [favorite.serialize() for favorite in character_favorites]
    # Aqui muestra los resultados
    response_body['planet_favorites'] = serialized_planet_favorites
    response_body['character_favorites'] = serialized_character_favorites
    response_body['message'] = 'User Favorites List'
    return response_body, 200

# Metodo POST de planetas
@app.route('/favorites/<int:user_id>/planets', methods=['POST'])
def add_planet_favorite(user_id):
    # Obtener el planet_id 
    data = request.get_json()
    if 'planet_id' not in data:
        return {'error': 'planet_id is required in the request body'}, 400
    planet_id = data['planet_id']

    user = Users.query.get(user_id)
    if not user:
        return {'error': 'User no encontrado'}, 404
    
    planet = Planets.query.get(planet_id)
    if not planet:
        return{'error': 'Planet no encontrado'}, 404
    
    new_favorite = PlanetFavorites(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return {'message': f'Planeta favorito añadido satisfactoriamente al user: {user_id}'}

# Metodo POST de characters
@app.route('/favorites/<int:user_id>/characters', methods=['POST'])
def add_character_favorite(user_id):
    # Obtener el planet_id 
    data = request.get_json()
    if 'character_id' not in data:
        return {'error': 'character_id is required in the request body'}, 400
    character_id = data['character_id']

    user = Users.query.get(user_id)
    if not user:
        return {'error': 'User no encontrado'}, 404
    
    character = Characters.query.get(character_id)
    if not character:
        return{'error': 'Character no encontrado'}, 404
    
    new_favorite = CharacterFavorites(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite)
    db.session.commit()
    return {'message': f'Character favorito añadido satisfactoriamente al user: {user_id}'}

@app.route('/favorites/<int:user_id>/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(user_id, planet_id):
    # Verificamos el usuario
    user = None
    db_user = Users.query.get(user_id)
    if  db_user:
        user = db_user
    else:
        return{'error': 'User no encontrado'}, 404
    
    # Verificamos si el planeta existe
    favorite = PlanetFavorites.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return {'error': 'Planeta favorito no encontrado para este usuario'}, 404
    
    # Obtener el nombre del planeta para poder mostrarlo al eliminarlo
    planet_name = Planets.query.get(planet_id).name

    db.session.delete(favorite)
    db.session.commit()
    return {'message': f'Planeta favorito:{planet_name} con id:{planet_id}, eliminado correctamente para el usuario {user_id}'}

@app.route('/favorites/<int:user_id>/characters/<int:character_id>', methods=['DELETE'])
def delete_character_favorite(user_id, character_id):
    # Verificamos el usuario
    user = None
    db_user = Users.query.get(user_id)
    if  db_user:
        user = db_user
    else:
        return{'error': 'User no encontrado'}, 404
    
    # Verificamos si el planeta existe
    favorite = CharacterFavorites.query.filter_by(user_id=user_id, character_id=character_id).first()
    if not favorite:
        return {'error': 'Personaje favorito no encontrado para este usuario'}, 404

    # Obtener el nombre del personaje para poder mostrarlo al eliminarlo
    character_name = Characters.query.get(character_id).name

    db.session.delete(favorite)
    db.session.commit()
    return {'message': f'Personaje favorito:{character_name},con id: {character_id}, eliminado correctamente para el usuario {user_id}'}

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
