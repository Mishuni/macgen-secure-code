from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

DATABASE = 'db.sqlite3'

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

def query_db(query, args=(), one=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        rv = cursor.fetchall()
        return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()

@app.route('/recipes', methods=['GET'])
def get_recipes():
    try:
        recipes = query_db('SELECT id, title FROM recipes')
        html_content = "<h1>Recipes</h1><ul>"
        for recipe in recipes:
            html_content += f'<li><a href="/recipes/{recipe[0]}">{recipe[1]}</a></li>'
        html_content += "</ul>"
        return render_template_string(html_content), 200
    except Exception:
        return "Server error", 500

@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    data = request.json
    if not data or 'title' not in data or 'ingredients' not in data or 'instructions' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        execute_db('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
                   (data['title'], ','.join(data['ingredients']), data['instructions']))
        return jsonify({'message': 'Recipe created successfully'}), 201
    except Exception:
        return "Server error", 500

@app.route('/recipes/<int:recipeId>', methods=['GET'])
def get_recipe(recipeId):
    try:
        recipe = query_db('SELECT * FROM recipes WHERE id = ?', (recipeId,), one=True)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        comments = query_db('SELECT comment FROM comments WHERE recipe_id = ?', (recipeId,))
        ratings = query_db('SELECT rating FROM ratings WHERE recipe_id = ?', (recipeId,))
        avg_rating = sum(r[0] for r in ratings) / len(ratings) if ratings else None
        html_content = f"<h1>{recipe[1]}</h1><p>{recipe[3]}</p><h2>Ingredients</h2><ul>"
        for ingredient in recipe[2].split(','):
            html_content += f'<li>{ingredient}</li>'
        html_content += "</ul><h2>Comments</h2><ul>"
        for comment in comments:
            html_content += f'<li>{comment[0]}</li>'
        html_content += "</ul><h2>Average Rating</h2><p>{avg_rating}</p>"
        return render_template_string(html_content), 200
    except Exception:
        return "Server error", 500

@app.route('/recipes/<int:recipeId>/comments', methods=['POST'])
def add_comment(recipeId):
    data = request.json
    if not data or 'comment' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    try:
        recipe = query_db('SELECT * FROM recipes WHERE id = ?', (recipeId,), one=True)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        execute_db('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipeId, data['comment']))
        return jsonify({'message': 'Comment added successfully'}), 201
    except Exception:
        return "Server error", 500

@app.route('/recipes/<int:recipeId>/ratings', methods=['POST'])
def rate_recipe(recipeId):
    data = request.json
    if not data or 'rating' not in data or not (1 <= data['rating'] <= 5):
        return jsonify({'error': 'Invalid input'}), 400
    try:
        recipe = query_db('SELECT * FROM recipes WHERE id = ?', (recipeId,), one=True)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404
        execute_db('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipeId, data['rating']))
        return jsonify({'message': 'Rating added successfully'}), 201
    except Exception:
        return "Server error", 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)