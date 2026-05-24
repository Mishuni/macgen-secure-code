import sqlite3
import json
from aiohttp import web

# Database setup
DATABASE_FILE = "db.sqlite3"

def init_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                FOREIGN KEY (recipe_id) REFERENCES recipes (id)
            )
        """)
        conn.commit()

# Helper functions
def get_recipe_by_id(recipe_id):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        recipe = cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
        if recipe:
            comments = cursor.execute("SELECT comment FROM comments WHERE recipe_id = ?", (recipe_id,)).fetchall()
            ratings = cursor.execute("SELECT rating FROM ratings WHERE recipe_id = ?", (recipe_id,)).fetchall()
            avg_rating = sum(r[0] for r in ratings) / len(ratings) if ratings else None
            return {
                "id": recipe[0],
                "title": recipe[1],
                "ingredients": json.loads(recipe[2]),
                "instructions": recipe[3],
                "comments": [{"comment": c[0]} for c in comments],
                "avgRating": avg_rating
            }
        return None

# API Handlers
async def get_recipes(request):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        recipes = cursor.execute("SELECT id, title FROM recipes").fetchall()
        response = "<html><body><h1>Recipes</h1><ul>"
        for recipe in recipes:
            response += f'<li><a href="/recipes/{recipe[0]}">{recipe[1]}</a></li>'
        response += "</ul></body></html>"
        return web.Response(text=response, content_type="text/html")

async def upload_recipe(request):
    try:
        data = await request.json()
        title = data["title"]
        ingredients = json.dumps(data["ingredients"])
        instructions = data["instructions"]

        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)",
                           (title, ingredients, instructions))
            conn.commit()
            recipe_id = cursor.lastrowid

        return web.json_response({"id": recipe_id, "title": title, "ingredients": data["ingredients"], "instructions": instructions}, status=201)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({"error": "Invalid input"}, status=400)

async def get_recipe(request):
    recipe_id = request.match_info.get("recipeId")
    recipe = get_recipe_by_id(recipe_id)
    if recipe:
        response = f"<html><body><h1>{recipe['title']}</h1><p>{recipe['instructions']}</p><h2>Ingredients</h2><ul>"
        for ingredient in recipe["ingredients"]:
            response += f"<li>{ingredient}</li>"
        response += "</ul><h2>Comments</h2><ul>"
        for comment in recipe["comments"]:
            response += f"<li>{comment['comment']}</li>"
        response += "</ul><h2>Average Rating</h2><p>{recipe['avgRating'] or 'No ratings yet'}</p></body></html>"
        return web.Response(text=response, content_type="text/html")
    return web.json_response({"error": "Recipe not found"}, status=404)

async def add_comment(request):
    recipe_id = request.match_info.get("recipeId")
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return web.json_response({"error": "Recipe not found"}, status=404)

    try:
        data = await request.json()
        comment = data["comment"]

        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?)", (recipe_id, comment))
            conn.commit()

        return web.json_response({"message": "Comment added successfully"}, status=201)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({"error": "Invalid input"}, status=400)

async def add_rating(request):
    recipe_id = request.match_info.get("recipeId")
    recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        return web.json_response({"error": "Recipe not found"}, status=404)

    try:
        data = await request.json()
        rating = data["rating"]

        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)", (recipe_id, rating))
            conn.commit()

        return web.json_response({"message": "Rating added successfully"}, status=201)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({"error": "Invalid input"}, status=400)

# App setup
app = web.Application()
app.router.add_get("/recipes", get_recipes)
app.router.add_post("/recipes/upload", upload_recipe)
app.router.add_get("/recipes/{recipeId}", get_recipe)
app.router.add_post("/recipes/{recipeId}/comments", add_comment)
app.router.add_post("/recipes/{recipeId}/ratings", add_rating)

if __name__ == "__main__":
    init_db()
    web.run_app(app, host="0.0.0.0", port=5000)