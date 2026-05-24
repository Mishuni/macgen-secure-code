from flask import Flask, request, jsonify, render_template, abort
from flask_wtf import CSRFProtect
from werkzeug.exceptions import HTTPException
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Secure random key for CSRF protection
csrf = CSRFProtect(app)

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.errorhandler(HTTPException)
def handle_exception(e):
    response = e.get_response()
    response.data = jsonify({'error': e.description}).data
    response.content_type = "application/json"
    return response

@app.route('/recipes', methods=['GET'])
def get_recipes():
    conn = get_db_connection()
    recipes = conn.execute('SELECT id, title FROM recipes').fetchall()
    conn.close()
    recipe_list = [{'id': recipe['id'], 'title': recipe['title']} for recipe in recipes]
    html_content = render_template('recipes.html', recipes=recipe_list)
    return html_content, 200

@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    data = request.get_json()
    if not data or 'title' not in data or 'ingredients' not in data or 'instructions' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    title = data['title'].strip()
    ingredients = ','.join(data['ingredients']).strip()
    instructions = data['instructions'].strip()

    if not title or not ingredients or not instructions:
        return jsonify({'error': 'Invalid input'}), 400

    if len(title) > 255 or len(ingredients) > 1000 or len(instructions) > 2000:
        return jsonify({'error': 'Input too long'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
                   (title, ingredients, instructions))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': recipe_id, 'title': title, 'ingredients': data['ingredients'], 'instructions': instructions}), 201

@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
    if recipe is None:
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404

    comments = conn.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,)).fetchall()
    ratings = conn.execute('SELECT rating FROM ratings WHERE recipe_id = ?', (recipe_id,)).fetchall()
    conn.close()

    avg_rating = sum(rating['rating'] for rating in ratings) / len(ratings) if ratings else None
    recipe_data = {
        'id': recipe['id'],
        'title': recipe['title'],
        'ingredients': recipe['ingredients'].split(','),
        'instructions': recipe['instructions'],
        'comments': [comment['comment'] for comment in comments],
        'avgRating': avg_rating
    }

    html_content = render_template('recipe.html', recipe=recipe_data)
    return html_content, 200

@app.route('/recipes/<int:recipe_id>/comments', methods=['POST'])
def add_comment(recipe_id):
    data = request.get_json()
    if not data or 'comment' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    comment = data['comment'].strip()
    if not comment:
        return jsonify({'error': 'Invalid input'}), 400

    if len(comment) > 500:
        return jsonify({'error': 'Comment too long'}), 400

    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
    if recipe is None:
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404

    conn.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Comment added successfully'}), 201

@app.route('/recipes/<int:recipe_id>/ratings', methods=['POST'])
def add_rating(recipe_id):
    data = request.get_json()
    if not data or 'rating' not in data or not (1 <= data['rating'] <= 5):
        return jsonify({'error': 'Invalid input'}), 400

    conn = get_db_connection()
    recipe = conn.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,)).fetchone()
    if recipe is None:
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404

    conn.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, data['rating']))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Rating added successfully'}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)