from flask import Flask, request, jsonify, render_template_string
import sqlite3
import html

app = Flask(__name__)

# Initialize the SQLite database
def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
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
                recipe_id INTEGER,
                comment TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        ''')
        conn.commit()

@app.route('/recipes', methods=['GET'])
def get_recipes():
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title FROM recipes')
        recipes = cursor.fetchall()
        html_content = '<h1>Recipe Overview</h1><ul>'
        for recipe in recipes:
            html_content += f'<li><a href="/recipes/{recipe[0]}">{html.escape(recipe[1])}</a></li>'
        html_content += '</ul>'
    return render_template_string(html_content)

@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    data = request.get_json()
    title = data.get('title')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')

    if not title or not ingredients or not instructions:
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
                       (title, ','.join(ingredients), instructions))
        conn.commit()
        recipe_id = cursor.lastrowid

    return jsonify({"id": recipe_id, "title": title, "ingredients": ingredients, "instructions": instructions}), 201

@app.route('/recipes/<int:recipeId>', methods=['GET'])
def get_recipe(recipeId):
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title, ingredients, instructions FROM recipes WHERE id = ?', (recipeId,))
        recipe = cursor.fetchone()
        if recipe is None:
            return jsonify({"error": "Recipe not found"}), 404

        cursor.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipeId,))
        comments = cursor.fetchall()
        cursor.execute('SELECT AVG(rating) FROM ratings WHERE recipe_id = ?', (recipeId,))
        avg_rating = cursor.fetchone()[0]

        html_content = f'<h1>{html.escape(recipe[0])}</h1><p>Ingredients: {html.escape(recipe[1])}</p><p>Instructions: {html.escape(recipe[2])}</p>'
        html_content += '<h2>Comments</h2><ul>'
        for comment in comments:
            html_content += f'<li>{html.escape(comment[0])}</li>'
        html_content += '</ul>'
        html_content += f'<h2>Average Rating: {avg_rating if avg_rating is not None else "No ratings yet"}</h2>'
    return render_template_string(html_content)

@app.route('/recipes/<int:recipeId>/comments', methods=['POST'])
def add_comment(recipeId):
    data = request.get_json()
    comment = data.get('comment')

    if not comment:
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipeId,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Recipe not found"}), 404

        cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipeId, comment))
        conn.commit()

    return jsonify({"message": "Comment added successfully"}), 201

@app.route('/recipes/<int:recipeId>/ratings', methods=['POST'])
def rate_recipe(recipeId):
    data = request.get_json()
    rating = data.get('rating')

    if rating is None or not (1 <= rating <= 5):
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipeId,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Recipe not found"}), 404

        cursor.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipeId, rating))
        conn.commit()

    return jsonify({"message": "Rating added successfully"}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)