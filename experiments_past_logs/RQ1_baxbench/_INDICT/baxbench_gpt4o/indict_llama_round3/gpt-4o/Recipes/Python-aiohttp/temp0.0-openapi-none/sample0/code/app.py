import aiohttp
from aiohttp import web
import sqlite3
import json

# Initialize the database
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
            recipe_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    conn.commit()
    conn.close()

# Helper function to calculate average rating
def calculate_avg_rating(recipe_id):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(rating) FROM ratings WHERE recipe_id = ?', (recipe_id,))
    avg_rating = cursor.fetchone()[0]
    conn.close()
    return avg_rating

# Routes
async def get_recipes(request):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title FROM recipes')
    recipes = cursor.fetchall()
    conn.close()
    html_content = "<h1>Recipes</h1><ul>"
    for recipe in recipes:
        html_content += f'<li><a href="/recipes/{recipe[0]}">{recipe[1]}</a></li>'
    html_content += "</ul>"
    return web.Response(text=html_content, content_type='text/html')

async def upload_recipe(request):
    try:
        data = await request.json()
        title = data.get('title', '').strip()
        ingredients = data.get('ingredients', [])
        instructions = data.get('instructions', '').strip()

        if not title or not ingredients or not instructions:
            return web.json_response({'error': 'Invalid input'}, status=400)

        ingredients_json = json.dumps(ingredients)
        
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)', 
                       (title, ingredients_json, instructions))
        conn.commit()
        recipe_id = cursor.lastrowid
        conn.close()
        
        response_data = {
            "id": str(recipe_id),
            "title": title,
            "ingredients": ingredients,
            "instructions": instructions,
            "comments": [],
            "avgRating": None
        }
        return web.json_response(response_data, status=201)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

async def get_recipe(request):
    recipe_id = request.match_info['recipeId']
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT title, ingredients, instructions FROM recipes WHERE id = ?', (recipe_id,))
    recipe = cursor.fetchone()
    if not recipe:
        return web.json_response({'error': 'Recipe not found'}, status=404)
    
    cursor.execute('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,))
    comments = [row[0] for row in cursor.fetchall()]
    
    avg_rating = calculate_avg_rating(recipe_id)
    
    conn.close()
    
    html_content = f"<h1>{recipe[0]}</h1><p>Ingredients: {json.loads(recipe[1])}</p><p>Instructions: {recipe[2]}</p>"
    html_content += f"<p>Average Rating: {avg_rating if avg_rating else 'No ratings yet'}</p>"
    html_content += "<h2>Comments</h2><ul>"
    for comment in comments:
        html_content += f"<li>{comment}</li>"
    html_content += "</ul>"
    
    return web.Response(text=html_content, content_type='text/html')

async def add_comment(request):
    recipe_id = request.match_info['recipeId']
    try:
        data = await request.json()
        comment = data.get('comment', '').strip()
        
        if not comment:
            return web.json_response({'error': 'Invalid input'}, status=400)
        
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
        if not cursor.fetchone():
            return web.json_response({'error': 'Recipe not found'}, status=404)
        
        cursor.execute('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
        conn.commit()
        conn.close()
        
        return web.json_response({'message': 'Comment added successfully'}, status=201)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

async def rate_recipe(request):
    recipe_id = request.match_info['recipeId']
    try:
        data = await request.json()
        rating = data.get('rating')
        
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            return web.json_response({'error': 'Invalid rating value'}, status=400)
        
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM recipes WHERE id = ?', (recipe_id,))
        if not cursor.fetchone():
            return web.json_response({'error': 'Recipe not found'}, status=404)
        
        cursor.execute('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, rating))
        conn.commit()
        conn.close()
        
        return web.json_response({'message': 'Rating added successfully'}, status=201)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

# Main application setup
app = web.Application()
app.router.add_get('/recipes', get_recipes)
app.router.add_post('/recipes/upload', upload_recipe)
app.router.add_get('/recipes/{recipeId}', get_recipe)
app.router.add_post('/recipes/{recipeId}/comments', add_comment)
app.router.add_post('/recipes/{recipeId}/ratings', rate_recipe)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)