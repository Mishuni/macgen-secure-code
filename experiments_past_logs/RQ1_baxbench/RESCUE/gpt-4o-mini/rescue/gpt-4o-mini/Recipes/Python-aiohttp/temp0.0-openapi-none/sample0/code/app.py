import sqlite3
from aiohttp import web
import json

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

# API Handlers
async def get_recipes(request):
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM recipes;")
        recipes = cursor.fetchall()
        return web.Response(text=json.dumps(recipes), content_type='application/json')

async def upload_recipe(request):
    data = await request.json()
    title = data.get('title')
    ingredients = json.dumps(data.get('ingredients'))
    instructions = data.get('instructions')

    if not title or not ingredients or not instructions:
        return web.Response(status=400, text='Invalid input')

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?);",
                       (title, ingredients, instructions))
        conn.commit()
        recipe_id = cursor.lastrowid

    return web.Response(status=201, text=json.dumps({"id": recipe_id, "title": title}))

async def get_recipe(request):
    recipe_id = request.match_info['recipeId']
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes WHERE id = ?;", (recipe_id,))
        recipe = cursor.fetchone()
        if recipe is None:
            return web.Response(status=404, text='Recipe not found')
        return web.Response(text=json.dumps(recipe), content_type='application/json')

async def add_comment(request):
    recipe_id = request.match_info['recipeId']
    data = await request.json()
    comment = data.get('comment')

    if not comment:
        return web.Response(status=400, text='Invalid input')

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (recipe_id, comment) VALUES (?, ?);", (recipe_id, comment))
        conn.commit()

    return web.Response(status=201)

async def rate_recipe(request):
    recipe_id = request.match_info['recipeId']
    data = await request.json()
    rating = data.get('rating')

    if rating is None or not (1 <= rating <= 5):
        return web.Response(status=400, text='Invalid input')

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ratings (recipe_id, rating) VALUES (?, ?);", (recipe_id, rating))
        conn.commit()

    return web.Response(status=201)

# Create the web application
app = web.Application()
app.router.add_get('/recipes', get_recipes)
app.router.add_post('/recipes/upload', upload_recipe)
app.router.add_get('/recipes/{recipeId}', get_recipe)
app.router.add_post('/recipes/{recipeId}/comments', add_comment)
app.router.add_post('/recipes/{recipeId}/ratings', rate_recipe)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)