from flask import Flask, request, jsonify, render_template_string
import sqlite3

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/recipes', methods=['GET'])
def get_recipes():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM recipes")
        recipes = cursor.fetchall()
        recipe_overview = "<h1>Recipe Overview</h1><ul>"
        for recipe in recipes:
            recipe_overview += f"<li><a href='/recipes/{recipe['id']}'>{recipe['title']}</a></li>"
        recipe_overview += "</ul>"
        return render_template_string(recipe_overview), 200
    except Exception:
        return "An error occurred. Please try again later.", 500
    finally:
        conn.close()

@app.route('/recipes/upload', methods=['POST'])
def upload_recipe():
    data = request.get_json()
    if not data or 'title' not in data or 'ingredients' not in data or 'instructions' not in data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
                       (data['title'], ','.join(data['ingredients']), data['instructions']))
        conn.commit()
        recipe_id = cursor.lastrowid
        return jsonify({"id": recipe_id, "title": data['title'], "ingredients": data['ingredients'], "instructions": data['instructions'], "comments": [], "avgRating": None}), 201
    except Exception:
        return "An error occurred. Please try again later.", 400
    finally:
        conn.close()

@app.route('/recipes/<recipeId>', methods=['GET'])
def get_recipe(recipeId):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipeId,))
        recipe = cursor.fetchone()
        if recipe is None:
            return jsonify({"error": "Recipe not found"}), 404

        comments = get_comments(recipeId)
        avg_rating = get_avg_rating(recipeId)
        return render_template_string(f"<h1>{recipe['title']}</h1><p>{recipe['instructions']}</p><h2>Ingredients</h2><p>{recipe['ingredients']}</p><h2>Comments</h2><ul>{''.join(f'<li>{c}</li>' for c in comments)}</ul><h2>Average Rating</h2><p>{avg_rating}</p>"), 200
    except Exception:
        return "An error occurred. Please try again later.", 500
    finally:
        conn.close()

@app.route('/recipes/<recipeId>/comments', methods=['POST'])
def add_comment(recipeId):
    data = request.get_json()
    if not data or 'comment' not in data:
        return jsonify({"error": "Invalid input"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (recipeId, data['comment']))
        conn.commit()
        return jsonify({"message": "Comment added successfully"}), 201
    except Exception:
        return "An error occurred. Please try again later.", 404
    finally:
        conn.close()

@app.route('/recipes/<recipeId>/ratings', methods=['POST'])
def rate_recipe(recipeId):
    data = request.get_json()
    if not data or 'rating' not in data or not (1 <= data['rating'] <= 5):
        return jsonify({"error": "Invalid input"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (recipeId, data['rating']))
        conn.commit()
        return jsonify({"message": "Rating added successfully"}), 201
    except Exception:
        return "An error occurred. Please try again later.", 404
    finally:
        conn.close()

def get_comments(recipeId):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipeId,))
    return [row['comment'] for row in cursor.fetchall()]

def get_avg_rating(recipeId):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(rating) as avg FROM ratings WHERE recipe_id = ?", (recipeId,))
    avg = cursor.fetchone()['avg']
    return avg if avg is not None else 0

if __name__ == '__main__':
    with get_db() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS recipes (id INTEGER PRIMARY KEY, title TEXT, ingredients TEXT, instructions TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, recipe_id INTEGER, comment TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS ratings (id INTEGER PRIMARY KEY, recipe_id INTEGER, rating INTEGER)''')
    app.run(host='0.0.0.0', port=5000)