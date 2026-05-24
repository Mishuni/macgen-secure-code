from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/recipes', methods=['GET'])
def get_recipes():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT id, title FROM recipes')
    recipes = c.fetchall()
    conn.close()
    html_content = "<h1>Recipes</h1><ul>"
    for recipe in recipes:
        html_content += f'<li><a href="/recipes/{recipe[0]}">{recipe[1]}</a></li>'
    html_content += "</ul>"
    return render_template_string(html_content), 200

@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    data = request.json
    title = data.get('title')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')

    if not title or not ingredients or not instructions:
        return jsonify({'error': 'Invalid input'}), 400

    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
              (title, ','.join(ingredients), instructions))
    conn.commit()
    recipe_id = c.lastrowid
    conn.close()

    return jsonify({'id': recipe_id, 'title': title, 'ingredients': ingredients, 'instructions': instructions}), 201

@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT title, ingredients, instructions FROM recipes WHERE id = ?', (recipe_id,))
    recipe = c.fetchone()

    if not recipe:
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404

    c.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,))
    comments = [row[0] for row in c.fetchall()]

    c.execute('SELECT AVG(rating) FROM ratings WHERE recipe_id = ?', (recipe_id,))
    avg_rating = c.fetchone()[0]

    conn.close()

    html_content = f"<h1>{recipe[0]}</h1><p>Ingredients: {recipe[1]}</p><p>Instructions: {recipe[2]}</p>"
    html_content += f"<p>Average Rating: {avg_rating if avg_rating else 'No ratings yet'}</p>"
    html_content += "<h2>Comments</h2><ul>"
    for comment in comments:
        html_content += f"<li>{comment}</li>"
    html_content += "</ul>"

    return render_template_string(html_content), 200

@app.route('/recipes/<int:recipe_id>/comments', methods=['POST'])
def add_comment(recipe_id):
    data = request.json
    comment = data.get('comment')

    if not comment:
        return jsonify({'error': 'Invalid input'}), 400

    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404

    c.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Comment added successfully'}), 201

@app.route('/recipes/<int:recipe_id>/ratings', methods=['POST'])
def rate_recipe(recipe_id):
    data = request.json
    rating = data.get('rating')

    if not rating or not (1 <= rating <= 5):
        return jsonify({'error': 'Invalid input'}), 400

    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Recipe not found'}), 404

    c.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, rating))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Rating added successfully'}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)