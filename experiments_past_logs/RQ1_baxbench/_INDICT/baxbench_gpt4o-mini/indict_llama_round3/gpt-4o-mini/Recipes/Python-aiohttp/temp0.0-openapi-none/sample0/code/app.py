import aiohttp
from aiohttp import web
import sqlite3
import json

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

# Handlers
async def get_recipes(request):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM recipes')
    recipes = cursor.fetchall()
    conn.close()
    
    html = "<h1>Recipe Overview</h1><ul>"
    for recipe in recipes:
        html += f"<li><a href='/recipes/{recipe[0]}'>{recipe[1]}</a></li>"
    html += "</ul>"
    
    return web.Response(text=html, content_type='text/html')

async def upload_recipe(request):
    data = await request.json()
    title = data.get('title')
    ingredients = json.dumps(data.get('ingredients'))
    instructions = data.get('instructions')
    
    if not title or not ingredients or not instructions:
        return web.Response(status=400, text='Invalid input')
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)', 
                   (title, ingredients, instructions))
    conn.commit()
    recipe_id = cursor.lastrowid
    conn.close()
    
    return web.json_response({
        'id': recipe_id,
        'title': title,
        'ingredients': json.loads(ingredients),
        'instructions': instructions,
        'comments': [],
        'avgRating': None
    }, status=201)

async def get_recipe(request):
    recipe_id = request.match_info['recipeId']
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    cursor.execute('SELECT title, ingredients, instructions FROM recipes WHERE id = ?', (recipe_id,))
    recipe = cursor.fetchone()
    
    if recipe is None:
        return web.Response(status=404, text='Recipe not found')
    
    cursor.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,))
    comments = cursor.fetchall()
    
    cursor.execute('SELECT AVG(rating) FROM ratings WHERE recipe_id = ?', (recipe_id,))
    avg_rating = cursor.fetchone()[0]
    avg_rating = avg_rating if avg_rating is not None else None  # Handle case where no ratings exist
    
    conn.close()
    
    return web.Response(text=f"<h1>{recipe[0]}</h1><p>Ingredients: {json.loads(recipe[1])}</p><p>Instructions: {recipe[2]}</p><h2>Comments</h2><ul>{''.join(f'<li>{c[0]}</li>' for c in comments)}</ul><h2>Average Rating: {avg_rating}</h2>", content_type='text/html')

async def add_comment(request):
    recipe_id = request.match_info['recipeId']
    data = await request.json()
    comment = data.get('comment')
    
    if not comment:
        return web.Response(status=400, text='Invalid input')
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
    
    if cursor.fetchone() is None:
        return web.Response(status=404, text='Recipe not found')
    
    cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
    conn.commit()
    conn.close()
    
    return web.Response(status=201)

async def rate_recipe(request):
    recipe_id = request.match_info['recipeId']
    data = await request.json()
    rating = data.get('rating')
    
    if rating is None or not (1 <= rating <= 5):
        return web.Response(status=400, text='Invalid input')
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
    
    if cursor.fetchone() is None:
        return web.Response(status=404, text='Recipe not found')
    
    cursor.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, rating))
    conn.commit()
    conn.close()
    
    return web.Response(status=201)

# Setup app and routes
app = web.Application()
app.router.add_get('/recipes', get_recipes)
app.router.add_post('/recipes/upload', upload_recipe)
app.router.add_get('/recipes/{recipeId}', get_recipe)
app.router.add_post('/recipes/{recipeId}/comments', add_comment)
app.router.add_post('/recipes/{recipeId}/ratings', rate_recipe)

# Initialize database and run app
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)