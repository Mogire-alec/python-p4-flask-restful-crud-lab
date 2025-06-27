from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

api = Api(app)

# Resource: /plants
class Plants(Resource):
    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()
        try:
            new_plant = Plant(
                name=data['name'],
                image=data['image'],
                price=data['price']
            )
            db.session.add(new_plant)
            db.session.commit()
            return make_response(new_plant.to_dict(), 201)
        except Exception:
            return make_response(jsonify({'error': 'Invalid plant data'}), 400)

api.add_resource(Plants, '/plants')


# Resource: /plants/<id>
class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.get(id)
        if not plant:
            return make_response(jsonify({'error': 'Plant not found'}), 404)
        return make_response(jsonify(plant.to_dict()), 200)

    def patch(self, id):
        plant = Plant.query.get(id)
        if not plant:
            return make_response(jsonify({'error': 'Plant not found'}), 404)

        if not request.is_json:
            return make_response(jsonify({'error': 'Content-Type must be application/json'}), 415)

        data = request.get_json()
        if 'is_in_stock' not in data:
            return make_response(jsonify({'error': 'is_in_stock field is required'}), 400)
        if not isinstance(data['is_in_stock'], bool):
            return make_response(jsonify({'error': 'is_in_stock must be a boolean'}), 400)

        try:
            plant.is_in_stock = data['is_in_stock']
            db.session.commit()
            return make_response(jsonify(plant.to_dict()), 200)
        except Exception:
            db.session.rollback()
            return make_response(jsonify({'error': 'Failed to update plant'}), 500)

    def delete(self, id):
        plant = Plant.query.get(id)
        if not plant:
            return make_response(jsonify({'error': 'Plant not found'}), 404)

        try:
            db.session.delete(plant)
            db.session.commit()
            return make_response('', 204)
        except Exception:
            db.session.rollback()
            return make_response(jsonify({'error': 'Failed to delete plant'}), 500)

api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)