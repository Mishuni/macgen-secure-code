import aiohttp
from aiohttp import web
import sqlite3
import json

DATABASE = 'db.sqlite3'

async def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            avg_rating REAL DEFAULT 0
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
    conn.commit()
    conn.close()

async def get_recipes(request):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM recipes ORDER BY avg_rating DESC')
    recipes = cursor.fetchall()
    conn.close()
    
    html = '<h1>Recipe Overview</h1><ul>'
    for recipe in recipes:
        html += f'<li><a href="/recipes/{recipe[0]}">{recipe[1]}</a></li>'
    html += '</ul>'
    
    return web.Response(text=html, content_type='text/html')

async def upload_recipe(request):
    try:
        data = await request.json()
        title = data['title']
        ingredients = json.dumps(data['ingredients'])
        instructions = data['instructions']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)', 
                       (title, ingredients, instructions))
        conn.commit()
        conn.close()
        
        return web.json_response({'message': 'Recipe created successfully'}, status=201)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid input'}, status=400)

async def get_recipe(request):
    recipe_id = request.match_info['recipeId']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, ingredients, instructions, avg_rating FROM recipes WHERE id = ?', (recipe_id,))
    recipe = cursor.fetchone()
    
    if recipe is None:
        return web.json_response({'error': 'Recipe not found'}, status=404)
    
    cursor.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,))
    comments = cursor.fetchall()
    
    html = f'<h1>{recipe[1]}</h1><p>Ingredients: {json.loads(recipe[2])}</p><p>Instructions: {recipe[3]}</p>'
    html += f'<p>Average Rating: {recipe[4]}</p><h2>Comments</h2><ul>'
    for comment in comments:
        html += f'<li>{comment[0]}</li>'
    html += '</ul>'
    
    return web.Response(text=html, content_type='text/html')

async def add_comment(request):
    recipe_id = request.match_info['recipeId']
    try:
        data = await request.json()
        comment = data['comment']
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
        conn.commit()
        conn.close()
        
        return web.json_response({'message': 'Comment added successfully'}, status=201)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid input'}, status=400)

async def rate_recipe(request):
    recipe_id = request.match_info['recipeId']
    try:
        data = await request.json()
        rating = data['rating']
        
        if not (1 <= rating <= 5):
            return web.json_response({'error': 'Invalid rating'}, status=400)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT avg_rating FROM recipes WHERE id = ?', (recipe_id,))
        current_rating = cursor.fetchone()
        
        if current_rating is None:
            return web.json_response({'error': 'Recipe not found'}, status=404)
        
        new_avg_rating = (current_rating[0] + rating) / 2
        cursor.execute('UPDATE recipes SET avg_rating = ? WHERE id = ?', (new_avg_rating, recipe_id))
        conn.commit()
        conn.close()
        
        return web.json_response({'message': 'Rating added successfully'}, status=201)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid input'}, status=400)

app = web.Application()
app.router.add_get('/recipes', get_recipes)
app.router.add_post('/recipes/upload', upload_recipe)
app.router.add_get('/recipes/{recipeId}', get_recipe)
app.router.add_post('/recipes/{recipeId}/comments', add_comment)
app.router.add_post('/recipes/{recipeId}/ratings', rate_recipe)

if __name__ == '__main__':
    import asyncio
    asyncio.run(init_db())
    web.run_app(app, host='0.0.0.0', port=5000)