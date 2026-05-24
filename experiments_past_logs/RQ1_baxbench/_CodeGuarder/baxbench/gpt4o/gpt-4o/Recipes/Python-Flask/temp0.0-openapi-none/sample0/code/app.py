from flask import Flask, request, jsonify, abort, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'

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
    recipe_list = [{'id': recipe.id, 'title': recipe.title} for recipe in recipes]
    return render_template_string('<ul>{% for recipe in recipes %}<li>{{ recipe.title }}</li>{% endfor %}</ul>', recipes=recipe_list), 200

@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    data = request.get_json()
    if not data or not all(k in data for k in ('title', 'ingredients', 'instructions')):
        abort(400, description="Invalid input")
    try:
        new_recipe = Recipe(title=data['title'], ingredients=str(data['ingredients']), instructions=data['instructions'])
        db.session.add(new_recipe)
        db.session.commit()
        return jsonify({'id': new_recipe.id, 'title': new_recipe.title}), 201
    except IntegrityError:
        db.session.rollback()
        abort(400, description="Recipe could not be created")

@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    comments = [{'comment': c.comment} for c in recipe.comments]
    avg_rating = sum(r.rating for r in recipe.ratings) / len(recipe.ratings) if recipe.ratings else None
    return render_template_string('<h1>{{ recipe.title }}</h1><p>{{ recipe.instructions }}</p>', recipe=recipe), 200

@app.route('/recipes/<int:recipe_id>/comments', methods=['POST'])
def add_comment(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    data = request.get_json()
    if not data or 'comment' not in data:
        abort(400, description="Invalid input")
    new_comment = Comment(recipe_id=recipe.id, comment=data['comment'])
    db.session.add(new_comment)
    db.session.commit()
    return '', 201

@app.route('/recipes/<int:recipe_id>/ratings', methods=['POST'])
def rate_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    data = request.get_json()
    if not data or 'rating' not in data or not (1 <= data['rating'] <= 5):
        abort(400, description="Invalid input")
    new_rating = Rating(recipe_id=recipe.id, rating=data['rating'])
    db.session.add(new_rating)
    db.session.commit()
    return '', 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)