#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class AllRestaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        response_body = [restaurant.to_dict(rules=('-restaurant_pizzas',)) for restaurant in restaurants]
        return make_response(response_body, 200)

api.add_resource(AllRestaurants, '/restaurants')

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)

        if restaurant:
            response_body = restaurant.to_dict(rules=('-restaurant_pizzas.restaurant', '-restaurant_pizzas.pizza.restaurant_pizzas'))
            return make_response(response_body, 200)

        else:
            response_body = {
                "error": "Restaurant not found"
            }
            return make_response(response_body, 404)
        
    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)

        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response({}, 204)

        else:
            response_body = {
                "error": "Restaurant not found"
            }
            return make_response(response_body, 404)

api.add_resource(RestaurantByID, '/restaurants/<int:id>')

class AllPizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        response_body = [pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas]
        return make_response(response_body, 200)

api.add_resource(AllPizzas, '/pizzas')

class AllRestaurantPizzas(Resource):
    def post(self):
        price_data = request.json.get('price')
        pizza_id_data = request.json.get('pizza_id')
        restaurant_id_data = request.json.get('restaurant_id')
        try:
            new_restaurant_pizza = RestaurantPizza(price=price_data, pizza_id=pizza_id_data, restaurant_id=restaurant_id_data)
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            response_body = new_restaurant_pizza.to_dict(rules=('-pizza.restaurant_pizzas', '-restaurant.restaurant_pizzas'))
            return make_response(response_body, 201)
        except:
            response_body = {
                "errors": ["validation errors"]
            }
            return make_response(response_body, 400)

api.add_resource(AllRestaurantPizzas, '/restaurant_pizzas')

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


if __name__ == "__main__":
    app.run(port=5555, debug=True)
