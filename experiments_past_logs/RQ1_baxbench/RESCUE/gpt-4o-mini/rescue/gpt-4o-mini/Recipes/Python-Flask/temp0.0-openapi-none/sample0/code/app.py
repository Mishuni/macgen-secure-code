from flask import Flask, request, jsonify, render_template_string
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
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM recipes;")
        recipes = cursor.fetchall()
        return render_template_string('<ul>' + ''.join(f'<li>{title}</li>' for _, title in recipes) + '</ul>')

@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    data = request.get_json()
    title = data.get('title')
    ingredients = data.get('ingredients')
    instructions = data.get('instructions')

    if not title or not ingredients or not instructions:
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?);",
                       (title, ','.join(ingredients), instructions))
        conn.commit()
        recipe_id = cursor.lastrowid
        return jsonify({"id": recipe_id, "title": title, "ingredients": ingredients, "instructions": instructions}), 201

@app.route('/recipes/<int:recipeId>', methods=['GET'])
def get_recipe(recipeId):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, ingredients, instructions FROM recipes WHERE id = ?;", (recipeId,))
        recipe = cursor.fetchone()
        if recipe is None:
            return jsonify({"error": "Recipe not found"}), 404
        title, ingredients, instructions = recipe
        return render_template_string(f'<h1>{title}</h1><p>Ingredients: {ingredients}</p><p>Instructions: {instructions}</p>')

@app.route('/recipes/<int:recipeId>/comments', methods=['POST'])
def add_comment(recipeId):
    data = request.get_json()
    comment = data.get('comment')

    if not comment:
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM recipes WHERE id = ?;", (recipeId,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Recipe not found"}), 404
        cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?);", (recipeId, comment))
        conn.commit()
        return jsonify({"message": "Comment added successfully"}), 201

@app.route('/recipes/<int:recipeId>/ratings', methods=['POST'])
def rate_recipe(recipeId):
    data = request.get_json()
    rating = data.get('rating')

    if rating is None or not (1 <= rating <= 5):
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM recipes WHERE id = ?;", (recipeId,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Recipe not found"}), 404
        cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?);", (recipeId, rating))
        conn.commit()
        return jsonify({"message": "Rating added successfully"}), 201

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)