import aiohttp
from aiohttp import web
import sqlite3
import json
import unicodedata

DB_NAME = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
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

# Sanitize input to prevent XSS
def sanitize_input(input_string):
    return unicodedata.normalize('NFC', input_string).replace('<', '&lt;').replace('>', '&gt;')

# Get overview of recipes
async def get_recipes(request):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title FROM recipes ORDER BY id DESC')
        recipes = cursor.fetchall()
    
    html = '<h1>Recipe Overview</h1><ul>'
    for recipe in recipes:
        html += f'<li><a href="/recipes/{recipe[0]}">{sanitize_input(recipe[1])}</a></li>'
    html += '</ul>'
    
    return web.Response(text=html, content_type='text/html')

# Upload a new recipe
async def upload_recipe(request):
    data = await request.json()
    title = sanitize_input(data.get('title', ''))
    ingredients = data.get('ingredients', [])
    instructions = sanitize_input(data.get('instructions', ''))
    
    if not title or not ingredients or not instructions:
        return web.Response(status=400, text='Invalid input')
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)', 
                       (title, json.dumps(ingredients), instructions))
        conn.commit()
        recipe_id = cursor.lastrowid
    
    return web.json_response({'id': recipe_id, 'title': title, 'ingredients': ingredients, 'instructions': instructions})

# Get a specific recipe
async def get_recipe(request):
    recipe_id = request.match_info['recipeId']
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, ingredients, instructions FROM recipes WHERE id = ?', (recipe_id,))
        recipe = cursor.fetchone()
        
        if recipe is None:
            return web.Response(status=404, text='Recipe not found')
        
        cursor.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,))
        comments = cursor.fetchall()
        
        cursor.execute('SELECT AVG(rating) FROM ratings WHERE recipe_id = ?', (recipe_id,))
        avg_rating = cursor.fetchone()[0]
    
    html = f'<h1>{sanitize_input(recipe[1])}</h1><p>Ingredients: {json.loads(recipe[2])}</p><p>Instructions: {sanitize_input(recipe[3])}</p>'
    html += '<h2>Comments</h2><ul>'
    for comment in comments:
        html += f'<li>{sanitize_input(comment[0])}</li>'
    html += '</ul>'
    html += f'<h2>Average Rating: {avg_rating if avg_rating is not None else "No ratings yet"}</h2>'
    
    return web.Response(text=html, content_type='text/html')

# Add a comment to a recipe
async def add_comment(request):
    recipe_id = request.match_info['recipeId']
    data = await request.json()
    comment = sanitize_input(data.get('comment', ''))
    
    if not comment:
        return web.Response(status=400, text='Invalid input')
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
        conn.commit()
    
    return web.Response(status=201)

# Rate a recipe
async def rate_recipe(request):
    recipe_id = request.match_info['recipeId']
    data = await request.json()
    rating = data.get('rating')
    
    if rating is None or not (1 <= rating <= 5):
        return web.Response(status=400, text='Invalid input')
    
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, rating))
        conn.commit()
    
    return web.Response(status=201)

# Set up the application and routes
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