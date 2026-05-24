import aiohttp
from aiohttp import web
import sqlite3
import json
import re

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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
    conn.close()

# Validate recipe ID
def validate_recipe_id(recipe_id):
    if not recipe_id.isdigit():
        return False
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM recipes WHERE id = ?', (recipe_id,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists

# Sanitize user input to prevent XSS
def sanitize_input(input_string):
    return re.sub(r'<[^>]+>', '', input_string)

# Get overview of recipes
async def get_recipes(request):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM recipes ORDER BY id DESC')
    recipes = cursor.fetchall()
    conn.close()
    
    html = '<h1>Recipe Overview</h1><ul>'
    for recipe in recipes:
        html += f'<li><a href="/recipes/{recipe[0]}">{sanitize_input(recipe[1])}</a></li>'
    html += '</ul>'
    
    return web.Response(text=html, content_type='text/html')

# Upload a new recipe
async def upload_recipe(request):
    data = await request.json()
    title = data.get('title')
    ingredients = json.dumps(data.get('ingredients'))
    instructions = data.get('instructions')

    if not title or not ingredients or not instructions:
        return web.Response(status=400, text='Invalid input')

    title = sanitize_input(title)
    instructions = sanitize_input(instructions)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)', 
                   (title, ingredients, instructions))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()

    return web.json_response({'id': recipe_id, 'title': title, 'ingredients': data.get('ingredients'), 'instructions': instructions})

# Get a recipe by ID
async def get_recipe(request):
    recipe_id = request.match_info['recipeId']
    
    if not validate_recipe_id(recipe_id):
        return web.Response(status=400, text='Invalid recipe ID')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?', (recipe_id,))
    recipe = cursor.fetchone()
    conn.close()

    if recipe is None:
        return web.Response(status=404, text='Recipe not found')

    ingredients = json.loads(recipe[2])
    html = f'<h1>{sanitize_input(recipe[1])}</h1><p>Ingredients: {", ".join(ingredients)}</p><p>Instructions: {sanitize_input(recipe[3])}</p>'
    return web.Response(text=html, content_type='text/html')

# Add a comment to a recipe
async def add_comment(request):
    recipe_id = request.match_info['recipeId']
    
    if not validate_recipe_id(recipe_id):
        return web.Response(status=400, text='Invalid recipe ID')

    data = await request.json()
    comment = data.get('comment')

    if not comment:
        return web.Response(status=400, text='Invalid input')

    comment = sanitize_input(comment)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
    conn.commit()
    conn.close()

    return web.Response(status=201)

# Rate a recipe
async def rate_recipe(request):
    recipe_id = request.match_info['recipeId']
    
    if not validate_recipe_id(recipe_id):
        return web.Response(status=400, text='Invalid recipe ID')

    data = await request.json()
    rating = data.get('rating')

    if rating is None or not (1 <= rating <= 5):
        return web.Response(status=400, text='Invalid input')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, rating))
    conn.commit()
    conn.close()

    return web.Response(status=201)

# Create the app and routes
app = web.Application()
app.router.add_get('/recipes', get_recipes)
app.router.add_post('/recipes/upload', upload_recipe)
app.router.add_get('/recipes/{recipeId}', get_recipe)
app.router.add_post('/recipes/{recipeId}/comments', add_comment)
app.router.add_post('/recipes/{recipeId}/ratings', rate_recipe)

# Initialize the database and run the app
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)