from flask import Flask, request, jsonify, render_template, abort
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    comments = db.relationship('Comment', backref='recipe', lazy=True)
    ratings = db.relationship('Rating', backref='recipe', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

db.create_all()

@app.route('/recipes', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    data = request.get_json()
    if not data or 'title' not in data or 'ingredients' not in data or 'instructions' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    new_recipe = Recipe(
        title=data['title'],
        ingredients=', '.join(data['ingredients']),
        instructions=data['instructions']
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({'id': new_recipe.id, 'title': new_recipe.title}), 201

@app.route('/recipes/<int:recipeId>', methods=['GET'])
def get_recipe(recipeId):
    recipe = Recipe.query.get(recipeId)
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404
    return render_template('recipe.html', recipe=recipe)

@app.route('/recipes/<int:recipeId>/comments', methods=['POST'])
def add_comment(recipeId):
    data = request.get_json()
    if not data or 'comment' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    recipe = Recipe.query.get(recipeId)
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404

    new_comment = Comment(recipe_id=recipeId, comment=data['comment'])
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'Comment added successfully'}), 201

@app.route('/recipes/<int:recipeId>/ratings', methods=['POST'])
def rate_recipe(recipeId):
    data = request.get_json()
    if not data or 'rating' not in data or not (1 <= data['rating'] <= 5):
        return jsonify({'error': 'Invalid input'}), 400

    recipe = Recipe.query.get(recipeId)
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404

    new_rating = Rating(recipe_id=recipeId, rating=data['rating'])
    db.session.add(new_rating)
    db.session.commit()
    return jsonify({'message': 'Rating added successfully'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)