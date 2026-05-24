from flask import Flask, request, jsonify, render_template_string, abort
import sqlite3

app = Flask(__name__)
DATABASE = 'db.sqlite3'

# Initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
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

# Helper function to query the database
def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rv = cursor.fetchall()
        conn.commit()
        return (rv[0] if rv else None) if one else rv

# Route: Get an overview of recipes
@app.route('/recipes', methods=['GET'])
def get_recipes():
    try:
        recipes = query_db('SELECT id, title FROM recipes')
        html = '<h1>Recipes</h1><ul>'
        for recipe in recipes:
            html += f'<li><a href="/recipes/{recipe[0]}">{recipe[1]}</a></li>'
        html += '</ul>'
        return html, 200
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

# Route: Upload a new recipe
@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    try:
        data = request.get_json()
        title = data.get('title')
        ingredients = data.get('ingredients')
        instructions = data.get('instructions')

        if not title or not ingredients or not instructions:
            return jsonify({'error': 'Invalid input'}), 400

        ingredients_str = ', '.join(ingredients)
        query_db('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
                 (title, ingredients_str, instructions))
        return jsonify({'message': 'Recipe created successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400

# Route: Get a recipe by ID
@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    try:
        recipe = query_db('SELECT * FROM recipes WHERE id = ?', (recipe_id,), one=True)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        comments = query_db('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,))
        ratings = query_db('SELECT rating FROM ratings WHERE recipe_id = ?', (recipe_id,))
        avg_rating = sum(r[0] for r in ratings) / len(ratings) if ratings else None

        html = f'''
        <h1>{recipe[1]}</h1>
        <p><strong>Ingredients:</strong> {recipe[2]}</p>
        <p><strong>Instructions:</strong> {recipe[3]}</p>
        <p><strong>Average Rating:</strong> {avg_rating if avg_rating else "No ratings yet"}</p>
        <h2>Comments</h2>
        <ul>
        '''
        for comment in comments:
            html += f'<li>{comment[0]}</li>'
        html += '</ul>'
        return html, 200
    except Exception as e:
        return jsonify({'error': 'Server error'}), 500

# Route: Add a comment to a recipe
@app.route('/recipes/<int:recipe_id>/comments', methods=['POST'])
def add_comment(recipe_id):
    try:
        data = request.get_json()
        comment = data.get('comment')

        if not comment:
            return jsonify({'error': 'Invalid input'}), 400

        recipe = query_db('SELECT id FROM recipes WHERE id = ?', (recipe_id,), one=True)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        query_db('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
        return jsonify({'message': 'Comment added successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400

# Route: Rate a recipe
@app.route('/recipes/<int:recipe_id>/ratings', methods=['POST'])
def rate_recipe(recipe_id):
    try:
        data = request.get_json()
        rating = data.get('rating')

        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Invalid input'}), 400

        recipe = query_db('SELECT id FROM recipes WHERE id = ?', (recipe_id,), one=True)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        query_db('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, rating))
        return jsonify({'message': 'Rating added successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)