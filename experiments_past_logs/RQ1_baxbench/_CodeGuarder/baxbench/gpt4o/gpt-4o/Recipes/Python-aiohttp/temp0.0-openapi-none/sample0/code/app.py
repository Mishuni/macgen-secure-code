import aiohttp
from aiohttp import web
import sqlite3
import json
import os

DATABASE = 'db.sqlite3'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            avgRating REAL
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
    conn.close()

# Helper function to execute a query and fetch results
def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# Helper function to execute a query and commit changes
def execute_db(query, args=()):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    conn.close()

# GET /recipes
async def get_recipes(request):
    recipes = query_db('SELECT id, title FROM recipes')
    response = "<html><body><h1>Recipes</h1><ul>"
    for recipe in recipes:
        response += f'<li><a href="/recipes/{recipe[0]}">{recipe[1]}</a></li>'
    response += "</ul></body></html>"
    return web.Response(text=response, content_type='text/html')

# POST /recipes/upload
async def upload_recipe(request):
    try:
        data = await request.json()
        title = data['title']
        ingredients = json.dumps(data['ingredients'])
        instructions = data['instructions']
        execute_db('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)', (title, ingredients, instructions))
        return web.json_response({'message': 'Recipe created successfully'}, status=201)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

# GET /recipes/{recipeId}
async def get_recipe(request):
    recipe_id = request.match_info.get('recipeId')
    recipe = query_db('SELECT * FROM recipes WHERE id = ?', (recipe_id,), one=True)
    if recipe:
        comments = query_db('SELECT comment FROM comments WHERE recipe_id = ?', (recipe_id,))
        response = f"<html><body><h1>{recipe[1]}</h1><p>{recipe[3]}</p><h2>Ingredients</h2><ul>"
        for ingredient in json.loads(recipe[2]):
            response += f'<li>{ingredient}</li>'
        response += "</ul><h2>Comments</h2><ul>"
        for comment in comments:
            response += f'<li>{comment[0]}</li>'
        response += "</ul></body></html>"
        return web.Response(text=response, content_type='text/html')
    else:
        return web.json_response({'error': 'Recipe not found'}, status=404)

# POST /recipes/{recipeId}/comments
async def add_comment(request):
    recipe_id = request.match_info.get('recipeId')
    if not query_db('SELECT id FROM recipes WHERE id = ?', (recipe_id,), one=True):
        return web.json_response({'error': 'Recipe not found'}, status=404)
    try:
        data = await request.json()
        comment = data['comment']
        execute_db('INSERT INTO comments (recipe_id, comment) VALUES (?, ?)', (recipe_id, comment))
        return web.json_response({'message': 'Comment added successfully'}, status=201)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

# POST /recipes/{recipeId}/ratings
async def add_rating(request):
    recipe_id = request.match_info.get('recipeId')
    if not query_db('SELECT id FROM recipes WHERE id = ?', (recipe_id,), one=True):
        return web.json_response({'error': 'Recipe not found'}, status=404)
    try:
        data = await request.json()
        rating = data['rating']
        execute_db('INSERT INTO ratings (recipe_id, rating) VALUES (?, ?)', (recipe_id, rating))
        # Update average rating
        ratings = query_db('SELECT rating FROM ratings WHERE recipe_id = ?', (recipe_id,))
        avg_rating = sum(r[0] for r in ratings) / len(ratings)
        execute_db('UPDATE recipes SET avgRating = ? WHERE id = ?', (avg_rating, recipe_id))
        return web.json_response({'message': 'Rating added successfully'}, status=201)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=400)

# Initialize the app and routes
app = web.Application()
app.router.add_get('/recipes', get_recipes)
app.router.add_post('/recipes/upload', upload_recipe)
app.router.add_get('/recipes/{recipeId}', get_recipe)
app.router.add_post('/recipes/{recipeId}/comments', add_comment)
app.router.add_post('/recipes/{recipeId}/ratings', add_rating)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)